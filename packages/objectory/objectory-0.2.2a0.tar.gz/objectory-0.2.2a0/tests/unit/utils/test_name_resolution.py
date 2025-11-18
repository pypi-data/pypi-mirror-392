from __future__ import annotations

from objectory.utils.name_resolution import find_matches, resolve_name

########################
#     resolve_name     #
########################


def test_resolve_name_no_match() -> None:
    assert resolve_name("OrderedDict", {"collections.Counter", "math.isclose"}) is None


def test_resolve_name_direct_match() -> None:
    assert (
        resolve_name("OrderedDict", {"OrderedDict", "collections.Counter", "math.isclose"})
        == "OrderedDict"
    )


def test_resolve_name_1_match() -> None:
    assert (
        resolve_name(
            "OrderedDict", {"collections.OrderedDict", "collections.Counter", "math.isclose"}
        )
        == "collections.OrderedDict"
    )


def test_resolve_name_2_matches() -> None:
    assert (
        resolve_name(
            "OrderedDict", {"collections.OrderedDict", "typing.OrderedDict", "math.isclose"}
        )
        is None
    )


def test_resolve_name_imported_name() -> None:
    assert (
        resolve_name("objectory.utils.resolve_name", {"math.isclose"})
        == "objectory.utils.name_resolution.resolve_name"
    )


def test_resolve_name_allow_import_false_exist() -> None:
    assert (
        resolve_name("OrderedDict", {"collections.OrderedDict"}, allow_import=False)
        == "collections.OrderedDict"
    )


def test_resolve_name_allow_import_false_missing() -> None:
    assert (
        resolve_name("objectory.utils.resolve_name", {"math.isclose"}, allow_import=False) is None
    )


########################
#     find_matches     #
########################


def test_find_matches_empty() -> None:
    assert find_matches("OrderedDict", set()) == set()


def test_find_matches_no_match() -> None:
    assert find_matches("OrderedDict", {"collections.Counter", "math.isclose"}) == set()


def test_find_matches_1_match() -> None:
    assert find_matches(
        "OrderedDict", {"collections.OrderedDict", "collections.Counter", "math.isclose"}
    ) == {"collections.OrderedDict"}


def test_find_matches_2_matches() -> None:
    assert find_matches(
        "OrderedDict", {"collections.OrderedDict", "typing.OrderedDict", "math.isclose"}
    ) == {"collections.OrderedDict", "typing.OrderedDict"}


def test_find_matches_invalid_query() -> None:
    assert (
        find_matches(
            "collections.abc.OrderedDict",
            {"collections.OrderedDict", "typing.OrderedDict", "math.isclose"},
        )
        == set()
    )
