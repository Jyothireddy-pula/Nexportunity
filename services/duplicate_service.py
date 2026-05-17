from rapidfuzz import fuzz


class DuplicateService:
    def __init__(self, threshold: int = 90):
        self.threshold = threshold

    def is_duplicate(self, candidate: dict, existing_rows: list[dict]) -> bool:
        for row in existing_rows:
            if candidate["source_link"] == row["source_link"]:
                return True
            if candidate["row_hash"] == row.get("row_hash"):
                return True
            score = fuzz.token_sort_ratio(candidate["normalized_title"], row["normalized_title"])
            if score >= self.threshold:
                return True
        return False
