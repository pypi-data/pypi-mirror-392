from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.nested import (
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
from tests.unit.array.test_reduction import DTYPES

if TYPE_CHECKING:
    from numpy.typing import DTypeLike

######################################
#     Tests for amax_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([8, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[8, 9]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            }
        ),
        {"a": np.array([8, 9], dtype=dtype), "b": np.int64(4)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            keepdims=True,
        ),
        {"a": np.array([[8, 9]], dtype=dtype), "b": np.array([4])},
    )


def test_amax_along_batch_nested() -> None:
    assert objects_are_equal(
        amax_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": np.array([4, 3, 2, 1, 0]),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {"a": np.array([8, 9]), "b": np.int64(4), "c": [np.int64(9)]},
    )


####################################
#     Tests for amax_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([4, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[4], [9]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": np.array([4, 9], dtype=dtype), "b": np.array([4])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amax_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            },
            keepdims=True,
        ),
        {"a": np.array([[4], [9]], dtype=dtype), "b": np.array([[4]])},
    )


def test_amax_along_seq_nested() -> None:
    assert objects_are_equal(
        amax_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": np.array([[4, 3, 2, 1, 0]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {"a": np.array([4, 9]), "b": np.array([4]), "c": [np.array([9])]},
    )


######################################
#     Tests for amin_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([0, 1], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[0, 1]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            }
        ),
        {"a": np.array([0, 1], dtype=dtype), "b": np.int64(0)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            keepdims=True,
        ),
        {"a": np.array([[0, 1]], dtype=dtype), "b": np.array([0])},
    )


def test_amin_along_batch_nested() -> None:
    assert objects_are_equal(
        amin_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": np.array([4, 3, 2, 1, 0]),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {"a": np.array([0, 1]), "b": np.int64(0), "c": [np.int64(5)]},
    )


####################################
#     Tests for amin_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([0, 5], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[0], [5]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": np.array([0, 5], dtype=dtype), "b": np.array([0])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        amin_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            },
            keepdims=True,
        ),
        {"a": np.array([[0], [5]], dtype=dtype), "b": np.array([[0]])},
    )


def test_amin_along_seq_nested() -> None:
    assert objects_are_equal(
        amin_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": np.array([[4, 3, 2, 1, 0]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {"a": np.array([0, 5]), "b": np.array([0]), "c": [np.array([5])]},
    )


########################################
#     Tests for argmax_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[4, 4]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            }
        ),
        {"a": np.array([4, 4]), "b": np.int64(0)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            keepdims=True,
        ),
        {"a": np.array([[4, 4]]), "b": np.array([0])},
    )


def test_argmax_along_batch_nested() -> None:
    assert objects_are_equal(
        argmax_along_batch(
            {
                "a": np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": np.array([4, 3, 2, 1, 0]),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {"a": np.array([4, 4]), "b": np.int64(0), "c": [np.int64(4)]},
    )


######################################
#     Tests for argmax_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[4], [4]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": np.array([4, 4]), "b": np.array([0])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmax_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            },
            keepdims=True,
        ),
        {"a": np.array([[4], [4]]), "b": np.array([[0]])},
    )


def test_argmax_along_seq_nested() -> None:
    assert objects_are_equal(
        argmax_along_seq(
            {
                "a": np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": np.array([[4, 3, 2, 1, 0]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {"a": np.array([4, 4]), "b": np.array([0]), "c": [np.array([4])]},
    )


########################################
#     Tests for argmin_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[0, 0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            }
        ),
        {"a": np.array([0, 0]), "b": np.int64(4)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            keepdims=True,
        ),
        {"a": np.array([[0, 0]]), "b": np.array([4])},
    )


def test_argmin_along_batch_nested() -> None:
    assert objects_are_equal(
        argmin_along_batch(
            {
                "a": np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": np.array([4, 3, 2, 1, 0]),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {"a": np.array([0, 0]), "b": np.int64(4), "c": [np.int64(0)]},
    )


######################################
#     Tests for argmin_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[0], [0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": np.array([0, 0]), "b": np.array([4])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        argmin_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            },
            keepdims=True,
        ),
        {"a": np.array([[0], [0]]), "b": np.array([[4]])},
    )


