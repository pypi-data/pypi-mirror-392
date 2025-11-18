from __future__ import annotations

import numpy as np
from coola import objects_are_equal

from batcharray.array import (
    chunk_along_batch,
    chunk_along_seq,
    select_along_batch,
    select_along_seq,
    slice_along_batch,
    slice_along_seq,
    split_along_batch,
    split_along_seq,
)

#######################################
#     Tests for chunk_along_batch     #
#######################################


def test_chunk_along_batch_chunks_3() -> None:
    assert objects_are_equal(
        chunk_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), chunks=3),
        [
            np.array([[0, 1], [2, 3]]),
            np.array([[4, 5], [6, 7]]),
            np.array([[8, 9]]),
        ],
    )


def test_chunk_along_batch_chunks_5() -> None:
    assert objects_are_equal(
        chunk_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), chunks=5),
        [
            np.array([[0, 1]]),
            np.array([[2, 3]]),
            np.array([[4, 5]]),
            np.array([[6, 7]]),
            np.array([[8, 9]]),
        ],
    )


def test_chunk_along_batch_masked_array() -> None:
    assert objects_are_equal(
        chunk_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [False, True], [False, False], [False, True]]
                ),
            ),
            chunks=3,
        ),
        [
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3]]), mask=np.array([[False, False], [False, False]])
            ),
            np.ma.masked_array(
                data=np.array([[4, 5], [6, 7]]), mask=np.array([[False, True], [False, False]])
            ),
            np.ma.masked_array(data=np.array([[8, 9]]), mask=np.array([[False, True]])),
        ],
    )


#####################################
#     Tests for chunk_along_seq     #
#####################################


def test_chunk_along_seq_chunks_3() -> None:
    assert objects_are_equal(
        chunk_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), chunks=3),
        [
            np.array([[0, 1], [5, 6]]),
            np.array([[2, 3], [7, 8]]),
            np.array([[4], [9]]),
        ],
    )


def test_chunk_along_seq_chunks_5() -> None:
    assert objects_are_equal(
        chunk_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), chunks=5),
        [
            np.array([[0], [5]]),
            np.array([[1], [6]]),
            np.array([[2], [7]]),
            np.array([[3], [8]]),
            np.array([[4], [9]]),
        ],
    )


def test_chunk_along_seq_masked_array() -> None:
    assert objects_are_equal(
        chunk_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            ),
            chunks=3,
        ),
        [
            np.ma.masked_array(
                data=np.array([[0, 1], [5, 6]]), mask=np.array([[False, False], [False, False]])
            ),
            np.ma.masked_array(
                data=np.array([[2, 3], [7, 8]]), mask=np.array([[False, False], [True, False]])
            ),
            np.ma.masked_array(data=np.array([[4], [9]]), mask=np.array([[False], [True]])),
        ],
    )


########################################
#     Tests for select_along_batch     #
########################################


def test_select_along_batch_index_0() -> None:
    assert objects_are_equal(
        select_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), index=0),
        np.array([0, 1]),
    )


def test_select_along_batch_index_2() -> None:
    assert objects_are_equal(
        select_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), index=2),
        np.array([4, 5]),
    )


def test_select_along_batch_masked_array() -> None:
    assert objects_are_equal(
        select_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [False, True], [False, False], [False, True]]
                ),
            ),
            index=2,
        ),
        np.ma.masked_array(data=np.array([4, 5]), mask=np.array([False, True])),
    )


######################################
#     Tests for select_along_seq     #
######################################


def test_select_along_seq_index_0() -> None:
    assert objects_are_equal(
        select_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), index=0),
        np.array([0, 5]),
    )


def test_select_along_seq_index_2() -> None:
    assert objects_are_equal(
        select_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), index=2),
        np.array([2, 7]),
    )


def test_select_along_seq_masked_array() -> None:
    assert objects_are_equal(
        select_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            ),
            index=2,
        ),
        np.ma.masked_array(data=np.array([2, 7]), mask=np.array([False, True])),
    )


#######################################
#     Tests for slice_along_batch     #
#######################################


def test_slice_along_batch() -> None:
    assert objects_are_equal(
        slice_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]])),
        np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
    )


def test_slice_along_batch_start_2() -> None:
    assert objects_are_equal(
        slice_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), start=2),
        np.array([[4, 5], [6, 7], [8, 9]]),
    )


def test_slice_along_batch_stop_3() -> None:
    assert objects_are_equal(
        slice_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), stop=3),
        np.array([[0, 1], [2, 3], [4, 5]]),
    )


def test_slice_along_batch_stop_100() -> None:
    assert objects_are_equal(
        slice_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), stop=100),
        np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
    )


def test_slice_along_batch_step_2() -> None:
    assert objects_are_equal(
        slice_along_batch(np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), step=2),
        np.array([[0, 1], [4, 5], [8, 9]]),
    )


def test_slice_along_batch_start_1_stop_4_step_2() -> None:
    assert objects_are_equal(
        slice_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), start=1, stop=4, step=2
        ),
        np.array([[2, 3], [6, 7]]),
    )


