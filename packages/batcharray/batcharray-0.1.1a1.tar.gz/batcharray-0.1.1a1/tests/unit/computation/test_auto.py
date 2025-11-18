from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import numpy as np
import pytest
from coola import objects_are_allclose, objects_are_equal

from batcharray.computation import (
    ArrayComputationModel,
    AutoComputationModel,
    BaseComputationModel,
    MaskedArrayComputationModel,
)
from batcharray.types import SORT_KINDS

if TYPE_CHECKING:
    from numpy.typing import DTypeLike

    from batcharray.types import SortKind

DTYPES = (np.float64, np.int64)

##########################################
#     Tests for AutoComputationModel     #
##########################################


def test_auto_computation_model_repr() -> None:
    assert repr(AutoComputationModel()).startswith("AutoComputationModel(")


def test_auto_computation_model_str() -> None:
    assert str(AutoComputationModel()).startswith("AutoComputationModel(")


@patch.dict(AutoComputationModel.registry, {}, clear=True)
def test_auto_computation_model_add_computation_model() -> None:
    assert len(AutoComputationModel.registry) == 0
    AutoComputationModel.add_computation_model(np.ndarray, ArrayComputationModel())
    assert AutoComputationModel.registry[np.ndarray] == ArrayComputationModel()


@patch.dict(AutoComputationModel.registry, {}, clear=True)
def test_auto_computation_model_add_computation_model_exist_ok_false() -> None:
    assert len(AutoComputationModel.registry) == 0
    AutoComputationModel.add_computation_model(np.ndarray, ArrayComputationModel())
    with pytest.raises(
        RuntimeError, match=r"A computation model .* is already registered for the array type"
    ):
        AutoComputationModel.add_computation_model(np.ndarray, ArrayComputationModel())


@patch.dict(AutoComputationModel.registry, {}, clear=True)
def test_auto_computation_model_add_computation_model_exist_ok_true() -> None:
    assert len(AutoComputationModel.registry) == 0
    AutoComputationModel.add_computation_model(np.ndarray, Mock(spec=BaseComputationModel))
    AutoComputationModel.add_computation_model(np.ndarray, ArrayComputationModel(), exist_ok=True)
    assert AutoComputationModel.registry[np.ndarray] == ArrayComputationModel()


def test_auto_computation_model_has_computation_model_true() -> None:
    assert AutoComputationModel.has_computation_model(np.ndarray)


def test_auto_computation_model_has_computation_model_false() -> None:
    assert not AutoComputationModel.has_computation_model(str)


def test_auto_computation_model_find_computation_model_ndarray() -> None:
    assert AutoComputationModel.find_computation_model(np.ndarray) == ArrayComputationModel()


def test_auto_computation_model_find_computation_model_masked_array() -> None:
    assert (
        AutoComputationModel.find_computation_model(np.ma.MaskedArray)
        == MaskedArrayComputationModel()
    )


def test_auto_computation_model_find_computation_model_missing() -> None:
    with pytest.raises(TypeError, match=r"Incorrect array type:"):
        AutoComputationModel.find_computation_model(str)


def test_auto_computation_model_registered_computation_models() -> None:
    assert len(AutoComputationModel.registry) >= 2
    assert AutoComputationModel.registry[np.ndarray] == ArrayComputationModel()
    assert AutoComputationModel.registry[np.ma.MaskedArray] == MaskedArrayComputationModel()


def test_auto_computation_model_concatenate() -> None:
    out = AutoComputationModel().concatenate(
        [
            np.array([[0, 1, 2], [4, 5, 6]]),
            np.array([[10, 11, 12], [13, 14, 15]]),
        ],
        axis=0,
    )
    assert objects_are_equal(out, np.array([[0, 1, 2], [4, 5, 6], [10, 11, 12], [13, 14, 15]]))


##################
#     argmax     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_argmax_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmax(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_argmax_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmax(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_argmax_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmax(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.int64(9),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_argmax_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmax(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[4, 4]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_argmax_masked_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmax(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            axis=0,
        ),
        np.array([3, 4]),
    )


##################
#     argmin     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_argmin_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmin(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_argmin_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmin(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_argmin_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmin(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.int64(0),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_argmin_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmin(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[0, 0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_argmin_masked_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argmin(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[True, False], [False, False], [True, False], [False, False], [False, False]]
                ),
            ),
            axis=0,
        ),
        np.array([1, 0]),
    )


