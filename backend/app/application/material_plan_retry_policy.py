from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialPlanAttempt:
    label: str
    model: str
    repair: bool = False
    backup: bool = False


def build_material_plan_attempts(*, primary_model: str, backup_model: str | None) -> list[MaterialPlanAttempt]:
    attempts = [
        MaterialPlanAttempt(label="primary", model=primary_model, repair=False),
        MaterialPlanAttempt(label="primary-repair", model=primary_model, repair=True),
    ]
    if backup_model and backup_model != primary_model:
        attempts.append(MaterialPlanAttempt(label="backup", model=backup_model, repair=True, backup=True))
    return attempts
