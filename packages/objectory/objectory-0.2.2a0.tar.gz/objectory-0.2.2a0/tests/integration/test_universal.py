from __future__ import annotations

from collections import Counter

from objectory import factory

#############################
#     Tests for factory     #
#############################


def test_factory_valid_object() -> None:
    counter = factory("collections.Counter", [1, 2, 1, 3])
    assert isinstance(counter, Counter)
    assert counter.most_common(5) == [(1, 2), (2, 1), (3, 1)]