def test_argmin_along_seq_nested() -> None:
    assert objects_are_equal(
        argmin_along_seq(
            {
                "a": np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": np.array([[4, 3, 2, 1, 0]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {"a": np.array([0, 0]), "b": np.array([4]), "c": [np.array([0])]},
    )


#####################################
#     Tests for max_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([8, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[8, 9]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": np.array([8, 9], dtype=dtype),
            "b": np.int64(4),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            keepdims=True,
        ),
        {
            "a": np.array([[8, 9]], dtype=dtype),
            "b": np.array([4]),
        },
    )


def test_max_along_batch_nested() -> None:
    assert objects_are_equal(
        max_along_batch(
            {
                "a": np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": np.array([4, 3, 2, 1, 0]),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": np.array([8.0, 9.0]),
            "b": np.int64(4),
            "c": [np.int64(9)],
        },
    )


###################################
#     Tests for max_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([4, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[4], [9]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[5, 4, 3, 2, 1]]),
            }
        ),
        {
            "a": np.array([4, 9], dtype=dtype),
            "b": np.array([5]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        max_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[5, 4, 3, 2, 1]]),
            },
            keepdims=True,
        ),
        {
            "a": np.array([[4], [9]], dtype=dtype),
            "b": np.array([[5]]),
        },
    )


def test_max_along_seq_nested() -> None:
    assert objects_are_equal(
        max_along_seq(
            {
                "a": np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": np.array([[5, 4, 3, 2, 1]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": np.array([4.0, 9.0]),
            "b": np.array([5]),
            "c": [np.array([9])],
        },
    )


######################################
#     Tests for mean_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_mean_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([4.0, 5.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_mean_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[4.0, 5.0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_mean_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
            }
        ),
        {"a": np.array([4.0, 5.0]), "b": np.float32(2.0)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_mean_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
            },
            keepdims=True,
        ),
        {"a": np.array([[4.0, 5.0]]), "b": np.array([2.0], dtype=np.float32)},
    )


def test_mean_along_batch_nested() -> None:
    assert objects_are_equal(
        mean_along_batch(
            {
                "a": np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
                "c": [np.array([5, 6, 7, 8, 9], dtype=np.float64)],
            }
        ),
        {"a": np.array([4.0, 5.0]), "b": np.float32(2.0), "c": [np.float64(7.0)]},
    )


####################################
#     Tests for mean_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_mean_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([2.0, 7.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_mean_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[2.0], [7.0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_mean_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
            }
        ),
        {"a": np.array([2.0, 7.0]), "b": np.array([2.0], dtype=np.float32)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_mean_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        mean_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
            },
            keepdims=True,
        ),
        {"a": np.array([[2.0], [7.0]]), "b": np.array([[2.0]], dtype=np.float32)},
    )


def test_mean_along_seq_nested() -> None:
    assert objects_are_equal(
        mean_along_seq(
            {
                "a": np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": np.array([[4, 3, 2, 1, 0]], dtype=np.float32),
                "c": [np.array([[5, 6, 7, 8, 9]], dtype=np.float64)],
            }
        ),
        {
            "a": np.array([2.0, 7.0]),
            "b": np.array([2.0], dtype=np.float32),
            "c": [np.array([7.0], dtype=np.float64)],
        },
    )


########################################
#     Tests for median_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([4.0, 5.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[4.0, 5.0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
            }
        ),
        {"a": np.array([4.0, 5.0]), "b": np.float32(2.0)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
            },
            keepdims=True,
        ),
        {"a": np.array([[4.0, 5.0]]), "b": np.array([2.0], dtype=np.float32)},
    )


def test_median_along_batch_nested() -> None:
    assert objects_are_equal(
        median_along_batch(
            {
                "a": np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": np.array([4, 3, 2, 1, 0], dtype=np.float32),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {"a": np.array([4.0, 5.0]), "b": np.float32(2.0), "c": [np.float64(7.0)]},
    )


######################################
#     Tests for median_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([2.0, 7.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[2.0], [7.0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            }
        ),
        {
            "a": np.array([2.0, 7.0]),
            "b": np.array([2.0]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        median_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            },
            keepdims=True,
        ),
        {
            "a": np.array([[2.0], [7.0]]),
            "b": np.array([[2.0]]),
        },
    )


def test_median_along_seq_nested() -> None:
    assert objects_are_equal(
        median_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": np.array([[4, 3, 2, 1, 0]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": np.array([2.0, 7.0]),
            "b": np.array([2.0]),
            "c": [np.array([7.0])],
        },
    )


