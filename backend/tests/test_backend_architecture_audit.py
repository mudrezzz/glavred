import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "backend-architecture-audit.py"
SPEC = importlib.util.spec_from_file_location("backend_architecture_audit", SCRIPT_PATH)
assert SPEC is not None
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


OWNERSHIP_HEADER = '''"""Owner: backend.test

Used by: architecture audit tests.
Does not own: runtime behavior.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""
'''


def write_module(root: Path, relative_path: str, source: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return path


def finding_keys(root: Path) -> set[str]:
    return {finding.findingKey for finding in audit.collect_findings(root)}


def test_detects_public_helper_sprawl_with_deterministic_key(tmp_path: Path) -> None:
    write_module(
        tmp_path,
        "backend/app/drafting/application/validation/helper_sprawl.py",
        OWNERSHIP_HEADER
        + """
def build_one() -> str:
    return "1"

def build_two() -> str:
    return "2"

def build_three() -> str:
    return "3"
""",
    )

    findings = audit.collect_findings(tmp_path)
    sprawl = [
        finding
        for finding in findings
        if finding.findingKey
        == "publicHelperSprawl:backend/app/drafting/application/validation/helper_sprawl.py"
    ]

    assert sprawl
    assert sprawl[0].severity == "high"
    assert sprawl[0].symbols == ["build_one", "build_two", "build_three"]


def test_detects_behavior_inside_migrated_thin_shim(tmp_path: Path) -> None:
    write_module(
        tmp_path,
        "backend/app/application/draft_bad_shim.py",
        '''"""Compatibility shim for backend.app.drafting.application.validation.bad."""

from backend.app.drafting.application.validation.bad import *

def leaked_behavior() -> dict[str, str]:
    return {"bad": "yes"}
''',
    )

    assert "shimBehavior:backend/app/application/draft_bad_shim.py" in finding_keys(tmp_path)


def test_detects_raw_provider_call_outside_allowed_adapter(tmp_path: Path) -> None:
    write_module(
        tmp_path,
        "backend/app/drafting/application/validation/provider_leak.py",
        OWNERSHIP_HEADER
        + """
class BadProviderService:
    def run(self, provider):
        return provider.complete_json([])
""",
    )

    findings = {
        finding.findingKey: finding for finding in audit.collect_findings(tmp_path)
    }
    finding = findings["providerBoundaryLeak:backend/app/drafting/application/validation/provider_leak.py"]
    assert finding.severity == "critical"


def test_detects_dependency_direction_risk(tmp_path: Path) -> None:
    write_module(
        tmp_path,
        "backend/app/domain/bad_domain.py",
        """
from fastapi import APIRouter

VALUE = APIRouter()
""",
    )

    assert "dependencyDirectionRisk:backend/app/domain/bad_domain.py" in finding_keys(tmp_path)


def test_detects_raw_dict_contract(tmp_path: Path) -> None:
    write_module(
        tmp_path,
        "backend/app/drafting/application/validation/raw_contract.py",
        OWNERSHIP_HEADER
        + """
from typing import Any

def expose_result() -> dict[str, Any]:
    return {}
""",
    )

    assert "rawDictContract:backend/app/drafting/application/validation/raw_contract.py" in finding_keys(tmp_path)


def test_ledger_matching_separates_known_from_unledgered_debt(tmp_path: Path) -> None:
    write_module(
        tmp_path,
        "backend/app/drafting/application/validation/helper_sprawl.py",
        OWNERSHIP_HEADER
        + """
def build_one() -> str:
    return "1"

def build_two() -> str:
    return "2"

def build_three() -> str:
    return "3"
""",
    )
    ledger_path = tmp_path / "docs/architecture/backend-architecture-debt-ledger.json"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        json.dumps(
            {
                "version": 1,
                "updatedForSlice": "test",
                "policy": "test policy",
                "entries": [
                    {
                        "debtId": "test-public-helper-sprawl",
                        "findingKey": (
                            "publicHelperSprawl:"
                            "backend/app/drafting/application/validation/helper_sprawl.py"
                        ),
                        "package": "backend/app/drafting/application/validation",
                        "module": "backend/app/drafting/application/validation/helper_sprawl.py",
                        "smellType": "publicHelperSprawl",
                        "severity": "high",
                        "owner": "drafting.application.validation",
                        "targetShape": "component",
                        "allowedUntilSlice": "test",
                        "repairSlice": "test",
                        "guardrail": "test",
                        "currentEvidence": "test",
                        "notes": "test",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = audit.build_report(tmp_path, ledger_path)

    assert not audit.blocking_unledgered(report, "high")
    assert report["ledgerCoverage"]["ledgeredFindingKeys"] == [
        "publicHelperSprawl:backend/app/drafting/application/validation/helper_sprawl.py"
    ]
