from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from coola import objects_are_allclose, objects_are_equal

from batcharray.computation import MaskedArrayComputationModel
from batcharray.types import SORT_KINDS

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import DTypeLike

    from batcharray.types import SortKind

DTYPES = (np.float64, np.int64)


def test_masked_array_computation_model_eq_true() -> None:
    assert MaskedArrayComputationModel() == MaskedArrayComputationModel()


def test_masked_array_computation_model_eq_false() -> None:
    assert MaskedArrayComputationModel() != "MaskedArrayComputationModel"


def test_masked_array_computation_model_repr() -> None:
    assert repr(MaskedArrayComputationModel()).startswith("MaskedArrayComputationModel(")


def test_masked_array_computation_model_str() -> None:
    assert str(MaskedArrayComputationModel()).startswith("MaskedArrayComputationModel(")


##################
#     argmax     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argmax_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argmax(
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


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argmax_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argmax(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            ),
            axis=1,
        ),
        np.array([4, 3]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argmax_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argmax(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            )
        ),
        np.int64(8),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argmax_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argmax(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            axis=0,
            keepdims=True,
        ),
        np.array([[3, 4]]),
    )


##################
#     argmin     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argmin_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argmin(
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


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argmin_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argmin(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[True, False, True, False, False], [False, False, False, False, False]]
                ),
            ),
            axis=1,
        ),
        np.array([1, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argmin_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argmin(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[True, False, True, False, False], [False, False, False, False, False]]
                ),
            )
        ),
        np.int64(1),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argmin_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argmin(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[True, False], [False, False], [True, False], [False, False], [False, False]]
                ),
            ),
            axis=0,
            keepdims=True,
        ),
        np.array([[1, 0]]),
    )


###################
#     argsort     #
###################


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argsort_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argsort(
            np.ma.masked_array(
                data=np.array(
                    [[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype
                ),
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
        np.array([[0, 1, 0, 2, 2], [2, 2, 1, 0, 1], [1, 0, 2, 1, 0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argsort_axis_0_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argsort(
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
            kind="stable",
        ),
        np.array([[0, 2, 0, 0, 2], [1, 0, 1, 2, 1], [2, 1, 2, 1, 0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argsort_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argsort(
            np.ma.masked_array(
                data=np.array(
                    [[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype
                ),
                mask=np.array(
                    [
                        [False, False, False, False, True],
                        [False, False, False, True, False],
                        [False, False, True, False, False],
                    ]
                ),
            ),
            axis=1,
        ),
        np.array([[0, 2, 3, 1, 4], [1, 0, 2, 4, 3], [0, 1, 4, 3, 2]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argsort_axis_1_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argsort(
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
            axis=1,
            kind="stable",
        ),
        np.array([[2, 3, 0, 1, 4], [0, 4, 1, 2, 3], [4, 1, 0, 3, 2]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argsort_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argsort(
            np.ma.masked_array(
                data=np.array(
                    [[1, 14, 4, 13, 6], [3, 0, 10, 5, 11], [2, 8, 7, 12, 9]], dtype=dtype
                ),
                mask=np.array(
                    [
                        [False, False, False, False, True],
                        [False, False, False, True, False],
                        [False, False, True, False, False],
                    ]
                ),
            )
        ),
        np.array([6, 0, 10, 5, 2, 11, 14, 7, 9, 13, 3, 1, 4, 8, 12]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_argsort_axis_none_stable(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argsort(
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
            kind="stable",
        ),
        np.array([2, 14, 3, 0, 5, 1, 9, 11, 6, 7, 10, 13, 4, 8, 12]),
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_masked_array_computation_model_argsort_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().argsort(
            np.ma.masked_array(
                data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 4, 1, 3, 0]]),
                mask=np.array(
                    [
                        [False, False, False, False, True],
                        [False, False, False, True, False],
                        [False, False, True, False, False],
                    ]
                ),
            ),
            axis=0,
            kind=kind,
        ),
        np.array([[0, 2, 0, 0, 2], [1, 0, 1, 2, 1], [2, 1, 2, 1, 0]]),
    )


#######################
#     concatenate     #
#######################


@pytest.mark.parametrize(
    "arrays",
    [
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ],
        (
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ),
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12]]), mask=np.array([[False, False, True]])
            ),
            np.ma.masked_array(
                data=np.array([[13, 14, 15]]), mask=np.array([[False, False, False]])
            ),
        ],
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(data=np.ones((0, 3), dtype=int)),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ],
    ],
)
def test_masked_array_computation_model_concatenate_axis_0(
    arrays: Sequence[np.ma.MaskedArray],
) -> None:
    out = MaskedArrayComputationModel().concatenate(arrays, axis=0)
    assert objects_are_equal(
        out,
        np.ma.masked_array(
            data=np.array([[0, 1, 2], [4, 5, 6], [10, 11, 12], [13, 14, 15]]),
            mask=np.array(
                [
                    [False, False, False],
                    [False, True, False],
                    [False, False, True],
                    [False, False, False],
                ]
            ),
        ),
    )


@pytest.mark.parametrize(
    "arrays",
    [
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ],
        (
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ),
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11], [13, 14]]),
                mask=np.array([[False, False], [False, False]]),
            ),
            np.ma.masked_array(data=np.array([[12], [15]]), mask=np.array([[True], [False]])),
        ],
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(data=np.ones((2, 0), dtype=int)),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ],
    ],
)
def test_masked_array_computation_model_concatenate_axis_1(
    arrays: Sequence[np.ma.MaskedArray],
) -> None:
    out = MaskedArrayComputationModel().concatenate(arrays, axis=1)
    assert objects_are_equal(
        out,
        np.ma.masked_array(
            data=np.array([[0, 1, 2, 10, 11, 12], [4, 5, 6, 13, 14, 15]]),
            mask=np.array(
                [
                    [False, False, False, False, False, True],
                    [False, True, False, False, False, False],
                ]
            ),
        ),
    )


