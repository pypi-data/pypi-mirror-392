from __future__ import annotations

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.nested import (
    argsort_along_batch,
    argsort_along_seq,
    sort_along_batch,
    sort_along_seq,
)
from batcharray.types import SORT_KINDS, SortKind

#########################################
#     Tests for argsort_along_batch     #
#########################################


def test_argsort_along_batch_array() -> None:
    assert objects_are_equal(
        argsort_along_batch(np.array([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]])),
        np.array([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
    )


def test_argsort_along_batch_dict() -> None:
    assert objects_are_equal(
        argsort_along_batch(
            {
                "a": np.array([[2, 6], [0, 3], [4, 9], [8, 1], [5, 7]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
            }
        ),
        {
            "a": np.array([[1, 3], [0, 1], [2, 0], [4, 4], [3, 2]]),
            "b": np.array([4, 3, 2, 1, 0]),
        },
    )


def test_argsort_along_batch_nested() -> None:
    assert objects_are_equal(
        argsort_along_batch(
            {
                "a": np.array([[2, 6], [0, 3], [4, 9], [8, 1], [5, 7]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
                "list": [np.array([5, 6, 7, 8, 9])],
                "masked": np.ma.masked_array(
                    data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 4, 1, 3, 0]]),
                    mask=np.array(
                        [
                            [False, False, False, False, True],
                            [False, False, False, True, False],
                            [False, False, True, False, False],
                        ]
                    ),
                ),
            }
        ),
        {
            "a": np.array([[1, 3], [0, 1], [2, 0], [4, 4], [3, 2]]),
            "b": np.array([4, 3, 2, 1, 0]),
            "list": [np.array([0, 1, 2, 3, 4])],
            "masked": np.array([[0, 2, 0, 0, 2], [1, 0, 1, 2, 1], [2, 1, 2, 1, 0]]),
        },
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_argsort_along_batch_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        argsort_along_batch(
            {
                "a": np.array([[2, 6], [0, 3], [4, 9], [8, 1], [5, 7]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
                "list": [np.array([5, 6, 7, 8, 9])],
            },
            kind=kind,
        ),
        {
            "a": np.array([[1, 3], [0, 1], [2, 0], [4, 4], [3, 2]]),
            "b": np.array([4, 3, 2, 1, 0]),
            "list": [np.array([0, 1, 2, 3, 4])],
        },
    )


#######################################
#     Tests for argsort_along_seq     #
#######################################


def test_argsort_along_seq_array() -> None:
    assert objects_are_equal(
        argsort_along_seq(np.array([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]])),
        np.array([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
    )


def test_argsort_along_seq_dict() -> None:
    assert objects_are_equal(
        argsort_along_seq(
            {
                "a": np.array([[7, 3, 0, 8, 5], [1, 9, 6, 4, 2]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
            }
        ),
        {
            "a": np.array([[2, 1, 4, 0, 3], [0, 4, 3, 2, 1]]),
            "b": np.array([[4, 3, 2, 1, 0]]),
        },
    )


def test_argsort_along_seq_nested() -> None:
    assert objects_are_equal(
        argsort_along_seq(
            {
                "a": np.array([[7, 3, 0, 8, 5], [1, 9, 6, 4, 2]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
                "list": [np.array([[5, 6, 7, 8, 9]])],
                "masked": np.ma.masked_array(
                    data=np.array([[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]]),
                    mask=np.array(
                        [
                            [False, False, False, False, True],
                            [False, False, False, True, False],
                            [False, False, True, False, False],
                        ]
                    ),
                ),
            },
        ),
        {
            "a": np.array([[2, 1, 4, 0, 3], [0, 4, 3, 2, 1]]),
            "b": np.array([[4, 3, 2, 1, 0]]),
            "list": [np.array([[0, 1, 2, 3, 4]])],
            "masked": np.array([[0, 2, 3, 1, 4], [1, 0, 2, 4, 3], [0, 1, 4, 3, 2]]),
        },
    )


def test_argsort_along_seq_nested_stable() -> None:
    assert objects_are_equal(
        argsort_along_seq(
            {
                "a": np.array([[7, 3, 0, 8, 5], [1, 9, 6, 4, 2]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
                "list": [np.array([[5, 6, 7, 8, 9]])],
                "masked": np.ma.masked_array(
                    data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]]),
                    mask=np.array(
                        [
                            [False, False, False, False, True],
                            [False, False, False, True, False],
                            [False, False, True, False, False],
                        ]
                    ),
                ),
            },
            kind="stable",
        ),
        {
            "a": np.array([[2, 1, 4, 0, 3], [0, 4, 3, 2, 1]]),
            "b": np.array([[4, 3, 2, 1, 0]]),
            "list": [np.array([[0, 1, 2, 3, 4]])],
            "masked": np.array([[2, 3, 0, 1, 4], [0, 4, 1, 2, 3], [4, 1, 0, 3, 2]]),
        },
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_argsort_along_seq_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        argsort_along_seq(
            {
                "a": np.array([[7, 3, 0, 8, 5], [1, 9, 6, 4, 2]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
                "list": [np.array([[5, 6, 7, 8, 9]])],
            },
            kind=kind,
        ),
        {
            "a": np.array([[2, 1, 4, 0, 3], [0, 4, 3, 2, 1]]),
            "b": np.array([[4, 3, 2, 1, 0]]),
            "list": [np.array([[0, 1, 2, 3, 4]])],
        },
    )


######################################
#     Tests for sort_along_batch     #
######################################


def test_sort_along_batch_array() -> None:
    assert objects_are_equal(
        sort_along_batch(np.array([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]])),
        np.array([[1, 5], [2, 6], [3, 7], [4, 8], [5, 9]]),
    )


def test_sort_along_batch_dict() -> None:
    assert objects_are_equal(
        sort_along_batch(
            {
                "a": np.array([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
            }
        ),
        {
            "a": np.array([[1, 5], [2, 6], [3, 7], [4, 8], [5, 9]]),
            "b": np.array([0, 1, 2, 3, 4], dtype=np.float32),
        },
    )


def test_sort_along_batch_nested() -> None:
    assert objects_are_equal(
        sort_along_batch(
            {
                "a": np.array([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
                "list": [np.array([5, 6, 7, 8, 9])],
                "masked": np.ma.masked_array(
                    data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]]),
                    mask=np.array(
                        [
                            [False, False, False, False, True],
                            [False, False, False, True, False],
                            [False, False, True, False, False],
                        ]
                    ),
                ),
            }
        ),
        {
            "a": np.array([[1, 5], [2, 6], [3, 7], [4, 8], [5, 9]]),
            "b": np.array([0, 1, 2, 3, 4], dtype=np.float32),
            "list": [np.array([5, 6, 7, 8, 9])],
            "masked": np.ma.masked_array(
                data=np.array([[3, 5, 0, 2, 0], [4, 5, 8, 8, 5], [8, 7, 8, 8, 4]]),
                mask=np.array(
                    [
                        [False, False, False, False, False],
                        [False, False, False, False, False],
                        [False, False, True, True, True],
                    ]
                ),
            ),
        },
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_sort_along_batch_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        sort_along_batch(
            {
                "a": np.array([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
                "list": [np.array([5, 6, 7, 8, 9])],
            },
            kind=kind,
        ),
        {
            "a": np.array([[1, 5], [2, 6], [3, 7], [4, 8], [5, 9]]),
            "b": np.array([0, 1, 2, 3, 4], dtype=np.float32),
            "list": [np.array([5, 6, 7, 8, 9])],
        },
    )


####################################
#     Tests for sort_along_seq     #
####################################


def test_sort_along_seq_array() -> None:
    assert objects_are_equal(
        sort_along_seq(np.array([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]])),
        np.array([[1, 2, 3, 4, 5], [5, 6, 7, 8, 9]]),
    )


def test_sort_along_seq_dict() -> None:
    assert objects_are_equal(
        sort_along_seq(
            {
                "a": np.array([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
            }
        ),
        {
            "a": np.array([[1, 2, 3, 4, 5], [5, 6, 7, 8, 9]]),
            "b": np.array([[0, 1, 2, 3, 4]], dtype=np.float32),
        },
    )


def test_sort_along_seq_nested() -> None:
    assert objects_are_equal(
        sort_along_seq(
            {
                "a": np.array([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
                "list": [np.array([[5, 6, 7, 8, 9]])],
                "masked": np.ma.masked_array(
                    data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]]),
                    mask=np.array(
                        [
                            [False, False, False, False, True],
                            [False, False, False, True, False],
                            [False, False, True, False, False],
                        ]
                    ),
                ),
            }
        ),
        {
            "a": np.array([[1, 2, 3, 4, 5], [5, 6, 7, 8, 9]]),
            "b": np.array([[0, 1, 2, 3, 4]], dtype=np.float32),
            "list": [np.array([[5, 6, 7, 8, 9]])],
            "masked": np.ma.masked_array(
                data=np.array([[0, 2, 3, 5, 4], [4, 5, 7, 8, 8], [0, 5, 8, 8, 8]]),
                mask=np.array(
                    [
                        [False, False, False, False, True],
                        [False, False, False, False, True],
                        [False, False, False, False, True],
                    ]
                ),
            ),
        },
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_sort_along_seq_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        sort_along_seq(
            {
                "a": np.array([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
                "list": [np.array([[5, 6, 7, 8, 9]])],
            },
            kind=kind,
        ),
        {
            "a": np.array([[1, 2, 3, 4, 5], [5, 6, 7, 8, 9]]),
            "b": np.array([[0, 1, 2, 3, 4]], dtype=np.float32),
            "list": [np.array([[5, 6, 7, 8, 9]])],
        },
    )
