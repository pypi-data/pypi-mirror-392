from collections.abc import Callable
from functools import partial

import numpy as np
import pytest
from coola import objects_are_equal
from numpy.typing import DTypeLike

from batcharray import nested

DTYPES = [np.float32, np.float64, np.int64]
POINTWISE_FUNCTIONS = [
    (np.abs, nested.abs),
    (partial(np.clip, a_min=2, a_max=None), partial(nested.clip, a_min=2)),
    (partial(np.clip, a_min=None, a_max=6), partial(nested.clip, a_max=6)),
    (partial(np.clip, a_min=2, a_max=6), partial(nested.clip, a_min=2, a_max=6)),
    (np.exp, nested.exp),
    (np.exp2, nested.exp2),
    (np.expm1, nested.expm1),
    (np.log, nested.log),
    (np.log2, nested.log2),
    (np.log10, nested.log10),
    (np.log1p, nested.log1p),
]


@pytest.mark.parametrize("dtype", DTYPES)
@pytest.mark.parametrize("functions", POINTWISE_FUNCTIONS)
def test_pointwise_function_array(dtype: DTypeLike, functions: tuple[Callable, Callable]) -> None:
    np_fn, nested_fn = functions
    array = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype)
    assert objects_are_equal(nested_fn(array), np_fn(array))


@pytest.mark.parametrize("dtype", DTYPES)
@pytest.mark.parametrize("functions", POINTWISE_FUNCTIONS)
def test_pointwise_function_dict(dtype: DTypeLike, functions: tuple[Callable, Callable]) -> None:
    np_fn, nested_fn = functions
    assert objects_are_equal(
        nested_fn(
            {
                "a": np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype),
                "b": np.array([4, 3, 2, 1], dtype=np.float32),
                "c": [np.array([5, 6, 7, 8, 9], dtype=np.float64)],
                "masked": np.ma.masked_array(
                    data=np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]),
                    mask=np.array(
                        [
                            [False, False],
                            [False, False],
                            [False, True],
                            [False, False],
                            [False, True],
                        ]
                    ),
                ),
            },
        ),
        {
            "a": np_fn(np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype)),
            "b": np_fn(np.array([4, 3, 2, 1], dtype=np.float32)),
            "c": [np_fn(np.array([5, 6, 7, 8, 9], dtype=np.float64))],
            "masked": np_fn(
                np.ma.masked_array(
                    data=np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]),
                    mask=np.array(
                        [
                            [False, False],
                            [False, False],
                            [False, True],
                            [False, False],
                            [False, True],
                        ]
                    ),
                )
            ),
        },
    )
