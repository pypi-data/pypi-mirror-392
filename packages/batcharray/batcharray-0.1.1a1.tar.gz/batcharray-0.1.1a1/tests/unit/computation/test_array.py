from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.computation import ArrayComputationModel
from batcharray.types import SORT_KINDS

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import DTypeLike

    from batcharray.types import SortKind

DTYPES = (np.float64, np.int64)


def test_array_computation_model_eq_true() -> None:
    assert ArrayComputationModel() == ArrayComputationModel()


def test_array_computation_model_eq_false() -> None:
    assert ArrayComputationModel() != "ArrayComputationModel"


def test_array_computation_model_repr() -> None:
    assert repr(ArrayComputationModel()).startswith("ArrayComputationModel(")


def test_array_computation_model_str() -> None:
    assert str(ArrayComputationModel()).startswith("ArrayComputationModel(")


##################
#     argmax     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argmax_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argmax(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argmax_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argmax(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argmax_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argmax(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.int64(9),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argmax_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argmax(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[4, 4]]),
    )


##################
#     argmin     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argmin_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argmin(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argmin_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argmin(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argmin_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argmin(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.int64(0),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argmin_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argmin(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[0, 0]]),
    )


###################
#     argsort     #
###################


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argsort_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argsort(
            np.array([[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype), axis=0
        ),
        np.array([[0, 1, 0, 1, 0], [2, 2, 2, 2, 2], [1, 0, 1, 0, 1]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argsort_axis_0_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argsort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 4, 1, 3, 0]], dtype=dtype),
            axis=0,
            kind="stable",
        ),
        np.array([[0, 2, 0, 0, 2], [1, 0, 2, 2, 0], [2, 1, 1, 1, 1]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argsort_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argsort(
            np.array([[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype), axis=1
        ),
        np.array([[0, 2, 4, 3, 1], [1, 0, 3, 2, 4], [0, 2, 1, 4, 3]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argsort_axis_1_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argsort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype),
            axis=1,
            kind="stable",
        ),
        np.array([[2, 3, 0, 4, 1], [0, 4, 1, 2, 3], [4, 1, 0, 2, 3]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argsort_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argsort(
            np.array([[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype)
        ),
        np.array([6, 0, 10, 5, 2, 8, 4, 12, 11, 14, 7, 9, 13, 3, 1]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_argsort_axis_none_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argsort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype),
            kind="stable",
        ),
        np.array([2, 14, 3, 0, 4, 5, 1, 9, 11, 6, 7, 8, 10, 12, 13]),
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_array_computation_model_argsort_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        ArrayComputationModel().argsort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 4, 1, 3, 0]]), axis=0, kind=kind
        ),
        np.array([[0, 2, 0, 0, 2], [1, 0, 2, 2, 0], [2, 1, 1, 1, 1]]),
    )


#######################
#     concatenate     #
#######################


@pytest.mark.parametrize(
    "arrays",
    [
        [np.array([[0, 1, 2], [4, 5, 6]]), np.array([[10, 11, 12], [13, 14, 15]])],
        (np.array([[0, 1, 2], [4, 5, 6]]), np.array([[10, 11, 12], [13, 14, 15]])),
        [
            np.array([[0, 1, 2], [4, 5, 6]]),
            np.array([[10, 11, 12]]),
            np.array([[13, 14, 15]]),
        ],
        [
            np.array([[0, 1, 2], [4, 5, 6]]),
            np.ones((0, 3), dtype=int),
            np.array([[10, 11, 12], [13, 14, 15]]),
        ],
    ],
)
def test_array_computation_model_concatenate_axis_0(arrays: Sequence[np.ndarray]) -> None:
    out = ArrayComputationModel().concatenate(arrays, axis=0)
    assert objects_are_equal(out, np.array([[0, 1, 2], [4, 5, 6], [10, 11, 12], [13, 14, 15]]))


@pytest.mark.parametrize(
    "arrays",
    [
        [np.array([[0, 1, 2], [4, 5, 6]]), np.array([[10, 11, 12], [13, 14, 15]])],
        (np.array([[0, 1, 2], [4, 5, 6]]), np.array([[10, 11, 12], [13, 14, 15]])),
        [
            np.array([[0, 1, 2], [4, 5, 6]]),
            np.array([[10, 11], [13, 14]]),
            np.array([[12], [15]]),
        ],
        [
            np.array([[0, 1, 2], [4, 5, 6]]),
            np.ones((2, 0), dtype=int),
            np.array([[10, 11, 12], [13, 14, 15]]),
        ],
    ],
)
def test_array_computation_model_concatenate_axis_1(arrays: Sequence[np.ndarray]) -> None:
    out = ArrayComputationModel().concatenate(arrays, axis=1)
    assert objects_are_equal(out, np.array([[0, 1, 2, 10, 11, 12], [4, 5, 6, 13, 14, 15]]))


@pytest.mark.parametrize(
    "arrays",
    [
        [np.array([[0, 1, 2], [4, 5, 6]]), np.array([[10, 11, 12], [13, 14, 15]])],
        (np.array([[0, 1, 2], [4, 5, 6]]), np.array([[10, 11, 12], [13, 14, 15]])),
        [
            np.array([[0, 1, 2], [4, 5, 6]]),
            np.array([[10, 11, 12]]),
            np.array([[13, 14, 15]]),
        ],
        [
            np.array([[0, 1, 2], [4, 5, 6]]),
            np.ones((0, 3), dtype=int),
            np.array([[10, 11, 12], [13, 14, 15]]),
        ],
    ],
)
def test_array_computation_model_concatenate_axis_none(arrays: Sequence[np.ndarray]) -> None:
    out = ArrayComputationModel().concatenate(arrays)
    assert objects_are_equal(out, np.array([0, 1, 2, 4, 5, 6, 10, 11, 12, 13, 14, 15]))


@pytest.mark.parametrize("dtype", [int, float])
def test_array_computation_model_concatenate_dtype(dtype: DTypeLike) -> None:
    out = ArrayComputationModel().concatenate(
        [
            np.array([[0, 1, 2], [4, 5, 6]]),
            np.array([[10, 11, 12], [13, 14, 15]]),
        ],
        axis=0,
        dtype=dtype,
    )
    assert objects_are_equal(
        out, np.array([[0, 1, 2], [4, 5, 6], [10, 11, 12], [13, 14, 15]], dtype=dtype)
    )


###############
#     max     #
###############


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_max_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().max(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([8, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_max_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().max(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([4, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_max_axis_none(dtype: DTypeLike) -> None:
    assert (
        ArrayComputationModel().max(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype))
        == 9.0
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_max_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().max(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[8, 9]], dtype=dtype),
    )


################
#     mean     #
################


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_mean_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().mean(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([4.0, 5.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_mean_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().mean(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([2.0, 7.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_mean_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().mean(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.float64(4.5),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_mean_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().mean(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[4.0, 5.0]]),
    )


##################
#     median     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_median_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().median(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([4.0, 5.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_median_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().median(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([2.0, 7.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_median_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().median(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.float64(4.5),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_median_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().median(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[4.0, 5.0]]),
    )


###############
#     min     #
###############


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_min_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().min(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([0, 1], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_min_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().min(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([0, 5], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_min_axis_none(dtype: DTypeLike) -> None:
    assert (
        ArrayComputationModel().min(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)) == 0
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_min_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().min(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[0, 1]], dtype=dtype),
    )


################
#     sort     #
################


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_sort_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().sort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype), axis=0
        ),
        np.array([[3, 5, 0, 2, 0], [4, 5, 8, 8, 4], [8, 7, 8, 8, 5]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_sort_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().sort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype), axis=1
        ),
        np.array([[0, 2, 3, 4, 5], [4, 5, 7, 8, 8], [0, 5, 8, 8, 8]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_array_computation_model_sort_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        ArrayComputationModel().sort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype)
        ),
        np.array([0, 0, 2, 3, 4, 4, 5, 5, 5, 7, 8, 8, 8, 8, 8], dtype=dtype),
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_array_computation_model_sort_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        ArrayComputationModel().sort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]]), axis=0, kind=kind
        ),
        np.array([[3, 5, 0, 2, 0], [4, 5, 8, 8, 4], [8, 7, 8, 8, 5]]),
    )
