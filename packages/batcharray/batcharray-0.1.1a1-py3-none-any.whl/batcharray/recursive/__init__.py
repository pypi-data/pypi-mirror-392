r"""Contain features to easily work on nested objects."""

from __future__ import annotations

__all__ = [
    "ApplyState",
    "AutoApplier",
    "BaseApplier",
    "DefaultApplier",
    "MappingApplier",
    "SequenceApplier",
    "recursive_apply",
]

from batcharray.recursive.auto import AutoApplier
from batcharray.recursive.base import BaseApplier
from batcharray.recursive.default import DefaultApplier
from batcharray.recursive.interface import recursive_apply
from batcharray.recursive.mapping import MappingApplier
from batcharray.recursive.sequence import SequenceApplier
from batcharray.recursive.state import ApplyState
