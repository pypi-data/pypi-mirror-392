from typing import Dict

REQUIRED_KEYS = ["name", "contact"]

def validate_profile(profile: Dict) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in profile or not profile[k]]
    if missing:
        raise ValueError(f"Missing required profile fields: {missing}")

def normalize_profile(profile: Dict) -> Dict:
    profile.setdefault("skills", [])
    profile.setdefault("projects", [])
    profile.setdefault("experience", [])
    profile.setdefault("education", [])
    return profile
