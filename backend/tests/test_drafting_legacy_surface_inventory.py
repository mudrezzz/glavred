import ast
from pathlib import Path

from backend.app.drafting.application.migration.legacy_surface_inventory import (
    LEGACY_DRAFT_RUN_SURFACE_INVENTORY,
    LegacyHelperDisposition,
    LegacyMigrationCluster,
    LegacyModuleDisposition,
    legacy_surface_inventory_payload,
)


LEGACY_APPLICATION_ROOT = Path("backend/app/application")


def _legacy_surface_modules() -> set[str]:
    return {
        path.as_posix()
        for path in (
            *LEGACY_APPLICATION_ROOT.glob("draft_*.py"),
            *LEGACY_APPLICATION_ROOT.glob("deterministic_*.py"),
        )
    }


def _public_top_level_functions(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }


def test_inventory_covers_every_legacy_draft_application_module() -> None:
    inventoried = {entry.current_module for entry in LEGACY_DRAFT_RUN_SURFACE_INVENTORY}

    assert inventoried == _legacy_surface_modules()


def test_inventory_covers_every_public_top_level_helper() -> None:
    entries_by_module = {
        entry.current_module: {helper.helper_name for helper in entry.public_helpers}
        for entry in LEGACY_DRAFT_RUN_SURFACE_INVENTORY
    }

    for module in sorted(_legacy_surface_modules()):
        public_helpers = _public_top_level_functions(Path(module))

        assert public_helpers <= entries_by_module[module], module


def test_inventory_entries_have_valid_owners_and_dispositions() -> None:
    for entry in LEGACY_DRAFT_RUN_SURFACE_INVENTORY:
        assert entry.cluster in LegacyMigrationCluster.ALL
        assert entry.module_disposition in LegacyModuleDisposition.ALL
        assert entry.target_package.startswith("backend/app/drafting/")
        assert entry.target_owner.startswith("backend.app.drafting.")
        assert entry.migration_slice
        assert entry.compatibility_strategy
        assert entry.notes
        assert "unknown" not in entry.target_owner.lower()

        for helper in entry.public_helpers:
            assert helper.helper_disposition in LegacyHelperDisposition.ALL
            assert helper.target_owner == entry.target_owner
            assert helper.target_visibility in {"private", "package", "compatibility"}
            assert helper.rationale


def test_deterministic_modules_have_fallback_policy_or_service_targets() -> None:
    deterministic_entries = [
        entry
        for entry in LEGACY_DRAFT_RUN_SURFACE_INVENTORY
        if Path(entry.current_module).name.startswith("deterministic_")
    ]

    assert deterministic_entries
    for entry in deterministic_entries:
        assert entry.module_disposition in {
            LegacyModuleDisposition.POLICY,
            LegacyModuleDisposition.SERVICE,
        }
        assert "fallback" in entry.target_owner.lower()
        assert "fallback" in entry.compatibility_strategy.lower()


def test_inventory_payload_keeps_public_review_shape() -> None:
    payload = legacy_surface_inventory_payload()

    assert payload
    for entry in payload:
        assert set(entry) == {
            "currentModule",
            "cluster",
            "targetPackage",
            "moduleDisposition",
            "targetOwner",
            "migrationSlice",
            "compatibilityStrategy",
            "publicHelpers",
            "notes",
        }
        for helper in entry["publicHelpers"]:
            assert set(helper) == {
                "helperName",
                "helperDisposition",
                "targetOwner",
                "targetVisibility",
                "rationale",
            }