@pytest.mark.parametrize(
    "arrays",
    [
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ],
        (
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ),
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12]]), mask=np.array([[False, False, True]])
            ),
            np.ma.masked_array(
                data=np.array([[13, 14, 15]]), mask=np.array([[False, False, False]])
            ),
        ],
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(data=np.ones((0, 3), dtype=int)),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ],
    ],
)
def test_masked_array_computation_model_concatenate_axis_none(
    arrays: Sequence[np.ma.MaskedArray],
) -> None:
    out = MaskedArrayComputationModel().concatenate(arrays)
    assert objects_are_equal(
        out,
        np.ma.masked_array(
            data=np.array([0, 1, 2, 4, 5, 6, 10, 11, 12, 13, 14, 15]),
            mask=np.array(
                [
                    False,
                    False,
                    False,
                    False,
                    True,
                    False,
                    False,
                    False,
                    True,
                    False,
                    False,
                    False,
                ]
            ),
        ),
    )


@pytest.mark.parametrize("dtype", [int, float])
def test_masked_array_computation_model_concatenate_dtype(dtype: DTypeLike) -> None:
    out = MaskedArrayComputationModel().concatenate(
        [
            np.ma.masked_array(
                data=np.array([[0, 1, 2], [4, 5, 6]]),
                mask=np.array([[False, False, False], [False, True, False]]),
            ),
            np.ma.masked_array(
                data=np.array([[10, 11, 12], [13, 14, 15]]),
                mask=np.array([[False, False, True], [False, False, False]]),
            ),
        ],
        axis=0,
        dtype=dtype,
    )
    assert objects_are_equal(
        out,
        np.ma.masked_array(
            data=np.array([[0, 1, 2], [4, 5, 6], [10, 11, 12], [13, 14, 15]], dtype=dtype),
            mask=np.array(
                [
                    [False, False, False],
                    [False, True, False],
                    [False, False, True],
                    [False, False, False],
                ]
            ),
        ),
    )


###############
#     max     #
###############


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_max_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        MaskedArrayComputationModel().max(
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


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_max_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        MaskedArrayComputationModel().max(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            ),
            axis=1,
        ),
        np.ma.masked_array(data=np.array([4, 8], dtype=dtype), mask=np.array([[False], [False]])),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_max_axis_none(dtype: DTypeLike) -> None:
    assert (
        MaskedArrayComputationModel().max(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            )
        )
        == 8
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_max_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().max(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            axis=0,
            keepdims=True,
        ),
        np.ma.masked_array(data=np.array([[6, 9]], dtype=dtype), mask=np.array([[False, False]])),
    )


