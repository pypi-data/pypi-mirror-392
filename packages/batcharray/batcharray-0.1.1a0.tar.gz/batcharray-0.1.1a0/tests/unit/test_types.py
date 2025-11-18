from __future__ import annotations

from batcharray.types import SORT_KINDS


def test_sort_kinds() -> None:
    assert len(SORT_KINDS) == 4
