from collections import Counter
from threading import Lock
from typing import Iterable

from models import CaseResult


class CasePopularity:
    def __init__(self):
        self._counts: Counter[str] = Counter()
        self._lock = Lock()

    def record(self, cases: Iterable[CaseResult]) -> None:
        case_ids = {case.case_id for case in cases if case.case_id}
        with self._lock:
            self._counts.update(case_ids)

    def ranked_ids(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counts)


case_popularity = CasePopularity()