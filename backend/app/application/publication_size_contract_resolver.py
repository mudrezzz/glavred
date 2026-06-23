from typing import Any

from backend.app.domain.publication_size import PublicationSizeContract


DEFAULT_PROFILE = {
    "id": "telegram-post",
    "title": "Telegram post",
    "platform": "Telegram",
    "publicationKind": "shortPost",
    "minChars": 1800,
    "targetChars": 2800,
    "maxChars": 3800,
    "hardMaxChars": 4096,
    "paragraphRange": {"min": 4, "max": 8},
    "sectionRange": {"min": 1, "max": 1},
    "density": "normal",
}

SIZE_MULTIPLIERS = {
    "compact": 0.85,
    "standard": 1.0,
    "deep": 1.15,
}


class PublicationSizeContractResolver:
    def resolve(self, context_artifact: dict[str, Any]) -> PublicationSizeContract:
        publication_size = _as_dict(context_artifact.get("publicationSize"))
        profile, source = _select_profile(publication_size)
        intent = str(publication_size.get("fabulaSizeIntent") or "standard")
        multiplier = SIZE_MULTIPLIERS.get(intent, 1.0)
        hard_max = _int(profile.get("hardMaxChars"), DEFAULT_PROFILE["hardMaxChars"])
        min_chars = _clamp(round(_int(profile.get("minChars"), DEFAULT_PROFILE["minChars"]) * multiplier), 100, hard_max)
        target_chars = _clamp(round(_int(profile.get("targetChars"), DEFAULT_PROFILE["targetChars"]) * multiplier), min_chars, hard_max)
        max_chars = _clamp(round(_int(profile.get("maxChars"), DEFAULT_PROFILE["maxChars"]) * multiplier), target_chars, hard_max)
        return PublicationSizeContract(
            profile_id=str(profile.get("id") or DEFAULT_PROFILE["id"]),
            title=str(profile.get("title") or DEFAULT_PROFILE["title"]),
            platform=str(profile.get("platform") or publication_size.get("platform") or DEFAULT_PROFILE["platform"]),
            publication_kind=str(profile.get("publicationKind") or DEFAULT_PROFILE["publicationKind"]),
            min_chars=min_chars,
            target_chars=target_chars,
            max_chars=max_chars,
            hard_max_chars=hard_max,
            paragraph_range=_range(profile.get("paragraphRange"), DEFAULT_PROFILE["paragraphRange"]),
            section_range=_range(profile.get("sectionRange"), DEFAULT_PROFILE["sectionRange"]),
            density=str(profile.get("density") or DEFAULT_PROFILE["density"]),
            fabula_size_intent=intent if intent in SIZE_MULTIPLIERS else "standard",
            source=source,
        )


def _select_profile(publication_size: dict[str, Any]) -> tuple[dict[str, Any], str]:
    slot_profile_id = publication_size.get("slotProfileId")
    selected = _as_dict(publication_size.get("selectedProfile"))
    if selected and (not slot_profile_id or selected.get("id") == slot_profile_id):
        return selected, "slotProfile" if slot_profile_id else "defaultProfile"
    profiles = _list_of_dicts(publication_size.get("availableProfiles"))
    for profile in profiles:
        if profile.get("id") == publication_size.get("defaultProfileId"):
            return profile, "defaultProfile"
    for profile in profiles:
        if profile.get("platform") == publication_size.get("platform"):
            return profile, "platformDefault"
    return dict(DEFAULT_PROFILE), "demoDefault"


def _range(value: Any, fallback: dict[str, int]) -> dict[str, int]:
    source = _as_dict(value)
    min_value = _int(source.get("min"), fallback["min"])
    return {"min": min_value, "max": max(min_value, _int(source.get("max"), fallback["max"]))}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _int(value: Any, fallback: int) -> int:
    return int(value) if isinstance(value, (int, float)) else fallback


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return min(maximum, max(minimum, value))
