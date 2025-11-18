from __future__ import annotations

from collections import OrderedDict, deque
from collections.abc import Iterable, Mapping
from typing import Any
from unittest.mock import Mock, patch

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.utils.bfs import (
    ArrayIterator,
    DefaultArrayIterator,
    IterableArrayIterator,
    IteratorState,
    MappingArrayIterator,
    bfs_array,
)


@pytest.fixture
def state() -> IteratorState:
    return IteratorState(iterator=ArrayIterator(), queue=deque())


###############################
#     Tests for bfs_array     #
###############################


def test_bfs_array_array() -> None:
    assert objects_are_equal(list(bfs_array(np.ones((2, 3)))), [np.ones((2, 3))])


@pytest.mark.parametrize(
    "data",
    [
        pytest.param("abc", id="string"),
        pytest.param(42, id="int"),
        pytest.param(4.2, id="float"),
        pytest.param([1, 2, 3], id="list"),
        pytest.param([], id="empty list"),
        pytest.param(("a", "b", "c"), id="tuple"),
        pytest.param((), id="empty tuple"),
        pytest.param({1, 2, 3}, id="set"),
        pytest.param(set(), id="empty set"),
        pytest.param({"key1": 1, "key2": 2, "key3": 3}, id="dict"),
        pytest.param({}, id="empty dict"),
    ],
)
def test_bfs_array_no_array(data: Any) -> None:
    assert objects_are_equal(list(bfs_array(data)), [])


@pytest.mark.parametrize(
    "data",
    [
        pytest.param([np.ones((2, 3)), np.array([0, 1, 2, 3, 4])], id="list with only arrays"),
        pytest.param(
            ["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])],
            id="list with non array objects",
        ),
        pytest.param((np.ones((2, 3)), np.array([0, 1, 2, 3, 4])), id="tuple with only arrays"),
        pytest.param(
            ("abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])),
            id="tuple with non array objects",
        ),
        pytest.param(
            {"key1": np.ones((2, 3)), "key2": np.array([0, 1, 2, 3, 4])}, id="dict with only arrays"
        ),
        pytest.param(
            {"key1": "abc", "key2": np.ones((2, 3)), "key3": 42, "key4": np.array([0, 1, 2, 3, 4])},
            id="dict with non array objects",
        ),
    ],
)
def test_bfs_array_iterable_array(data: Any) -> None:
    assert objects_are_equal(list(bfs_array(data)), [np.ones((2, 3)), np.array([0, 1, 2, 3, 4])])


def test_bfs_array_nested_data() -> None:
    data = [
        {"key1": np.zeros((1, 1, 1)), "key2": np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])},
        np.ones((2, 3)),
        [np.ones(4), np.array([0, -1, -2]), [np.ones(5)]],
        (1, np.array([42.0]), np.zeros(2)),
        np.array([0, 1, 2, 3, 4]),
    ]
    assert objects_are_equal(
        list(bfs_array(data)),
        [
            np.ones((2, 3)),
            np.array([0, 1, 2, 3, 4]),
            np.zeros((1, 1, 1)),
            np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
            np.ones(4),
            np.array([0, -1, -2]),
            np.array([42.0]),
            np.zeros(2),
            np.ones(5),
        ],
    )


##########################################
#     Tests for DefaultArrayIterator     #
##########################################


def test_default_array_iterator_str() -> None:
    assert str(DefaultArrayIterator()).startswith("DefaultArrayIterator(")


def test_default_array_iterator_iterable(state: IteratorState) -> None:
    DefaultArrayIterator().iterate("abc", state)
    assert state.queue == deque()


###########################################
#     Tests for IterableArrayIterator     #
###########################################


def test_iterable_array_iterator_str() -> None:
    assert str(IterableArrayIterator()).startswith("IterableArrayIterator(")