#####################################
#     Tests for min_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([0, 1], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[0, 1]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": np.array([0, 1], dtype=dtype),
            "b": np.int64(0),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([4, 3, 2, 1, 0]),
            },
            keepdims=True,
        ),
        {
            "a": np.array([[0, 1]], dtype=dtype),
            "b": np.array([0]),
        },
    )


def test_min_along_batch_nested() -> None:
    assert objects_are_equal(
        min_along_batch(
            {
                "a": np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": np.array([4, 3, 2, 1, 0]),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": np.array([0.0, 1.0]),
            "b": np.int64(0),
            "c": [np.int64(5)],
        },
    )


###################################
#     Tests for min_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([0, 5], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[0], [5]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[5, 4, 3, 2, 1]]),
            }
        ),
        {
            "a": np.array([0, 5], dtype=dtype),
            "b": np.array([1]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        min_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[5, 4, 3, 2, 1]]),
            },
            keepdims=True,
        ),
        {
            "a": np.array([[0], [5]], dtype=dtype),
            "b": np.array([[1]]),
        },
    )


def test_min_along_seq_nested() -> None:
    assert objects_are_equal(
        min_along_seq(
            {
                "a": np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": np.array([[5, 4, 3, 2, 1]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": np.array([0.0, 5.0]),
            "b": np.array([1]),
            "c": [np.array([5])],
        },
    )


######################################
#     Tests for prod_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([0, 945], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[0, 945]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([5, 4, 3, 2, 1]),
            }
        ),
        {"a": np.array([0, 945], dtype=dtype), "b": np.int64(120)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([5, 4, 3, 2, 1]),
            },
            keepdims=True,
        ),
        {"a": np.array([[0, 945]], dtype=dtype), "b": np.array([120])},
    )


def test_prod_along_batch_nested() -> None:
    assert objects_are_equal(
        prod_along_batch(
            {
                "a": np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": np.array([5, 4, 3, 2, 1]),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": np.array([0.0, 945.0]),
            "b": np.int64(120),
            "c": [np.int64(15120)],
        },
    )


####################################
#     Tests for prod_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([0, 15120], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[0], [15120]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[5, 4, 3, 2, 1]]),
            }
        ),
        {"a": np.array([0, 15120], dtype=dtype), "b": np.array([120])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        prod_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[5, 4, 3, 2, 1]]),
            },
            keepdims=True,
        ),
        {"a": np.array([[0], [15120]], dtype=dtype), "b": np.array([[120]])},
    )


def test_prod_along_seq_nested() -> None:
    assert objects_are_equal(
        prod_along_seq(
            {
                "a": np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": np.array([[5, 4, 3, 2, 1]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": np.array([0.0, 15120.0]),
            "b": np.array([120]),
            "c": [np.array([15120])],
        },
    )


#####################################
#     Tests for sum_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        np.array([20, 25], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdims=True
        ),
        np.array([[20, 25]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([5, 4, 3, 2, 1]),
            }
        ),
        {"a": np.array([20, 25], dtype=dtype), "b": np.int64(15)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": np.array([5, 4, 3, 2, 1]),
            },
            keepdims=True,
        ),
        {"a": np.array([[20, 25]], dtype=dtype), "b": np.array([15])},
    )


def test_sum_along_batch_nested() -> None:
    assert objects_are_equal(
        sum_along_batch(
            {
                "a": np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": np.array([5, 4, 3, 2, 1]),
                "c": [np.array([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": np.array([20.0, 25.0]),
            "b": np.int64(15),
            "c": [np.int64(35)],
        },
    )


###################################
#     Tests for sum_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.array([10, 35], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_array_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdims=True),
        np.array([[10], [35]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_dict(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": np.array([10, 35], dtype=dtype), "b": np.array([10])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_dict_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        sum_along_seq(
            {
                "a": np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": np.array([[4, 3, 2, 1, 0]]),
            },
            keepdims=True,
        ),
        {"a": np.array([[10], [35]], dtype=dtype), "b": np.array([[10]])},
    )


def test_sum_along_seq_nested() -> None:
    assert objects_are_equal(
        sum_along_seq(
            {
                "a": np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": np.array([[4, 3, 2, 1, 0]]),
                "c": [np.array([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": np.array([10.0, 35.0]),
            "b": np.array([10]),
            "c": [np.array([35])],
        },
    )
