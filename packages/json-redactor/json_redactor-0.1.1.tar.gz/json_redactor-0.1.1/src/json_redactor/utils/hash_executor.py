from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any


def _hash_value_worker(value: Any) -> str:
    if isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


class HashExecutor:
    """
    Wrapper around ThreadPoolExecutor for parallel SHA-256 hashing.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, value: Any):
        return self.pool.submit(_hash_value_worker, value)

    def shutdown(self) -> None:
        self.pool.shutdown(wait=True)
