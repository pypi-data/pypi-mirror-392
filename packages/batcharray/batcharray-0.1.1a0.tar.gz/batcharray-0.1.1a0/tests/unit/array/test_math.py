from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.array import (
    cumprod_along_batch,
    cumprod_along_seq,
    cumsum_along_batch,
    cumsum_along_seq,
)

if TYPE_CHECKING:
    from numpy.typing import DTypeLike

DTYPES = [np.int64, np.float32, np.float64]


#########################################
#     Tests for cumprod_along_batch     #
#########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumprod_along_batch(np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype)),
        np.array([[1, 2], [3, 8], [15, 48], [105, 384], [945, 3840]], dtype=dtype),
    )


def test_cumprod_along_batch_masked_array() -> None:
    assert objects_are_equal(
        cumprod_along_batch(
            np.ma.masked_array(
                data=np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]),
                mask=np.array(
                    [[False, False], [False, False], [False, True], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(
            data=np.array([[1, 2], [3, 8], [15, 8], [105, 64], [105, 640]]),
            mask=np.array(
                [[False, False], [False, False], [False, True], [False, False], [True, False]]
            ),
        ),
    )


#######################################
#     Tests for cumprod_along_seq     #
#######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumprod_along_seq(np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], dtype=dtype)),
        np.array([[1, 2, 6, 24, 120], [6, 42, 336, 3024, 30240]], dtype=dtype),
    )


def test_cumprod_along_seq_masked_array() -> None:
    assert objects_are_equal(
        cumprod_along_seq(
            np.ma.masked_array(
                data=np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]),
                mask=np.array(
                    [[False, False, False, False, True], [False, False, True, False, False]]
                ),
            )
        ),
        np.ma.masked_array(
            data=np.array([[1, 2, 6, 24, 24], [6, 42, 42, 378, 3780]]),
            mask=np.array([[False, False, False, False, True], [False, False, True, False, False]]),
        ),
    )


########################################
#     Tests for cumsum_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumsum_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([[0, 1], [2, 4], [6, 9], [12, 16], [20, 25]], dtype=dtype),
    )


def test_cumsum_along_batch_masked_array() -> None:
    assert objects_are_equal(
        cumsum_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [False, True], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(
            data=np.array([[0, 1], [2, 4], [6, 4], [12, 11], [12, 20]]),
            mask=np.array(
                [[False, False], [False, False], [False, True], [False, False], [True, False]]
            ),
        ),
    )


######################################
#     Tests for cumsum_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumsum_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([[0, 1, 3, 6, 10], [5, 11, 18, 26, 35]], dtype=dtype),
    )


def test_cumsum_along_seq_masked_array() -> None:
    assert objects_are_equal(
        cumsum_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, False, False, True], [False, False, True, False, False]]
                ),
            )
        ),
        np.ma.masked_array(
            data=np.array([[0, 1, 3, 6, 6], [5, 11, 11, 19, 28]]),
            mask=np.array([[False, False, False, False, True], [False, False, True, False, False]]),
        ),
    )