################
#     mean     #
################


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_mean_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        MaskedArrayComputationModel().mean(
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


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_mean_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        MaskedArrayComputationModel().mean(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            ),
            axis=1,
        ),
        np.ma.masked_array(
            data=np.array([2.0, 6.333333333333333]), mask=np.array([[False], [False]])
        ),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_mean_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().mean(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            )
        ),
        np.float64(3.625),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_mean_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().mean(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            axis=0,
            keepdims=True,
        ),
        np.ma.masked_array(
            data=np.array([[2.6666666666666665, 5.0]]), mask=np.array([[False, False]])
        ),
    )


##################
#     median     #
##################


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_median_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().median(
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


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_median_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().median(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            ),
            axis=1,
        ),
        np.ma.masked_array(data=np.array([2.0, 6.0]), mask=np.array([[False], [False]])),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_median_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().median(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            )
        ),
        np.float64(3.5),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_median_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().median(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False], [False, False], [True, False], [False, False], [True, False]]
                ),
            ),
            axis=0,
            keepdims=True,
        ),
        np.ma.masked_array(data=np.array([[2.0, 5.0]]), mask=np.array([[False, False]])),
    )


###############
#     min     #
###############


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_min_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        MaskedArrayComputationModel().min(
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


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_min_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_allclose(
        MaskedArrayComputationModel().min(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [True, False, False, True, False]]
                ),
            ),
            axis=1,
        ),
        np.ma.masked_array(data=np.array([0, 6], dtype=dtype), mask=np.array([[False], [False]])),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_min_axis_none(dtype: DTypeLike) -> None:
    assert (
        MaskedArrayComputationModel().min(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                mask=np.array(
                    [[False, False, False, False, False], [True, False, False, True, False]]
                ),
            )
        )
        == 0
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_min_keepdims_true(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().min(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                mask=np.array(
                    [[True, False], [False, False], [True, False], [False, False], [False, False]]
                ),
            ),
            axis=0,
            keepdims=True,
        ),
        np.ma.masked_array(data=np.array([[2, 1]], dtype=dtype), mask=np.array([[False, False]])),
    )


################
#     sort     #
################


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_sort_axis_0(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().sort(
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


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_sort_axis_1(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().sort(
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
            axis=1,
        ),
        np.ma.masked_array(
            data=np.array([[0, 2, 3, 5, 4], [4, 5, 7, 8, 8], [0, 5, 8, 8, 8]], dtype=dtype),
            mask=np.array(
                [
                    [False, False, False, False, True],
                    [False, False, False, False, True],
                    [False, False, False, False, True],
                ]
            ),
        ),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_masked_array_computation_model_sort_axis_none(dtype: DTypeLike) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().sort(
            np.ma.masked_array(
                data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]], dtype=dtype),
                mask=np.array(
                    [
                        [False, False, False, False, True],
                        [False, False, False, True, False],
                        [False, False, True, False, False],
                    ]
                ),
            )
        ),
        np.ma.masked_array(
            data=np.array([0, 0, 2, 3, 4, 5, 5, 5, 7, 8, 8, 8, 4, 8, 8], dtype=dtype),
            mask=np.array(
                [
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        True,
                        True,
                        True,
                    ],
                ]
            ),
        ),
    )


@pytest.mark.parametrize("kind", SORT_KINDS)
def test_masked_array_computation_model_sort_kind(kind: SortKind) -> None:
    assert objects_are_equal(
        MaskedArrayComputationModel().sort(
            np.ma.masked_array(
                data=np.array([[3, 5, 0, 2, 4], [4, 7, 8, 8, 5], [8, 5, 8, 8, 0]]),
                mask=np.array(
                    [
                        [False, False, False, False, True],
                        [False, False, False, True, False],
                        [False, False, True, False, False],
                    ]
                ),
            ),
            axis=0,
            kind=kind,
        ),
        np.ma.masked_array(
            data=np.array([[3, 5, 0, 2, 0], [4, 5, 8, 8, 5], [8, 7, 8, 8, 4]]),
            mask=np.array(
                [
                    [False, False, False, False, False],
                    [False, False, False, False, False],
                    [False, False, True, True, True],
                ]
            ),
        ),
    )
