import hashlib
import re


def normalize_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title.strip().lower())
    return re.sub(r"[^a-z0-9 ]", "", title)


def build_hash(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
