from __future__ import annotations

import numpy as np
from coola import objects_are_equal

from batcharray.nested import to_list

#############################
#     Tests for to_list     #
#############################


def test_to_list_array_float() -> None:
    assert objects_are_equal(
        to_list(np.ones((2, 3), dtype=float)), [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    )


def test_to_list_array_int() -> None:
    assert objects_are_equal(to_list(np.ones((2, 3), dtype=int)), [[1, 1, 1], [1, 1, 1]])


def test_to_list_dict() -> None:
    assert objects_are_equal(
        to_list(
            {
                "a": np.array(
                    [[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]], dtype=np.float32
                ),
                "b": np.array([4, 3, 2, 1, 0], dtype=int),
            }
        ),
        {
            "a": [[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]],
            "b": [4, 3, 2, 1, 0],
        },
    )


def test_to_list_nested() -> None:
    assert objects_are_equal(
        to_list(
            {
                "a": np.array(
                    [[4.0, 9.0], [1.0, 7.0], [2.0, 5.0], [5.0, 6.0], [3.0, 8.0]], dtype=np.float64
                ),
                "b": np.array([4.0, 3.0, 2.0, 1.0, 0.0], dtype=np.float32),
                "list": [np.array([5, 6, 7, 8, 9], dtype=int), [6, 7, 8]],
                "int": 42,
            }
        ),
        {
            "a": [[4.0, 9.0], [1.0, 7.0], [2.0, 5.0], [5.0, 6.0], [3.0, 8.0]],
            "b": [4.0, 3.0, 2.0, 1.0, 0.0],
            "list": [[5, 6, 7, 8, 9], [6, 7, 8]],
            "int": 42,
        },
    )
