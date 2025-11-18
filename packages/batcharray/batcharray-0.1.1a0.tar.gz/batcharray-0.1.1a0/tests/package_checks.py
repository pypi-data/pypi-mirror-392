from __future__ import annotations

import logging

import numpy as np
from coola import objects_are_equal

logger = logging.getLogger(__name__)


def check_array() -> None:
    logger.info("Checking batcharray.array package...")

    from batcharray.array import take_along_batch

    assert objects_are_equal(
        take_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), np.array([4, 3, 2, 1, 0])
        ),
        np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
    )


def check_computation() -> None:
    logger.info("Checking batcharray.computation package...")

    from batcharray.computation import concatenate

    assert objects_are_equal(
        concatenate([np.array([[0, 1], [2, 3]]), np.array([[4, 5], [6, 7], [8, 9]])], axis=0),
        np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
    )


def check_nested() -> None:
    logger.info("Checking batcharray.nested package...")

    from batcharray.nested import take_along_batch

    assert objects_are_equal(
        take_along_batch(
            {
                "a": np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": np.array([[5], [4], [3], [2], [1]]),
            },
            np.array([4, 3, 2, 1, 0]),
        ),
        {
            "a": np.array([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
            "b": np.array([[1], [2], [3], [4], [5]]),
        },
    )


def check_recursive() -> None:
    logger.info("Checking batcharray.recursive package...")

    from batcharray.recursive import recursive_apply

    assert objects_are_equal(recursive_apply([1, "abc"], str), ["1", "abc"])


def check_utils() -> None:
    logger.info("Checking batcharray.utils package...")

    from batcharray.utils import bfs_array

    assert objects_are_equal(
        list(bfs_array(["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])])),
        [np.array([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]), np.array([0, 1, 2, 3, 4])],
    )


def main() -> None:
    check_array()
    check_computation()
    check_nested()
    check_recursive()
    check_utils()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