def test_slice_along_batch_masked_array() -> None:
    assert objects_are_equal(
        slice_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [False, True], [False, False], [False, True]]
                ),
            ),
            start=1,
            stop=4,
            step=2,
        ),
        np.ma.masked_array(
            data=np.array([[2, 3], [6, 7]]),
            mask=np.array([[False, False], [False, False]]),
        ),
    )


#####################################
#     Tests for slice_along_seq     #
#####################################


def test_slice_along_seq() -> None:
    assert objects_are_equal(
        slice_along_seq(np.array([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]])),
        np.array([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]),
    )


def test_slice_along_seq_start_2() -> None:
    assert objects_are_equal(
        slice_along_seq(np.array([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]), start=2),
        np.array([[2, 3, 4], [7, 6, 5]]),
    )


def test_slice_along_seq_stop_3() -> None:
    assert objects_are_equal(
        slice_along_seq(np.array([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]), stop=3),
        np.array([[0, 1, 2], [9, 8, 7]]),
    )


def test_slice_along_seq_stop_100() -> None:
    assert objects_are_equal(
        slice_along_seq(np.array([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]), stop=100),
        np.array([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]),
    )


def test_slice_along_seq_step_2() -> None:
    assert objects_are_equal(
        slice_along_seq(np.array([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]), step=2),
        np.array([[0, 2, 4], [9, 7, 5]]),
    )


def test_slice_along_seq_start_1_stop_4_step_2() -> None:
    assert objects_are_equal(
        slice_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), start=1, stop=4, step=2),
        np.array([[1, 3], [6, 8]]),
    )


def test_slice_along_seq_masked_array() -> None:
    assert objects_are_equal(
        slice_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            ),
            start=1,
            stop=4,
            step=2,
        ),
        np.ma.masked_array(
            data=np.array([[1, 3], [6, 8]]), mask=np.array([[False, False], [False, False]])
        ),
    )


#######################################
#     Tests for split_along_batch     #
#######################################


def test_split_along_batch_split_size_1() -> None:
    assert objects_are_equal(
        split_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), split_size_or_sections=1
        ),
        [
            np.array([[0, 1]]),
            np.array([[2, 3]]),
            np.array([[4, 5]]),
            np.array([[6, 7]]),
            np.array([[8, 9]]),
        ],
    )


def test_split_along_batch_split_size_2() -> None:
    assert objects_are_equal(
        split_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), split_size_or_sections=2
        ),
        [
            np.array([[0, 1], [2, 3]]),
            np.array([[4, 5], [6, 7]]),
            np.array([[8, 9]]),
        ],
    )


def test_split_along_batch_split_size_list() -> None:
    assert objects_are_equal(
        split_along_batch(
            np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), split_size_or_sections=[2, 2, 1]
        ),
        [
            np.array([[0, 1], [2, 3]]),
            np.array([[4, 5], [6, 7]]),
            np.array([[8, 9]]),
        ],
    )


def test_split_along_batch_masked_array() -> None:
    assert objects_are_equal(
        split_along_batch(
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                mask=np.array(
                    [[False, False], [False, False], [False, True], [False, False], [False, True]]
                ),
            ),
            split_size_or_sections=2,
        ),
        [
            np.ma.masked_array(
                data=np.array([[0, 1], [2, 3]]), mask=np.array([[False, False], [False, False]])
            ),
            np.ma.masked_array(
                data=np.array([[4, 5], [6, 7]]), mask=np.array([[False, True], [False, False]])
            ),
            np.ma.masked_array(data=np.array([[8, 9]]), mask=np.array([[False, True]])),
        ],
    )


#####################################
#     Tests for split_along_seq     #
#####################################


def test_split_along_seq_split_size_1() -> None:
    assert objects_are_equal(
        split_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), split_size_or_sections=1),
        [
            np.array([[0], [5]]),
            np.array([[1], [6]]),
            np.array([[2], [7]]),
            np.array([[3], [8]]),
            np.array([[4], [9]]),
        ],
    )


def test_split_along_seq_split_size_2() -> None:
    assert objects_are_equal(
        split_along_seq(np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), split_size_or_sections=2),
        [
            np.array([[0, 1], [5, 6]]),
            np.array([[2, 3], [7, 8]]),
            np.array([[4], [9]]),
        ],
    )


def test_split_along_seq_split_size_list() -> None:
    assert objects_are_equal(
        split_along_seq(
            np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), split_size_or_sections=[2, 2, 1]
        ),
        [
            np.array([[0, 1], [5, 6]]),
            np.array([[2, 3], [7, 8]]),
            np.array([[4], [9]]),
        ],
    )


def test_split_along_seq_masked_array() -> None:
    assert objects_are_equal(
        split_along_seq(
            np.ma.masked_array(
                data=np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                mask=np.array(
                    [[False, False, False, False, False], [False, False, True, False, True]]
                ),
            ),
            split_size_or_sections=2,
        ),
        [
            np.ma.masked_array(
                data=np.array([[0, 1], [5, 6]]), mask=np.array([[False, False], [False, False]])
            ),
            np.ma.masked_array(
                data=np.array([[2, 3], [7, 8]]), mask=np.array([[False, False], [True, False]])
            ),
            np.ma.masked_array(data=np.array([[4], [9]]), mask=np.array([[False], [True]])),
        ],
    )
