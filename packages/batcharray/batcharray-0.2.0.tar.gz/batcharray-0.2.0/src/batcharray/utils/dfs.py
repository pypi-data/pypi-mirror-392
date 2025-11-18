r"""Contain code to iterate over the data to find the arrays with a
Depth-First Search (DFS) strategy."""

from __future__ import annotations

__all__ = [
    "ArrayIterator",
    "BaseArrayIterator",
    "DefaultArrayIterator",
    "IterableArrayIterator",
    "MappingArrayIterator",
    "dfs_array",
    "register_default_iterators",
    "register_iterators",
]

import logging
from collections import deque
from collections.abc import Generator, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

import numpy as np
from coola.utils import str_indent, str_mapping

logger = logging.getLogger(__name__)

T = TypeVar("T")


def dfs_array(data: Any) -> Generator[np.ndarray]:
    r"""Implement a Depth-First Search (DFS) iterator over the
    ``np.ndarray``s.

    This function assumes the underlying data has a tree-like
    structure.

    Args:
        data: Specifies the data to iterate on.

    Yields:
        The next ``np.ndarray`` in the data.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from batcharray.utils.dfs import dfs_array
    >>> list(dfs_array(["abc", np.ones((2, 3)), 42, np.array([0, 1, 2, 3, 4])]))
    [array([[1., 1., 1.], [1., 1., 1.]]), array([0, 1, 2, 3, 4])]

    ```
    """
    state = IteratorState(iterator=ArrayIterator())
    yield from state.iterator.iterate(data, state)


@dataclass
class IteratorState:
    r"""Store the current state."""

    iterator: BaseArrayIterator


class BaseArrayIterator(Generic[T]):
    r"""Define the base class to iterate over the data to find the
    arrays with a Depth-First Search (DFS) strategy."""

    def iterate(self, data: T, state: IteratorState) -> Generator[np.ndarray]:
        r"""Iterate over the data and add the items to the queue.

        Args:
            data: Specifies the data to iterate on.
            state: Specifies the current state, which include the
                queue.

        Yields:
            The next ``np.ndarray`` in the data.
        """


class DefaultArrayIterator(BaseArrayIterator[Any]):
    r"""Implement the default array iterator."""

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def iterate(
        self,
        data: Any,
        state: IteratorState,  # noqa: ARG002
    ) -> Generator[np.ndarray]:
        if isinstance(data, np.ndarray):
            yield data


class IterableArrayIterator(BaseArrayIterator[Iterable]):
    r"""Implement the array iterator for iterable objects."""

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def iterate(self, data: Iterable, state: IteratorState) -> Generator[np.ndarray]:
        for item in data:
            yield from state.iterator.iterate(item, state)


class MappingArrayIterator(BaseArrayIterator[Mapping]):
    r"""Implement the array iterator for mapping objects."""

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def iterate(self, data: Mapping, state: IteratorState) -> Generator[np.ndarray]:
        for item in data.values():
            yield from state.iterator.iterate(item, state)


class ArrayIterator(BaseArrayIterator[Any]):
    """Implement an array iterator."""

    registry: ClassVar[dict[type, BaseArrayIterator]] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  {str_indent(str_mapping(self.registry))}\n)"

    @classmethod
    def add_iterator(
        cls, data_type: type, iterator: BaseArrayIterator, exist_ok: bool = False
    ) -> None:
        r"""Add an iterator for a given data type.

        Args:
            data_type: Specifies the data type for this test.
            iterator: Specifies the iterator object.
            exist_ok: If ``False``, ``RuntimeError`` is raised if the
                data type already exists. This parameter should be set
                to ``True`` to overwrite the iterator for a type.

        Raises:
            RuntimeError: if an iterator is already registered for the
                data type and ``exist_ok=False``.

        Example usage:

        ```pycon
        >>> from batcharray.utils.dfs import ArrayIterator, IterableArrayIterator
        >>> ArrayIterator.add_iterator(list, IterableArrayIterator(), exist_ok=True)

        ```
        """
        if data_type in cls.registry and not exist_ok:
            msg = (
                f"An iterator ({cls.registry[data_type]}) is already registered for the data "
                f"type {data_type}. Please use `exist_ok=True` if you want to overwrite the "
                "iterator for this type"
            )
            raise RuntimeError(msg)
        cls.registry[data_type] = iterator

    def iterate(self, data: Iterable, state: IteratorState) -> Generator[np.ndarray]:
        yield from self.find_iterator(type(data)).iterate(data, state)

    @classmethod
    def has_iterator(cls, data_type: type) -> bool:
        r"""Indicate if an iterator is registered for the given data
        type.

        Args:
            data_type: Specifies the data type to check.

        Returns:
            ``True`` if an iterator is registered, otherwise ``False``.

        Example usage:

        ```pycon
        >>> from batcharray.utils.dfs import ArrayIterator
        >>> ArrayIterator.has_iterator(list)
        True
        >>> ArrayIterator.has_iterator(int)
        False

        ```
        """
        return data_type in cls.registry

    @classmethod
    def find_iterator(cls, data_type: Any) -> BaseArrayIterator:
        r"""Find the iterator associated to an object.

        Args:
            data_type: Specifies the data type to get.

        Returns:
            The iterator associated to the data type.

        Example usage:

        ```pycon
        >>> from batcharray.utils.dfs import ArrayIterator
        >>> ArrayIterator.find_iterator(list)
        IterableArrayIterator()

        ```
        """
        for object_type in data_type.__mro__:
            iterator = cls.registry.get(object_type, None)
            if iterator is not None:
                return iterator
        msg = f"Incorrect data type: {data_type}"
        raise TypeError(msg)


def register_iterators(mapping: Mapping[type, BaseArrayIterator]) -> None:
    r"""Register some iterators.

    Args:
        mapping: Specifies the iterators to register.
    """
    for typ, op in mapping.items():
        if not ArrayIterator.has_iterator(typ):  # pragma: no cover
            ArrayIterator.add_iterator(typ, op)


def register_default_iterators() -> None:
    r"""Register some default iterators."""
    default = DefaultArrayIterator()
    iterable = IterableArrayIterator()
    mapping = MappingArrayIterator()
    register_iterators(
        {
            Iterable: iterable,
            Mapping: mapping,
            deque: iterable,
            dict: mapping,
            list: iterable,
            object: default,
            set: iterable,
            str: default,
            tuple: iterable,
        }
    )


register_default_iterators()
