from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.nested import (
    permute_along_batch,
    permute_along_seq,
    shuffle_along_batch,
    shuffle_along_seq,
)
from tests.unit.array.test_permutation import INDEX_DTYPES

if TYPE_CHECKING:
    from numpy.typing import DTypeLike

#########################################
#     Tests for permute_along_batch     #
#########################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        permute_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            np.array([4, 3, 2, 1, 0], dtype=dtype),
        ),
        np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        permute_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            np.array([4, 3, 2, 1, 0], dtype=dtype),
        ),
        {
            "a": np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
            "b": np.array([0, 1, 2, 3, 4]),
        },
    )


def test_permute_along_batch_nested() -> None:
    assert objects_are_equal(
        permute_along_batch(
            {
                "a": np.array([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
                "list": [np.array([5, 6, 7, 8, 9])],
                "masked": np.ma.masked_array(
                    data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                    mask=np.array(
                        [
                            [False, False],
                            [False, False],
                            [True, False],
                            [False, False],
                            [True, False],
                        ]
                    ),
                ),
            },
            permutation=np.array([2, 4, 1, 3, 0]),
        ),
        {
            "a": np.array([[2, 5], [3, 8], [1, 7], [5, 6], [4, 9]]),
            "b": np.array([2, 0, 3, 1, 4], dtype=np.float32),
            "list": [np.array([7, 9, 6, 8, 5])],
            "masked": np.ma.masked_array(
                data=np.array([[4, 5], [8, 9], [2, 3], [6, 7], [0, 1]]),
                mask=np.array(
                    [[True, False], [True, False], [False, False], [False, False], [False, False]]
                ),
            ),
        },
    )


def test_permute_along_batch_incorrect_shape() -> None:
    with pytest.raises(
        RuntimeError,
        match=r"permutation shape \(.*\) is not compatible with array shape \(.*\)",
    ):
        permute_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            np.array([4, 3, 2, 1, 0, 2]),
        )


#######################################
#     Tests for permute_along_seq     #
#######################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        permute_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), np.array([4, 3, 2, 1, 0], dtype=dtype)
        ),
        np.array([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        permute_along_seq(
            {"a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), "b": np.array([[4, 3, 2, 1, 0]])},
            np.array([4, 3, 2, 1, 0], dtype=dtype),
        ),
        {
            "a": np.array([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
            "b": np.array([[0, 1, 2, 3, 4]]),
        },
    )


def test_permute_along_seq_nested() -> None:
    assert objects_are_equal(
        permute_along_seq(
            {
                "a": np.array([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
                "list": [np.array([[5, 6, 7, 8, 9]])],
                "masked": np.ma.masked_array(
                    data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                    mask=np.array(
                        [[False, False, True, False, True], [False, False, False, False, False]]
                    ),
                ),
            },
            permutation=np.array([2, 4, 1, 3, 0]),
        ),
        {
            "a": np.array([[2, 3, 1, 5, 4], [5, 8, 7, 6, 9]]),
            "b": np.array([[2, 0, 3, 1, 4]], dtype=np.float32),
            "list": [np.array([[7, 9, 6, 8, 5]])],
            "masked": np.ma.masked_array(
                data=np.array([[2, 4, 1, 3, 0], [7, 9, 6, 8, 5]]),
                mask=np.array(
                    [[True, True, False, False, False], [False, False, False, False, False]]
                ),
            ),
        },
    )


def test_permute_along_seq_incorrect_shape() -> None:
    with pytest.raises(
        RuntimeError,
        match=r"permutation shape \(.*\) is not compatible with array shape \(.*\)",
    ):
        permute_along_seq(
            {"a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), "b": np.array([[4, 3, 2, 1, 0]])},
            np.array([4, 3, 2, 1, 0, 2]),
        )


#########################################
#     Tests for shuffle_along_batch     #
#########################################


def test_shuffle_along_batch() -> None:
    out = shuffle_along_batch(np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]))
    assert out.shape == (4, 3)


def test_shuffle_along_batch_array() -> None:
    rng = Mock(spec=np.random.Generator, permutation=Mock(return_value=np.array([2, 1, 3, 0])))
    assert objects_are_equal(
        shuffle_along_batch(np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]), rng=rng),
        np.array([[6, 7, 8], [3, 4, 5], [9, 10, 11], [0, 1, 2]]),
    )


def test_shuffle_along_batch_dict() -> None:
    rng = Mock(spec=np.random.Generator, permutation=Mock(return_value=np.array([2, 4, 1, 3, 0])))
    assert objects_are_equal(
        shuffle_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            rng=rng,
        ),
        {
            "a": np.array([[4, 5], [8, 9], [2, 3], [6, 7], [0, 1]]),
            "b": np.array([2, 0, 3, 1, 4]),
        },
    )


def test_shuffle_along_batch_nested() -> None:
    rng = Mock(spec=np.random.Generator, permutation=Mock(return_value=np.array([2, 4, 1, 3, 0])))
    assert objects_are_equal(
        shuffle_along_batch(
            {
                "a": np.array([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
                "list": [np.array([5, 6, 7, 8, 9])],
                "masked": np.ma.masked_array(
                    data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                    mask=np.array(
                        [
                            [False, False],
                            [False, False],
                            [True, False],
                            [False, False],
                            [True, False],
                        ]
                    ),
                ),
            },
            rng=rng,
        ),
        {
            "a": np.array([[2, 5], [3, 8], [1, 7], [5, 6], [4, 9]]),
            "b": np.array([2, 0, 3, 1, 4], dtype=np.float32),
            "list": [np.array([7, 9, 6, 8, 5])],
            "masked": np.ma.masked_array(
                data=np.array([[4, 5], [8, 9], [2, 3], [6, 7], [0, 1]]),
                mask=np.array(
                    [[True, False], [True, False], [False, False], [False, False], [False, False]]
                ),
            ),
        },
    )


def test_shuffle_along_batch_same_random_seed() -> None:
    data = {"a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), "b": np.array([4, 3, 2, 1, 0])}
    assert objects_are_equal(
        shuffle_along_batch(data, np.random.default_rng(1)),
        shuffle_along_batch(data, np.random.default_rng(1)),
    )


def test_shuffle_along_batch_different_random_seeds() -> None:
    data = {"a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), "b": np.array([4, 3, 2, 1, 0])}
    assert not objects_are_equal(
        shuffle_along_batch(data, np.random.default_rng(1)),
        shuffle_along_batch(data, np.random.default_rng(2)),
    )


def test_shuffle_along_batch_multiple_shuffle() -> None:
    data = {"a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), "b": np.array([4, 3, 2, 1, 0])}
    generator = np.random.default_rng(1)
    assert not objects_are_equal(
        shuffle_along_batch(data, generator), shuffle_along_batch(data, generator)
    )


#######################################
#     Tests for shuffle_along_seq     #
#######################################


def test_shuffle_along_seq() -> None:
    out = shuffle_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]))
    assert out.shape == (2, 5)


def test_shuffle_along_seq_array() -> None:
    rng = Mock(spec=np.random.Generator, permutation=Mock(return_value=np.array([2, 4, 1, 3, 0])))
    assert objects_are_equal(
        shuffle_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), rng=rng),
        np.array([[2, 4, 1, 3, 0], [7, 9, 6, 8, 5]]),
    )


def test_shuffle_along_seq_dict() -> None:
    rng = Mock(spec=np.random.Generator, permutation=Mock(return_value=np.array([2, 4, 1, 3, 0])))
    assert objects_are_equal(
        shuffle_along_seq(
            {"a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), "b": np.array([[4, 3, 2, 1, 0]])},
            rng=rng,
        ),
        {
            "a": np.array([[2, 4, 1, 3, 0], [7, 9, 6, 8, 5]]),
            "b": np.array([[2, 0, 3, 1, 4]]),
        },
    )


def test_shuffle_along_seq_nested() -> None:
    rng = Mock(spec=np.random.Generator, permutation=Mock(return_value=np.array([2, 4, 1, 3, 0])))
    assert objects_are_equal(
        shuffle_along_seq(
            {
                "a": np.array([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
                "list": [np.array([[5, 6, 7, 8, 9]])],
                "masked": np.ma.masked_array(
                    data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                    mask=np.array(
                        [[False, False, True, False, True], [False, False, False, False, False]]
                    ),
                ),
            },
            rng=rng,
        ),
        {
            "a": np.array([[2, 3, 1, 5, 4], [5, 8, 7, 6, 9]]),
            "b": np.array([[2, 0, 3, 1, 4]], dtype=np.float32),
            "list": [np.array([[7, 9, 6, 8, 5]])],
            "masked": np.ma.masked_array(
                data=np.array([[2, 4, 1, 3, 0], [7, 9, 6, 8, 5]]),
                mask=np.array(
                    [[True, True, False, False, False], [False, False, False, False, False]]
                ),
            ),
        },
    )


def test_shuffle_along_seq_same_random_seed() -> None:
    data = {"a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), "b": np.array([[4, 3, 2, 1, 0]])}
    assert objects_are_equal(
        shuffle_along_seq(data, np.random.default_rng(1)),
        shuffle_along_seq(data, np.random.default_rng(1)),
    )


def test_shuffle_along_seq_different_random_seeds() -> None:
    data = {"a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), "b": np.array([[4, 3, 2, 1, 0]])}
    assert not objects_are_equal(
        shuffle_along_seq(data, np.random.default_rng(1)),
        shuffle_along_seq(data, np.random.default_rng(2)),
    )


def test_shuffle_along_seq_multiple_shuffle() -> None:
    data = {"a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), "b": np.array([[4, 3, 2, 1, 0]])}
    generator = np.random.default_rng(1)
    assert not objects_are_equal(
        shuffle_along_seq(data, generator), shuffle_along_seq(data, generator)
    )
