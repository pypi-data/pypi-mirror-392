from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter

import pytest

from objectory import factory
from objectory.errors import AbstractClassFactoryError


class BaseFakeClass(ABC):
    @abstractmethod
    def method(self) -> None:
        """Abstract method."""


#############################
#     Tests for factory     #
#############################


def test_factory_valid_object() -> None:
    counter = factory("collections.Counter", [1, 2, 1, 3])
    assert isinstance(counter, Counter)
    assert counter.most_common(5) == [(1, 2), (2, 1), (3, 1)]


def test_factory_abstract_object() -> None:
    with pytest.raises(
        AbstractClassFactoryError,
        match=r"Cannot instantiate the class .* because it is an abstract class.",
    ):
        factory("tests.unit.test_universal.BaseFakeClass")


def test_factory_non_existing_object() -> None:
    with pytest.raises(RuntimeError, match=r"The target object does not exist:"):
        factory("collections.NotACounter")
