#!/usr/bin/env python
"""Backend architecture audit command.

Scans backend Python modules for structural smells that ordinary unit tests do
not catch: public helper sprawl, procedural bounded packages, provider boundary
leaks, raw dict contracts, dependency direction risks, migrated-shim behavior,
large modules, god-service candidates, and tests that keep legacy owners alive.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence


SMELL_TYPES = {
    "shimBehavior",
    "providerBoundaryLeak",
    "dependencyDirectionRisk",
    "proceduralBoundedPackage",
    "publicHelperSprawl",
    "rawDictContract",
    "godService",
    "largeModule",
    "testMirrorsBadArchitecture",
}

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}
TARGET_SHAPES = {
    "service",
    "policy",
    "component",
    "dto",
    "privateHelper",
    "compatibilityShim",
    "deleteAfterMigration",
    "allowlistedPublicFactory",
}

DRAFTING_BOUNDED_APP_PACKAGES = {
    "artifacts",
    "evidence",
    "planning",
    "generation",
    "validation",
    "revision",
    "final_quality",
    "hitl",
    "operations",
    "migration",
}

PROCEDURAL_PACKAGE_REPAIR_SLICES = {
    "backend/app/drafting/application/validation": "2.17.4.6.0.11",
    "backend/app/drafting/application/revision": "2.17.4.6.0.11",
    "backend/app/drafting/application/final_quality": "2.17.4.6.0.11",
    "backend/app/drafting/application/hitl": "2.17.4.6.0.10",
    "backend/app/drafting/application/operations": "2.17.4.6.0.10",
    "backend/app/shared/llm_operations": "2.17.4.6.0.10",
    "backend/app/application": "2.17.4.6.0.11",
    "backend/app/api": "2.17.4.6.0.11",
    "backend/app/infrastructure": "2.17.4.6.0.11",
}

RAW_PROVIDER_ALLOWED_PREFIXES = (
    "backend/app/infrastructure/openrouter_json_adapter.py",
    "backend/app/drafting/application/operations/json_step_adapter.py",
)

DOMAIN_FORBIDDEN_IMPORT_PREFIXES = (
    "fastapi",
    "httpx",
    "requests",
    "sqlite3",
    "celery",
    "backend.app.infrastructure",
)
API_FORBIDDEN_IMPORT_PREFIXES = (
    "backend.app.infrastructure.openrouter",
    "backend.app.infrastructure.sqlite",
    "backend.app.infrastructure.draft_run_tasks",
    "backend.app.infrastructure.celery_app",
)


@dataclass(frozen=True)
class Finding:
    findingKey: str
    smellType: str
    severity: str
    path: str
    package: str
    symbols: list[str] = field(default_factory=list)
    evidence: str = ""
    suggestedOwner: str = ""
    suggestedRepairSlice: str = ""

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ModuleFacts:
    path: str
    package: str
    source: str
    tree: ast.Module | None
    line_count: int
    public_functions: list[ast.FunctionDef | ast.AsyncFunctionDef]
    classes: list[ast.ClassDef]
    imports: list[str]


def normalize_path(path: Path) -> str:
    return path.as_posix()


def module_package(relative_path: str) -> str:
    parts = relative_path.split("/")
    if len(parts) <= 1:
        return relative_path
    if parts[:4] == ["backend", "app", "drafting", "application"] and len(parts) >= 5:
        return "/".join(parts[:5])
    if parts[:3] == ["backend", "app", "shared"] and len(parts) >= 4:
        return "/".join(parts[:4])
    if parts[:2] == ["backend", "app"] and len(parts) >= 3:
        return "/".join(parts[:3])
    if parts[:2] == ["backend", "tests"]:
        return "backend/tests"
    return "/".join(parts[:-1])


def is_public_function(node: ast.AST) -> bool:
    return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")


def annotation_text(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def collect_imports(tree: ast.Module | None) -> list[str]:
    imports: list[str] = []
    if tree is None:
        return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def iter_python_files(root: Path) -> Iterable[Path]:
    for base in [root / "backend" / "app", root / "backend" / "tests"]:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" not in path.parts:
                yield path


def parse_module(root: Path, path: Path) -> ModuleFacts:
    relative_path = normalize_path(path.relative_to(root))
    source = path.read_text(encoding="utf-8")
    try:
        tree: ast.Module | None = ast.parse(source, filename=relative_path)
    except SyntaxError:
        tree = None
    public_functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    classes: list[ast.ClassDef] = []
    if tree is not None:
        public_functions = [node for node in tree.body if is_public_function(node)]
        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    return ModuleFacts(
        path=relative_path,
        package=module_package(relative_path),
        source=source,
        tree=tree,
        line_count=len(source.splitlines()),
        public_functions=public_functions,
        classes=classes,
        imports=collect_imports(tree),
    )


def finding_key(smell_type: str, path_or_package: str, symbol: str | None = None) -> str:
    if symbol:
        return f"{smell_type}:{path_or_package}:{symbol}"
    return f"{smell_type}:{path_or_package}"


def repair_slice_for(package: str) -> str:
    for prefix, repair_slice in PROCEDURAL_PACKAGE_REPAIR_SLICES.items():
        if package.startswith(prefix):
            return repair_slice
    return "2.17.4.6.0.11"


def detect_shim_behavior(facts: ModuleFacts) -> list[Finding]:
    if not facts.path.startswith("backend/app/application/"):
        return []
    name = facts.path.rsplit("/", 1)[-1]
    if not (name.startswith("draft_") or name.startswith("deterministic_")):
        return []
    if "Compatibility shim" not in facts.source and "compatibility shim" not in facts.source:
        return []

    risky_markers = [
        marker
        for marker in ("def ", "class ", ".complete_json(", "fallbackUsed", "trace", "artifactPayload")
        if marker in facts.source
    ]
    if not risky_markers:
        return []
    symbols = [node.name for node in facts.public_functions] + [node.name for node in facts.classes]
    return [
        Finding(
            findingKey=finding_key("shimBehavior", facts.path),
            smellType="shimBehavior",
            severity="critical",
            path=facts.path,
            package=facts.package,
            symbols=symbols,
            evidence=f"Migrated shim contains behavior markers: {', '.join(sorted(set(risky_markers)))}.",
            suggestedOwner="backend.app.drafting canonical package",
            suggestedRepairSlice=repair_slice_for(facts.package),
        )
    ]


def detect_provider_boundary_leak(facts: ModuleFacts) -> list[Finding]:
    if facts.path.startswith("backend/tests/"):
        return []
    if ".complete_json(" not in facts.source:
        return []
    if any(facts.path == allowed for allowed in RAW_PROVIDER_ALLOWED_PREFIXES):
        return []
    severity = "critical" if facts.path.startswith("backend/app/drafting/") else "high"
    return [
        Finding(
            findingKey=finding_key("providerBoundaryLeak", facts.path),
            smellType="providerBoundaryLeak",
            severity=severity,
            path=facts.path,
            package=facts.package,
            evidence="Raw provider .complete_json( call outside the bounded JSON adapter allowlist.",
            suggestedOwner="backend.app.drafting.application.operations.json_step_adapter",
            suggestedRepairSlice=repair_slice_for(facts.package),
        )
    ]


def detect_dependency_direction_risk(facts: ModuleFacts) -> list[Finding]:
    forbidden_prefixes: tuple[str, ...] = ()
    if facts.path.startswith("backend/app/domain/"):
        forbidden_prefixes = DOMAIN_FORBIDDEN_IMPORT_PREFIXES
    elif facts.path.startswith("backend/app/api/"):
        forbidden_prefixes = API_FORBIDDEN_IMPORT_PREFIXES
    if not forbidden_prefixes:
        return []

    risky = [
        imported
        for imported in facts.imports
        for prefix in forbidden_prefixes
        if imported == prefix or imported.startswith(prefix + ".")
    ]
    if not risky:
        return []
    return [
        Finding(
            findingKey=finding_key("dependencyDirectionRisk", facts.path),
            smellType="dependencyDirectionRisk",
            severity="critical",
            path=facts.path,
            package=facts.package,
            symbols=sorted(set(risky)),
            evidence=f"Forbidden imports for this backend layer: {', '.join(sorted(set(risky)))}.",
            suggestedOwner=facts.package,
            suggestedRepairSlice="2.17.4.6.0.11",
        )
    ]


def detect_public_helper_sprawl(facts: ModuleFacts) -> list[Finding]:
    if not facts.path.startswith("backend/app/drafting/application/"):
        return []
    if facts.path.endswith("__init__.py"):
        return []
    if not facts.public_functions:
        return []
    severity = "high" if len(facts.public_functions) >= 3 else "medium"
    symbols = [node.name for node in facts.public_functions]
    return [
        Finding(
            findingKey=finding_key("publicHelperSprawl", facts.path),
            smellType="publicHelperSprawl",
            severity=severity,
            path=facts.path,
            package=facts.package,
            symbols=symbols,
            evidence=f"{len(symbols)} public top-level helper(s): {', '.join(symbols[:8])}.",
            suggestedOwner=facts.package,
            suggestedRepairSlice=repair_slice_for(facts.package),
        )
    ]


def detect_raw_dict_contract(facts: ModuleFacts) -> list[Finding]:
    if not (
        facts.path.startswith("backend/app/drafting/application/")
        or facts.path.startswith("backend/app/application/")
        or facts.path.startswith("backend/app/api/")
    ):
        return []
    symbols: list[str] = []
    for function in facts.public_functions:
        annotations = [annotation_text(function.returns)]
        annotations.extend(annotation_text(arg.annotation) for arg in function.args.args)
        annotations.extend(annotation_text(arg.annotation) for arg in function.args.kwonlyargs)
        joined = " ".join(annotations)
        if "dict[" in joined or "Dict[" in joined or "Mapping[" in joined or "dict[str, Any]" in joined:
            symbols.append(function.name)
    if not symbols:
        return []
    severity = "high" if facts.path.endswith("_service.py") or facts.path.endswith("_orchestrator.py") else "medium"
    return [
        Finding(
            findingKey=finding_key("rawDictContract", facts.path),
            smellType="rawDictContract",
            severity=severity,
            path=facts.path,
            package=facts.package,
            symbols=symbols,
            evidence=f"Public function annotations expose raw dict/Mapping contract: {', '.join(symbols[:8])}.",
            suggestedOwner=f"{facts.package} DTO/result contract",
            suggestedRepairSlice=repair_slice_for(facts.package),
        )
    ]


def detect_large_module(facts: ModuleFacts) -> list[Finding]:
    if facts.path.startswith("backend/tests/"):
        return []
    if facts.line_count < 220:
        return []
    severity = "high" if facts.line_count >= 300 else "medium"
    return [
        Finding(
            findingKey=finding_key("largeModule", facts.path),
            smellType="largeModule",
            severity=severity,
            path=facts.path,
            package=facts.package,
            symbols=[node.name for node in facts.classes[:5]],
            evidence=f"Module has {facts.line_count} lines.",
            suggestedOwner=facts.package,
            suggestedRepairSlice=repair_slice_for(facts.package),
        )
    ]


def detect_god_service(facts: ModuleFacts) -> list[Finding]:
    if facts.path.startswith("backend/tests/"):
        return []
    if not facts.classes or facts.line_count < 240:
        return []
    if _has_component_delegation(facts) and ".complete_json(" not in facts.source and not facts.public_functions:
        return []
    markers = [
        marker
        for marker in (".complete_json(", "parse_", "payload", "fallback", "trace", "repair", "incident")
        if marker in facts.source
    ]
    if len(markers) < 3:
        return []
    return [
        Finding(
            findingKey=finding_key("godService", facts.path),
            smellType="godService",
            severity="high",
            path=facts.path,
            package=facts.package,
            symbols=[node.name for node in facts.classes],
            evidence=f"Large class module mixes responsibility markers: {', '.join(markers)}.",
            suggestedOwner=f"{facts.package} service/policy/component split",
            suggestedRepairSlice=repair_slice_for(facts.package),
        )
    ]


def _has_component_delegation(facts: ModuleFacts) -> bool:
    delegated_roles = (
        "Parser(",
        "PromptBuilder(",
        "TraceBuilder(",
        "AttemptMapper(",
        "FailureMapper(",
        "ArtifactFactory(",
        "EvidenceEvaluator(",
        "ReportAppender(",
    )
    return sum(1 for role in delegated_roles if role in facts.source) >= 3


def detect_test_mirrors_bad_architecture(facts: ModuleFacts) -> list[Finding]:
    if not facts.path.startswith("backend/tests/"):
        return []
    risky = [
        imported
        for imported in facts.imports
        if imported.startswith("backend.app.application.draft_")
        or imported.startswith("backend.app.application.deterministic_")
    ]
    if not risky:
        return []
    return [
        Finding(
            findingKey=finding_key("testMirrorsBadArchitecture", facts.path),
            smellType="testMirrorsBadArchitecture",
            severity="medium",
            path=facts.path,
            package=facts.package,
            symbols=sorted(set(risky)),
            evidence=f"Test imports legacy DraftRun owners: {', '.join(sorted(set(risky))[:8])}.",
            suggestedOwner="canonical backend.app.drafting package imports",
            suggestedRepairSlice=repair_slice_for(facts.package),
        )
    ]


def detect_procedural_bounded_packages(module_facts: Sequence[ModuleFacts]) -> list[Finding]:
    by_package: dict[str, list[ModuleFacts]] = defaultdict(list)
    for facts in module_facts:
        by_package[facts.package].append(facts)

    findings: list[Finding] = []
    for package, modules in sorted(by_package.items()):
        if not (
            package.startswith("backend/app/drafting/application/")
            or package == "backend/app/application"
            or package == "backend/app/api"
            or package == "backend/app/infrastructure"
            or package == "backend/app/shared/llm_operations"
        ):
            continue
        public_function_count = sum(len(facts.public_functions) for facts in modules)
        procedural_names = [
            facts.path
            for facts in modules
            if any(token in facts.path for token in ("_prompts.py", "_parser.py", "_audit.py", "_payloads.py"))
            and facts.public_functions
            and not facts.classes
        ]
        large_count = sum(1 for facts in modules if facts.line_count >= 220)
        if public_function_count < 8 and len(procedural_names) < 3 and large_count < 2:
            continue
        severity = "high" if public_function_count >= 12 or len(procedural_names) >= 4 else "medium"
        findings.append(
            Finding(
                findingKey=finding_key("proceduralBoundedPackage", package),
                smellType="proceduralBoundedPackage",
                severity=severity,
                path=package,
                package=package,
                symbols=[],
                evidence=(
                    f"{len(modules)} modules, {public_function_count} public helper(s), "
                    f"{len(procedural_names)} procedural naming marker(s), {large_count} large module(s)."
                ),
                suggestedOwner=f"{package} service/policy/component owners",
                suggestedRepairSlice=repair_slice_for(package),
            )
        )
    return findings


def collect_findings(root: Path) -> list[Finding]:
    module_facts = [parse_module(root, path) for path in iter_python_files(root)]
    findings: list[Finding] = []
    for facts in module_facts:
        findings.extend(detect_shim_behavior(facts))
        findings.extend(detect_provider_boundary_leak(facts))
        findings.extend(detect_dependency_direction_risk(facts))
        findings.extend(detect_public_helper_sprawl(facts))
        findings.extend(detect_raw_dict_contract(facts))
        findings.extend(detect_large_module(facts))
        findings.extend(detect_god_service(facts))
        findings.extend(detect_test_mirrors_bad_architecture(facts))
    findings.extend(detect_procedural_bounded_packages(module_facts))
    return sorted(findings, key=lambda finding: (finding.severity, finding.smellType, finding.findingKey))


def load_ledger(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"version": 1, "entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def validate_ledger(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        return ["ledger entries must be a list"]
    seen_keys: set[str] = set()
    required = {
        "debtId",
        "findingKey",
        "package",
        "module",
        "smellType",
        "severity",
        "owner",
        "targetShape",
        "allowedUntilSlice",
        "repairSlice",
        "guardrail",
        "currentEvidence",
        "notes",
    }
    for index, entry in enumerate(entries):
        missing = sorted(key for key in required if not entry.get(key))
        if missing:
            errors.append(f"entry {index} missing required fields: {', '.join(missing)}")
        finding = entry.get("findingKey")
        if finding in seen_keys:
            errors.append(f"duplicate findingKey in ledger: {finding}")
        if finding:
            seen_keys.add(finding)
        if entry.get("smellType") not in SMELL_TYPES:
            errors.append(f"entry {index} has invalid smellType: {entry.get('smellType')}")
        if entry.get("severity") not in SEVERITY_ORDER:
            errors.append(f"entry {index} has invalid severity: {entry.get('severity')}")
        if entry.get("targetShape") not in TARGET_SHAPES:
            errors.append(f"entry {index} has invalid targetShape: {entry.get('targetShape')}")
    return errors


def ledger_finding_keys(ledger: dict[str, Any]) -> set[str]:
    return {entry["findingKey"] for entry in ledger.get("entries", []) if entry.get("findingKey")}


def build_report(root: Path, ledger_path: Path | None = None) -> dict[str, Any]:
    findings = collect_findings(root)
    ledger = load_ledger(ledger_path)
    ledger_errors = validate_ledger(ledger)
    ledger_keys = ledger_finding_keys(ledger)
    finding_keys = {finding.findingKey for finding in findings}
    ledgered = [finding for finding in findings if finding.findingKey in ledger_keys]
    unledgered = [finding for finding in findings if finding.findingKey not in ledger_keys]
    stale_keys = sorted(ledger_keys - finding_keys)

    severity_counts = Counter(finding.severity for finding in findings)
    smell_counts = Counter(finding.smellType for finding in findings)
    package_counts = Counter(finding.package for finding in findings)

    module_files = list(iter_python_files(root))
    report = {
        "summary": {
            "filesScanned": len(module_files),
            "findings": len(findings),
            "ledgeredFindings": len(ledgered),
            "unledgeredFindings": len(unledgered),
            "staleLedgerKeys": len(stale_keys),
            "bySeverity": dict(sorted(severity_counts.items())),
            "bySmellType": dict(sorted(smell_counts.items())),
            "topPackages": dict(package_counts.most_common(12)),
            "ledgerErrors": ledger_errors,
        },
        "findings": [finding.to_payload() for finding in findings],
        "ledgeredFindings": [finding.to_payload() for finding in ledgered],
        "unledgeredFindings": [finding.to_payload() for finding in unledgered],
        "ledgerCoverage": {
            "ledgeredFindingKeys": sorted(finding.findingKey for finding in ledgered),
            "unledgeredFindingKeys": sorted(finding.findingKey for finding in unledgered),
            "staleLedgerKeys": stale_keys,
        },
    }
    return report


def severity_at_or_above(severity: str, threshold: str) -> bool:
    return SEVERITY_ORDER[severity] >= SEVERITY_ORDER[threshold]


def blocking_unledgered(report: dict[str, Any], threshold: str) -> list[dict[str, Any]]:
    return [
        finding
        for finding in report["unledgeredFindings"]
        if severity_at_or_above(finding["severity"], threshold)
    ]


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Backend Architecture Audit",
        "",
        "Generated by `python scripts/backend-architecture-audit.py --format markdown`.",
        "",
        "## Summary",
        "",
        f"- Files scanned: {summary['filesScanned']}",
        f"- Findings: {summary['findings']}",
        f"- Ledgered findings: {summary['ledgeredFindings']}",
        f"- Unledgered findings: {summary['unledgeredFindings']}",
        f"- Stale ledger keys: {summary['staleLedgerKeys']}",
        "",
        "## Findings By Severity",
        "",
    ]
    for severity in ("critical", "high", "medium", "low"):
        lines.append(f"- {severity}: {summary['bySeverity'].get(severity, 0)}")
    lines.extend(["", "## Findings By Smell Type", ""])
    for smell_type, count in sorted(summary["bySmellType"].items()):
        lines.append(f"- {smell_type}: {count}")
    lines.extend(["", "## Top Packages", ""])
    for package, count in summary["topPackages"].items():
        lines.append(f"- `{package}`: {count}")

    high_findings = [
        finding
        for finding in report["findings"]
        if finding["severity"] in {"critical", "high"}
    ][:30]
    lines.extend(["", "## Top High-Severity Debt Clusters", ""])
    if not high_findings:
        lines.append("- None.")
    for finding in high_findings:
        lines.append(
            f"- `{finding['findingKey']}` ({finding['severity']}): "
            f"{finding['evidence']} Repair slice: `{finding['suggestedRepairSlice']}`."
        )

    lines.extend(
        [
            "",
            "## Completed Cleanup Slices",
            "",
            "- `2.17.4.6.0.8`: Drafting validation package OOP cleanup closed validation high findings; residual validation debt is medium line-count/package cleanup tracked in the ledger.",
            "- `2.17.4.6.0.9`: Drafting revision and final-quality OOP cleanup closed public helper sprawl in both packages; final-quality findings are closed, and residual revision debt is medium line-count/package cleanup tracked in the ledger.",
            "- `2.17.4.6.0.10`: Drafting HITL and provider operation surface cleanup closed HITL/service high debt, split drafting operation helper surfaces into class-owned modules, and split shared LLM operation contracts/inventory/results by role.",
            "",
            "## Next Repair Slices",
            "",
            "- `2.17.4.6.0.11`: Backend API/application/infrastructure/upstream surface cleanup.",
            "",
            "## Smoke Enforcement",
            "",
            "- `npm run test:architecture` runs this audit with the committed debt ledger.",
            "- Unledgered `critical` and `high` findings fail architecture smoke.",
            "- Existing migrated-shim, ownership-header, provider-boundary, and documentation guardrails still run.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit backend architecture debt.")
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format.",
    )
    parser.add_argument("--ledger", help="Optional debt ledger JSON path.")
    parser.add_argument(
        "--fail-on-unledgered",
        choices=("critical", "high", "medium", "low"),
        help="Exit nonzero when unledgered findings at or above this severity exist.",
    )
    parser.add_argument("--output", help="Optional output file path.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    ledger_path = (root / args.ledger).resolve() if args.ledger else None
    report = build_report(root, ledger_path)
    if args.format == "json":
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    else:
        rendered = render_markdown(report)

    if args.output:
        output_path = (root / args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    if report["summary"]["ledgerErrors"]:
        for error in report["summary"]["ledgerErrors"]:
            print(f"ledger error: {error}", file=sys.stderr)
        return 2
    if args.fail_on_unledgered:
        blockers = blocking_unledgered(report, args.fail_on_unledgered)
        if blockers:
            for finding in blockers:
                print(
                    f"unledgered {finding['severity']} finding: {finding['findingKey']}",
                    file=sys.stderr,
                )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
