from collections.abc import Callable

import numpy as np
import pytest
from coola import objects_are_allclose
from numpy.typing import DTypeLike

from batcharray import nested

DTYPES = [np.float32, np.float64, np.int64]
POINTWISE_FUNCTIONS = [
    (np.arccos, nested.arccos),
    (np.arccosh, nested.arccosh),
    (np.arcsin, nested.arcsin),
    (np.arcsinh, nested.arcsinh),
    (np.arctan, nested.arctan),
    (np.arctanh, nested.arctanh),
    (np.cos, nested.cos),
    (np.cosh, nested.cosh),
    (np.sin, nested.sin),
    (np.sinh, nested.sinh),
    (np.tan, nested.tan),
    (np.tanh, nested.tanh),
]


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.parametrize("dtype", DTYPES)
@pytest.mark.parametrize("functions", POINTWISE_FUNCTIONS)
def test_trigo_array(dtype: DTypeLike, functions: tuple[Callable, Callable]) -> None:
    np_fn, nested_fn = functions
    rng = np.random.default_rng()
    array = rng.normal(size=(5, 2)).astype(dtype=dtype)
    assert objects_are_allclose(nested_fn(array), np_fn(array), equal_nan=True)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.parametrize("dtype", DTYPES)
@pytest.mark.parametrize("functions", POINTWISE_FUNCTIONS)
def test_trigo_dict(dtype: DTypeLike, functions: tuple[Callable, Callable]) -> None:
    np_fn, nested_fn = functions
    assert objects_are_allclose(
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
        equal_nan=True,
    )
