from __future__ import annotations

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.recursive import ApplyState, AutoApplier, SequenceApplier


@pytest.fixture
def state() -> ApplyState:
    return ApplyState(applier=AutoApplier())


#####################################
#     Tests for SequenceApplier     #
#####################################


def test_sequence_applier_str() -> None:
    assert str(SequenceApplier()) == "SequenceApplier()"


def test_sequence_applier_apply_str_list(state: ApplyState) -> None:
    assert objects_are_equal(SequenceApplier().apply([1, "abc"], str, state), ["1", "abc"])


def test_sequence_applier_apply_str_tuple(state: ApplyState) -> None:
    assert objects_are_equal(SequenceApplier().apply((1, "abc"), str, state), ("1", "abc"))


def test_sequence_applier_apply_str_set(state: ApplyState) -> None:
    assert objects_are_equal(SequenceApplier().apply({1, "abc"}, str, state), {"1", "abc"})


def test_sequence_applier_apply_array(state: ApplyState) -> None:
    assert objects_are_equal(
        SequenceApplier().apply(
            [np.ones((2, 3)), np.ones(2), [np.ones((2, 1))]],
            lambda array: array.shape,
            state,
        ),
        [(2, 3), (2,), [(2, 1)]],
    )
