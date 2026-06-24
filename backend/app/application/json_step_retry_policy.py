from dataclasses import dataclass


@dataclass(frozen=True)
class JsonStepAttempt:
    label: str
    model: str
    repair: bool = False
    backup: bool = False


def build_json_step_attempts(*, primary_model: str, backup_model: str | None) -> list[JsonStepAttempt]:
    attempts = [
        JsonStepAttempt(label="primary", model=primary_model),
        JsonStepAttempt(label="primary-repair", model=primary_model, repair=True),
    ]
    if backup_model and backup_model != primary_model:
        attempts.append(JsonStepAttempt(label="backup", model=backup_model, repair=True, backup=True))
    return attempts