@pytest.mark.parametrize(
    "data",
    [
        pytest.param([], id="empty list"),
        pytest.param((), id="empty tuple"),
        pytest.param(set(), id="empty set"),
        pytest.param(deque(), id="empty deque"),
    ],
)
def test_iterable_array_iterator_iterate_empty(data: Iterable, state: IteratorState) -> None:
    IterableArrayIterator().iterate(data, state)
    assert state.queue == deque()


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])], id="list"),
        pytest.param(deque(["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])]), id="deque"),
        pytest.param(("abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])), id="tuple"),
    ],
)
def test_iterable_array_iterator_iterate(data: Iterable, state: IteratorState) -> None:
    IterableArrayIterator().iterate(data, state)
    assert objects_are_equal(
        list(state.queue), ["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])]
    )


##########################################
#     Tests for MappingArrayIterator     #
##########################################


def test_mapping_array_iterator_str() -> None:
    assert str(MappingArrayIterator()).startswith("MappingArrayIterator(")


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({}, id="empty dict"),
        pytest.param(OrderedDict(), id="empty OrderedDict"),
    ],
)
def test_mapping_array_iterator_iterate_empty(data: Mapping, state: IteratorState) -> None:
    MappingArrayIterator().iterate(data, state)
    assert state.queue == deque()


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {"key1": "abc", "key2": np.ones((2, 3)), "key3": 42, "key4": np.array([0, 1, 2, 3, 4])},
            id="dict",
        ),
        pytest.param(
            OrderedDict(
                {
                    "key1": "abc",
                    "key2": np.ones((2, 3)),
                    "key3": 42,
                    "key4": np.array([0, 1, 2, 3, 4]),
                }
            ),
            id="OrderedDict",
        ),
    ],
)
def test_mapping_array_iterator_iterate(data: Mapping, state: IteratorState) -> None:
    MappingArrayIterator().iterate(data, state)
    assert objects_are_equal(
        list(state.queue), ["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])]
    )


###################################
#     Tests for ArrayIterator     #
###################################


def test_iterator_str() -> None:
    assert str(ArrayIterator()).startswith("ArrayIterator(")


@patch.dict(ArrayIterator.registry, {}, clear=True)
def test_iterator_add_iterator() -> None:
    iterator = ArrayIterator()
    seq_iterator = IterableArrayIterator()
    iterator.add_iterator(list, seq_iterator)
    assert iterator.registry[list] is seq_iterator


@patch.dict(ArrayIterator.registry, {}, clear=True)
def test_iterator_add_iterator_duplicate_exist_ok_true() -> None:
    iterator = ArrayIterator()
    seq_iterator = IterableArrayIterator()
    iterator.add_iterator(list, DefaultArrayIterator())
    iterator.add_iterator(list, seq_iterator, exist_ok=True)
    assert iterator.registry[list] is seq_iterator


@patch.dict(ArrayIterator.registry, {}, clear=True)
def test_iterator_add_iterator_duplicate_exist_ok_false() -> None:
    iterator = ArrayIterator()
    seq_iterator = IterableArrayIterator()
    iterator.add_iterator(list, DefaultArrayIterator())
    with pytest.raises(RuntimeError, match=r"An iterator (.*) is already registered"):
        iterator.add_iterator(list, seq_iterator)


def test_iterator_iterate(state: IteratorState) -> None:
    ArrayIterator().iterate(["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])], state=state)
    assert objects_are_equal(
        list(state.queue), ["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])]
    )


def test_iterator_has_iterator_true() -> None:
    assert ArrayIterator().has_iterator(list)


def test_iterator_has_iterator_false() -> None:
    assert not ArrayIterator().has_iterator(type(None))


def test_iterator_find_iterator_direct() -> None:
    assert isinstance(ArrayIterator().find_iterator(list), IterableArrayIterator)


def test_iterator_find_iterator_indirect() -> None:
    assert isinstance(ArrayIterator().find_iterator(str), DefaultArrayIterator)


def test_iterator_find_iterator_incorrect_type() -> None:
    with pytest.raises(TypeError, match=r"Incorrect data type:"):
        ArrayIterator().find_iterator(Mock(__mro__=[]))


def test_iterator_registry_default() -> None:
    assert len(ArrayIterator.registry) >= 9
    assert isinstance(ArrayIterator.registry[Iterable], IterableArrayIterator)
    assert isinstance(ArrayIterator.registry[Mapping], MappingArrayIterator)
    assert isinstance(ArrayIterator.registry[deque], IterableArrayIterator)
    assert isinstance(ArrayIterator.registry[dict], MappingArrayIterator)
    assert isinstance(ArrayIterator.registry[list], IterableArrayIterator)
    assert isinstance(ArrayIterator.registry[object], DefaultArrayIterator)
    assert isinstance(ArrayIterator.registry[set], IterableArrayIterator)
    assert isinstance(ArrayIterator.registry[str], DefaultArrayIterator)
    assert isinstance(ArrayIterator.registry[tuple], IterableArrayIterator)
