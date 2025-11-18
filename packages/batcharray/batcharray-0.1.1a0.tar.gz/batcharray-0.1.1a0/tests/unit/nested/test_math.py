from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.nested import (
    cumprod_along_batch,
    cumprod_along_seq,
    cumsum_along_batch,
    cumsum_along_seq,
)
from tests.unit.array.test_math import DTYPES

if TYPE_CHECKING:
    from numpy.typing import DTypeLike

#########################################
#     Tests for cumprod_along_batch     #
#########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumprod_along_batch(np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype)),
        np.array([[1, 2], [3, 8], [15, 48], [105, 384], [945, 3840]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumprod_along_batch(
            {
                "a": np.ma.masked_array(
                    data=np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype),
                    mask=np.array(
                        [
                            [False, False],
                            [False, False],
                            [False, True],
                            [False, False],
                            [True, False],
                        ]
                    ),
                ),
                "b": np.array([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": np.ma.masked_array(
                data=np.array([[1, 2], [3, 8], [15, 8], [105, 64], [105, 640]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [False, True], [False, False], [True, False]]
                ),
            ),
            "b": np.array([4, 12, 24, 24, 0]),
        },
    )


#######################################
#     Tests for cumprod_along_seq     #
#######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumprod_along_seq(np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], dtype=dtype)),
        np.array([[1, 2, 6, 24, 120], [6, 42, 336, 3024, 30240]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumprod_along_seq(
            {
                "a": np.ma.masked_array(
                    data=np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], dtype=dtype),
                    mask=np.array(
                        [[False, False, False, False, True], [False, False, True, False, False]]
                    ),
                ),
                "b": np.array([[4, 3, 2, 1, 0]]),
            }
        ),
        {
            "a": np.ma.masked_array(
                data=np.array([[1, 2, 6, 24, 24], [6, 42, 42, 378, 3780]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, True], [False, False, True, False, False]]
                ),
            ),
            "b": np.array([[4, 12, 24, 24, 0]]),
        },
    )


########################################
#     Tests for cumsum_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumsum_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([[0, 1], [2, 4], [6, 9], [12, 16], [20, 25]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumsum_along_batch(
            {
                "a": np.ma.masked_array(
                    data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                    mask=np.array(
                        [
                            [False, False],
                            [False, False],
                            [False, True],
                            [False, False],
                            [True, False],
                        ]
                    ),
                ),
                "b": np.array([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": np.ma.masked_array(
                data=np.array([[0, 1], [2, 4], [6, 4], [12, 11], [12, 20]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [False, True], [False, False], [True, False]]
                ),
            ),
            "b": np.array([4, 7, 9, 10, 10]),
        },
    )


######################################
#     Tests for cumsum_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumsum_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([[0, 1, 3, 6, 10], [5, 11, 18, 26, 35]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        cumsum_along_seq(
            {
                "a": np.ma.masked_array(
                    data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                    mask=np.array(
                        [[False, False, False, False, True], [False, False, True, False, False]]
                    ),
                ),
                "b": np.array([[4, 3, 2, 1, 0]]),
            }
        ),
        {
            "a": np.ma.masked_array(
                data=np.array([[0, 1, 3, 6, 6], [5, 11, 11, 19, 28]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, True], [False, False, True, False, False]]
                ),
            ),
            "b": np.array([[4, 7, 9, 10, 10]]),
        },
    )