###################
#     argsort     #
###################


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_argsort_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argsort(
            np.array([[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype), axis=0
        ),
        np.array([[0, 1, 0, 1, 0], [2, 2, 2, 2, 2], [1, 0, 1, 0, 1]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_argsort_axis_0_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argsort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 4, 1, 3, 0]], dtype=dtype),
            axis=0,
            kind="stable",
        ),
        np.array([[0, 2, 0, 0, 2], [1, 0, 2, 2, 0], [2, 1, 1, 1, 1]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_argsort_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argsort(
            np.array([[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype), axis=1
        ),
        np.array([[0, 2, 4, 3, 1], [1, 0, 3, 2, 4], [0, 2, 1, 4, 3]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_argsort_axis_1_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argsort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype),
            axis=1,
            kind="stable",
        ),
        np.array([[2, 3, 0, 4, 1], [0, 4, 1, 2, 3], [4, 1, 0, 2, 3]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_argsort_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argsort(
            np.array([[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype)
        ),
        np.array([6, 0, 10, 5, 2, 8, 4, 12, 11, 14, 7, 9, 13, 3, 1]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_argsort_axis_none_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argsort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype),
            kind="stable",
        ),
        np.array([2, 14, 3, 0, 4, 5, 1, 9, 11, 6, 7, 8, 10, 12, 13]),
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_auto_computation_model_argsort_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        AutoComputationModel().argsort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 4, 1, 3, 0]]), axis=0, kind=kind
        ),
        np.array([[0, 2, 0, 0, 2], [1, 0, 2, 2, 0], [2, 1, 1, 1, 1]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_array_computation_model_argsort_masked_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().argsort(
            np.ma.masked_array(
                data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 4, 1, 3, 0]], dtype=dtype),
                mask=np.array(
                    [
                        [False, False, False, False, True],
                        [False, False, False, True, False],
                        [False, False, True, False, False],
                    ]
                ),
            ),
            axis=0,
        ),
        np.array([[0, 2, 0, 0, 2], [1, 0, 1, 2, 1], [2, 1, 2, 1, 0]]),
    )


###############
#     max     #
###############


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_max_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().max(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([8, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_max_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().max(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([4, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_max_axis_none(dtype: DTypeLike) -> None:
    assert (
        AutoComputationModel().max(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)) == 9
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_max_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().max(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[8, 9]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_max_masked_array(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        AutoComputationModel().max(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            axis=0,
        ),
        np.ma.masked_array(data=np.array([6, 9], dtype=dtype), mask=np.array([False, False])),
    )


################
#     mean     #
################


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_mean_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().mean(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([4.0, 5.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_mean_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().mean(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([2.0, 7.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_mean_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().mean(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.float64(4.5),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_mean_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().mean(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[4.0, 5.0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_mean_masked_array(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        AutoComputationModel().mean(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            axis=0,
        ),
        np.ma.masked_array(data=np.array([2.6666666666666665, 5.0]), mask=np.array([False, False])),
    )


##################
#     median     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_median_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().median(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([4.0, 5.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_median_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().median(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([2.0, 7.0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_median_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().median(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        np.float64(4.5),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_median_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().median(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[4.0, 5.0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_median_masked_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().median(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            axis=0,
        ),
        np.ma.masked_array(data=np.array([2.0, 5.0]), mask=np.array([False, False])),
    )


###############
#     min     #
###############


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_min_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().min(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0
        ),
        np.array([0, 1], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_min_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().min(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), axis=1
        ),
        np.array([0, 5], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_min_axis_none(dtype: DTypeLike) -> None:
    assert (
        AutoComputationModel().min(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)) == 0
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_min_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().min(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), axis=0, keepdims=True
        ),
        np.array([[0, 1]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_min_masked_array(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        AutoComputationModel().min(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[True, False], [False, False], [True, False], [False, False], [False, False]]
                ),
            ),
            axis=0,
        ),
        np.ma.masked_array(data=np.array([2, 1], dtype=dtype), mask=np.array([False, False])),
    )


################
#     sort     #
################


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_sort_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().sort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype), axis=0
        ),
        np.array([[3, 5, 0, 2, 0], [4, 5, 8, 8, 4], [8, 7, 8, 8, 5]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_sort_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().sort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype), axis=1
        ),
        np.array([[0, 2, 3, 4, 5], [4, 5, 7, 8, 8], [0, 5, 8, 8, 8]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_sort_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().sort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype)
        ),
        np.array([0, 0, 2, 3, 4, 4, 5, 5, 5, 7, 8, 8, 8, 8, 8], dtype=dtype),
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_auto_computation_model_sort_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        AutoComputationModel().sort(
            np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]]), axis=0, kind=kind
        ),
        np.array([[3, 5, 0, 2, 0], [4, 5, 8, 8, 4], [8, 7, 8, 8, 5]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_auto_computation_model_sort_masked_array(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        AutoComputationModel().sort(
            np.ma.masked_array(
                data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype),
                mask=np.array(
                    [
                        [False, False, False, False, True],
                        [False, False, False, True, False],
                        [False, False, True, False, False],
                    ]
                ),
            ),
            axis=0,
        ),
        np.ma.masked_array(
            data=np.array([[3, 5, 0, 2, 0], [4, 5, 8, 8, 5], [8, 7, 8, 8, 4]], dtype=dtype),
            mask=np.array(
                [
                    [False, False, False, False, False],
                    [False, False, False, False, False],
                    [False, False, True, True, True],
                ]
            ),
        ),
    )
