from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from coola import objects_are_allclose, objects_are_equal

from batcharray.array import (
    amax_along_batch,
    amax_along_seq,
    amin_along_batch,
    amin_along_seq,
    argmax_along_batch,
    argmax_along_seq,
    argmin_along_batch,
    argmin_along_seq,
    max_along_batch,
    max_along_seq,
    mean_along_batch,
    mean_along_seq,
    median_along_batch,
    median_along_seq,
    min_along_batch,
    min_along_seq,
    prod_along_batch,
    prod_along_seq,
    sum_along_batch,
    sum_along_seq,
)

if TYPE_CHECKING:
    from numpy.typing import DTypeLike

DTYPES = (np.float64, np.int64)
FLOATING_DTYPES = (np.float32, np.float64)


######################################
#     Tests for amax_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([8, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[8, 9]], dtype=dtype),
    )


def test_amax_along_batch_masked_array() -> None:
    assert objects_are_equal(
        amax_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([6, 9]), mask=np.array([[False, False]])),
    )


####################################
#     Tests for amax_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([4, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[4], [9]], dtype=dtype),
    )


def test_amax_along_seq_masked_array() -> None:
    assert objects_are_equal(
        amax_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([3, 9]), mask=np.array([[False], [False]])),
    )


######################################
#     Tests for amin_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([0, 1], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[0, 1]], dtype=dtype),
    )


def test_amin_along_batch_masked_array() -> None:
    assert objects_are_equal(
        amin_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, True], [False, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([0, 3]), mask=np.array([[False, False]])),
    )


####################################
#     Tests for amin_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([0, 5], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[0], [5]], dtype=dtype),
    )


def test_amin_along_seq_masked_array() -> None:
    assert objects_are_equal(
        amin_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[True, False, True, False, False], [False, False, False, False, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([1, 5]), mask=np.array([[False], [False]])),
    )


########################################
#     Tests for argmax_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[4, 4]]),
    )


def test_argmax_along_batch_masked_array() -> None:
    assert objects_are_equal(
        argmax_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.array([3, 4]),
    )


######################################
#     Tests for argmax_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[4], [4]]),
    )


def test_argmax_along_seq_masked_array() -> None:
    assert objects_are_equal(
        argmax_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            )
        ),
        np.array([3, 4]),
    )


########################################
#     Tests for argmin_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[0, 0]]),
    )


def test_argmin_along_batch_masked_array() -> None:
    assert objects_are_equal(
        argmin_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.array([0, 0]),
    )


######################################
#     Tests for argmin_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[0], [0]]),
    )


def test_argmin_along_seq_masked_array() -> None:
    assert objects_are_equal(
        argmin_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[True, False, True, False, False], [False, False, False, False, False]]
                ),
            )
        ),
        np.array([1, 0]),
    )


#####################################
#     Tests for max_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([8, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[8, 9]], dtype=dtype),
    )


def test_max_along_batch_masked_array() -> None:
    assert objects_are_equal(
        max_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([6, 9]), mask=np.array([[False, False]])),
    )


###################################
#     Tests for max_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([4, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[4], [9]], dtype=dtype),
    )


def test_max_along_seq_masked_array() -> None:
    assert objects_are_equal(
        max_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([3, 9]), mask=np.array([[False], [False]])),
    )


######################################
#     Tests for mean_along_batch     #
######################################


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([4.0, 5.0], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[4.0, 5.0]], dtype=dtype),
    )


def test_mean_along_batch_masked_array() -> None:
    assert objects_are_equal(
        mean_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [True, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([3.0, 5.0]), mask=np.array([[False, False]])),
    )


####################################
#     Tests for mean_along_seq     #
####################################


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([2.0, 7.0], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[2.0], [7.0]], dtype=dtype),
    )


def test_mean_along_seq_masked_array() -> None:
    assert objects_are_allclose(
        mean_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            )
        ),
        np.ma.masked_array(
            data=np.array([1.3333333333333333, 7.0]), mask=np.array([[False], [False]])
        ),
    )


########################################
#     Tests for median_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([4.0, 5.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[4.0, 5.0]]),
    )


def test_median_along_batch_masked_array() -> None:
    assert objects_are_equal(
        median_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([2.0, 5.0]), mask=np.array([[False, False]])),
    )


######################################
#     Tests for median_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([2.0, 7.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[2.0], [7.0]]),
    )


def test_median_along_seq_masked_array() -> None:
    assert objects_are_equal(
        median_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([1.0, 7.0]), mask=np.array([[False], [False]])),
    )


#####################################
#     Tests for min_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([0, 1], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[0, 1]], dtype=dtype),
    )


def test_min_along_batch_masked_array() -> None:
    assert objects_are_equal(
        min_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([0, 1]), mask=np.array([[False, False]])),
    )


###################################
#     Tests for min_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([0, 5], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[0], [5]], dtype=dtype),
    )


def test_min_along_seq_masked_array() -> None:
    assert objects_are_equal(
        min_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[True, False, True, False, False], [False, False, False, False, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([1, 5]), mask=np.array([[False], [False]])),
    )


######################################
#     Tests for prod_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([0, 945], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[0, 945]], dtype=dtype),
    )


def test_prod_along_batch_masked_array() -> None:
    assert objects_are_equal(
        prod_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[True, False], [False, False], [True, False], [False, False], [False, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([96, 945]), mask=np.array([[False, False]])),
    )


####################################
#     Tests for prod_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([0, 15120], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[0], [15120]], dtype=dtype),
    )


def test_prod_along_seq_masked_array() -> None:
    assert objects_are_equal(
        prod_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[True, False, False, True, False], [False, False, False, False, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([8, 15120]), mask=np.array([[False], [False]])),
    )


#####################################
#     Tests for sum_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([20, 25], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[20, 25]], dtype=dtype),
    )


def test_sum_along_batch_masked_array() -> None:
    assert objects_are_equal(
        sum_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([8, 25]), mask=np.array([[False, False]])),
    )


###################################
#     Tests for sum_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([10, 35], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[10], [35]], dtype=dtype),
    )


def test_sum_along_seq_masked_array() -> None:
    assert objects_are_equal(
        sum_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, True, False, True], [False, False, False, False, False]]
                ),
            )
        ),
        np.ma.masked_array(data=np.array([4, 35]), mask=np.array([[False], [False]])),
    )
