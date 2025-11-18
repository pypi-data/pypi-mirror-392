from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.array import (
    permute_along_batch,
    permute_along_seq,
    shuffle_along_batch,
    shuffle_along_seq,
)

if TYPE_CHECKING:
    from numpy.typing import DTypeLike

INDEX_DTYPES = [np.int32, np.int64, np.uint32]

#########################################
#     Tests for permute_along_batch     #
#########################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        permute_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            np.array([4, 3, 2, 1, 0], dtype=dtype),
        ),
        np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
    )


def test_permute_along_batch_incorrect_shape() -> None:
    with pytest.raises(
        RuntimeError,
        match=r"permutation shape \(.*\) is not compatible with array shape \(.*\)",
    ):
        permute_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), np.array([4, 3, 2, 1, 0, 2, 0])
        )


def test_permute_along_batch_masked_array() -> None:
    assert objects_are_equal(
        permute_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            np.array([4, 3, 2, 1, 0]),
        ),
        np.ma.masked_array(
            data=np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
            mask=np.array(
                [[True, False], [False, False], [True, False], [False, False], [False, False]]
            ),
        ),
    )


#######################################
#     Tests for permute_along_seq     #
#######################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        permute_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), np.array([4, 3, 2, 1, 0], dtype=dtype)
        ),
        np.array([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
    )


def test_permute_along_seq_incorrect_shape() -> None:
    with pytest.raises(
        RuntimeError,
        match=r"permutation shape \(.*\) is not compatible with array shape \(.*\)",
    ):
        permute_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), np.array([4, 3, 2, 1, 0, 2, 0])
        )


def test_permute_along_seq_masked_array() -> None:
    assert objects_are_equal(
        permute_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            ),
            np.array([4, 3, 2, 1, 0]),
        ),
        np.ma.masked_array(
            data=np.array([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
            mask=np.array([[True, False, True, False, False], [False, False, False, False, False]]),
        ),
    )


#########################################
#     Tests for shuffle_along_batch     #
#########################################


def test_shuffle_along_batch() -> None:
    out = shuffle_along_batch(np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]))
    assert out.shape == (4, 3)


def test_shuffle_along_batch_mock_rng() -> None:
    rng = Mock(spec=np.random.Generator, permutation=Mock(return_value=np.array([2, 1, 3, 0])))
    assert objects_are_equal(
        shuffle_along_batch(np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]), rng),
        np.array([[6, 7, 8], [3, 4, 5], [9, 10, 11], [0, 1, 2]]),
    )


def test_shuffle_along_batch_same_random_seed() -> None:
    array = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])
    assert objects_are_equal(
        shuffle_along_batch(array, np.random.default_rng(1)),
        shuffle_along_batch(array, np.random.default_rng(1)),
    )


def test_shuffle_along_batch_different_random_seeds() -> None:
    array = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])
    assert not objects_are_equal(
        shuffle_along_batch(array, np.random.default_rng(1)),
        shuffle_along_batch(array, np.random.default_rng(2)),
    )


def test_shuffle_along_batch_multiple_shuffle() -> None:
    array = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])
    rng = np.random.default_rng(1)
    assert not objects_are_equal(shuffle_along_batch(array, rng), shuffle_along_batch(array, rng))


#######################################
#     Tests for shuffle_along_seq     #
#######################################


def test_shuffle_along_seq() -> None:
    out = shuffle_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]))
    assert out.shape == (2, 5)


def test_shuffle_along_seq_mock_rng() -> None:
    rng = Mock(spec=np.random.Generator, permutation=Mock(return_value=np.array([2, 4, 1, 3, 0])))
    assert objects_are_equal(
        shuffle_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), rng),
        np.array([[2, 4, 1, 3, 0], [7, 9, 6, 8, 5]]),
    )


def test_shuffle_along_seq_same_random_seed() -> None:
    array = np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
    assert objects_are_equal(
        shuffle_along_seq(array, np.random.default_rng(1)),
        shuffle_along_seq(array, np.random.default_rng(1)),
    )


def test_shuffle_along_seq_different_random_seeds() -> None:
    array = np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
    assert not objects_are_equal(
        shuffle_along_seq(array, np.random.default_rng(1)),
        shuffle_along_seq(array, np.random.default_rng(2)),
    )


def test_shuffle_along_seq_multiple_shuffle() -> None:
    array = np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
    rng = np.random.default_rng(1)
    assert not objects_are_equal(shuffle_along_seq(array, rng), shuffle_along_seq(array, rng))
