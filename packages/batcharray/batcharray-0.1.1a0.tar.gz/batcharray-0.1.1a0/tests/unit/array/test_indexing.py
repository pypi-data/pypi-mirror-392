from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.array import (
    index_select_along_batch,
    index_select_along_seq,
    masked_select_along_batch,
    masked_select_along_seq,
    take_along_batch,
    take_along_seq,
)

if TYPE_CHECKING:
    from numpy.typing import DTypeLike

INDEX_DTYPES = [np.int32, np.int64, np.uint32]


##############################################
#     Tests for index_select_along_batch     #
##############################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_index_select_along_batch_2(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        index_select_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            indices=np.array([2, 4], dtype=dtype),
        ),
        np.array([[4, 5], [8, 9]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_index_select_along_batch_5(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        index_select_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            indices=np.array([4, 3, 2, 1, 0], dtype=dtype),
        ),
        np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_index_select_along_batch_7(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        index_select_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            indices=np.array([4, 3, 2, 1, 0, 2, 0], dtype=dtype),
        ),
        np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1], [4, 5], [0, 1]]),
    )


def test_index_select_along_batch_masked_array() -> None:
    assert objects_are_equal(
        index_select_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            indices=np.array([2, 4]),
        ),
        np.ma.masked_array(
            data=np.array([[4, 5], [8, 9]]), mask=np.array([[True, False], [True, False]])
        ),
    )


############################################
#     Tests for index_select_along_seq     #
############################################


@pytest.mark.parametrize("indices", [np.array([2, 4]), np.array([[2, 4], [2, 4]])])
@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_index_select_along_seq_2(dtype: DTypeLike, indices: np.ndarray) -> None:
    assert objects_are_equal(
        index_select_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), indices=indices.astype(dtype=dtype)
        ),
        np.array([[2, 4], [7, 9]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_index_select_along_seq_5(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        index_select_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
            indices=np.array([4, 3, 2, 1, 0], dtype=dtype),
        ),
        np.array([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_index_select_along_seq_7(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        index_select_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
            indices=np.array([4, 3, 2, 1, 0, 2, 0], dtype=dtype),
        ),
        np.array([[4, 3, 2, 1, 0, 2, 0], [9, 8, 7, 6, 5, 7, 5]]),
    )


def test_index_select_along_seq_per_batch_indices() -> None:
    assert objects_are_equal(
        index_select_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), indices=np.array([[2, 4], [1, 3]])
        ),
        np.array([[2, 4], [6, 8]]),
    )


def test_index_select_along_seq_extra_dims() -> None:
    assert objects_are_equal(
        index_select_along_seq(
            np.array(
                [
                    [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
                    [[10, 11], [12, 13], [14, 15], [16, 17], [18, 19]],
                ]
            ),
            indices=np.array([[2, 0], [4, 3]]),
        ),
        np.array([[[4, 5], [0, 1]], [[18, 19], [16, 17]]]),
    )


def test_index_select_along_seq_masked_array_1d() -> None:
    assert objects_are_equal(
        index_select_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            ),
            indices=np.array([2, 4]),
        ),
        np.ma.masked_array(
            data=np.array([[2, 4], [7, 9]]), mask=np.array([[True, True], [False, False]])
        ),
    )


def test_index_select_along_seq_masked_array_2d() -> None:
    assert objects_are_equal(
        index_select_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            ),
            indices=np.array([[2, 4], [1, 3]]),
        ),
        np.ma.masked_array(
            data=np.array([[2, 4], [6, 8]]), mask=np.array([[True, True], [False, False]])
        ),
    )


###############################################
#     Tests for masked_select_along_batch     #
###############################################


def test_masked_select_along_batch() -> None:
    assert objects_are_equal(
        masked_select_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            mask=np.array([False, False, True, False, True]),
        ),
        np.array([[4, 5], [8, 9]]),
    )


def test_masked_select_along_batch_masked_array() -> None:
    assert objects_are_equal(
        masked_select_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            mask=np.array([False, False, True, False, True]),
        ),
        np.ma.masked_array(
            np.array([[4, 5], [8, 9]]), mask=np.array([[True, False], [True, False]])
        ),
    )


#############################################
#     Tests for masked_select_along_seq     #
#############################################


def test_masked_select_along_seq() -> None:
    assert objects_are_equal(
        masked_select_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
            mask=np.array([False, False, True, False, True]),
        ),
        np.array([[2, 4], [7, 9]]),
    )


def test_masked_select_along_seq_masked_array() -> None:
    assert objects_are_equal(
        masked_select_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            ),
            mask=np.array([False, False, True, False, True]),
        ),
        np.ma.masked_array(
            data=np.array([[2, 4], [7, 9]]), mask=np.array([[True, True], [False, False]])
        ),
    )


######################################
#     Tests for take_along_batch     #
######################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_take_along_batch_2(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        take_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            indices=np.array([2, 4], dtype=dtype),
        ),
        np.array([[4, 5], [8, 9]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_take_along_batch_5(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        take_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            indices=np.array([4, 3, 2, 1, 0], dtype=dtype),
        ),
        np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_take_along_batch_7(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        take_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            indices=np.array([4, 3, 2, 1, 0, 2, 0], dtype=dtype),
        ),
        np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1], [4, 5], [0, 1]]),
    )


def test_take_along_batch_masked_array() -> None:
    assert objects_are_equal(
        take_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            indices=np.array([2, 4]),
        ),
        np.ma.masked_array(
            data=np.array([[4, 5], [8, 9]]), mask=np.array([[True, False], [True, False]])
        ),
    )


####################################
#     Tests for take_along_seq     #
####################################


@pytest.mark.parametrize("indices", [np.array([2, 4]), np.array([[2, 4], [2, 4]])])
@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_take_along_seq_2(dtype: DTypeLike, indices: np.ndarray) -> None:
    assert objects_are_equal(
        take_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), indices=indices.astype(dtype=dtype)
        ),
        np.array([[2, 4], [7, 9]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_take_along_seq_5(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        take_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
            indices=np.array([4, 3, 2, 1, 0], dtype=dtype),
        ),
        np.array([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_take_along_seq_7(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        take_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
            indices=np.array([4, 3, 2, 1, 0, 2, 0], dtype=dtype),
        ),
        np.array([[4, 3, 2, 1, 0, 2, 0], [9, 8, 7, 6, 5, 7, 5]]),
    )


def test_take_along_seq_per_batch_indices() -> None:
    assert objects_are_equal(
        take_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), indices=np.array([[2, 4], [1, 3]])
        ),
        np.array([[2, 4], [6, 8]]),
    )


def test_take_along_seq_extra_dims() -> None:
    assert objects_are_equal(
        take_along_seq(
            np.array(
                [
                    [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
                    [[10, 11], [12, 13], [14, 15], [16, 17], [18, 19]],
                ]
            ),
            indices=np.array([[2, 0], [4, 3]]),
        ),
        np.array([[[4, 5], [0, 1]], [[18, 19], [16, 17]]]),
    )


def test_take_along_seq_masked_array_1d() -> None:
    assert objects_are_equal(
        take_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            ),
            indices=np.array([2, 4]),
        ),
        np.ma.masked_array(
            data=np.array([[2, 4], [7, 9]]), mask=np.array([[True, True], [False, False]])
        ),
    )


def test_take_along_seq_masked_array_2d() -> None:
    assert objects_are_equal(
        take_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            ),
            indices=np.array([[2, 4], [1, 3]]),
        ),
        np.ma.masked_array(
            data=np.array([[2, 4], [6, 8]]), mask=np.array([[True, True], [False, False]])
        ),
    )
