from __future__ import annotations

from collections import OrderedDict

import numpy as np
import pytest
from coola import objects_are_equal

from batcharray.recursive import ApplyState, AutoApplier, MappingApplier


@pytest.fixture
def state() -> ApplyState:
    return ApplyState(applier=AutoApplier())


####################################
#     Tests for MappingApplier     #
####################################


def test_mapping_applier_str() -> None:
    assert str(MappingApplier()) == "MappingApplier()"


def test_mapping_applier_apply_str(state: ApplyState) -> None:
    assert objects_are_equal(
        MappingApplier().apply({"a": 1, "b": "abc"}, str, state), {"a": "1", "b": "abc"}
    )


def test_mapping_applier_apply_array(state: ApplyState) -> None:
    assert objects_are_equal(
        MappingApplier().apply(
            {"a": np.ones((2, 3)), "b": np.ones(2), "c": {"d": np.ones((2, 1))}},
            lambda array: array.shape,
            state,
        ),
        {"a": (2, 3), "b": (2,), "c": {"d": (2, 1)}},
    )


def test_mapping_applier_apply_ordered_dict(state: ApplyState) -> None:
    assert objects_are_equal(
        MappingApplier().apply(OrderedDict({"a": 1, "b": "abc"}), str, state),
        OrderedDict({"a": "1", "b": "abc"}),
    )
