from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import TYPE_CHECKING, TypeVar

import pytest

from objectory import Registry
from objectory.errors import (
    IncorrectObjectFactoryError,
    InvalidAttributeRegistryError,
    InvalidNameFactoryError,
    UnregisteredObjectFactoryError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


class ClassToRegister:
    def __init__(self, arg1: int, arg2: str = "abc") -> None:
        self.arg1 = arg1
        self.arg2 = arg2

    @classmethod
    def class_method(cls) -> ClassToRegister:
        return cls(arg1=35, arg2="bac")

    @classmethod
    def class_method_with_arg(cls, arg2: str) -> ClassToRegister:
        return cls(arg1=333, arg2=arg2)


def function_to_register(arg1: int, arg2: str = "abc") -> ClassToRegister:
    """Fake function to tests some functions."""
    return ClassToRegister(arg1=arg1, arg2=arg2)


class Foo(ABC):
    @abstractmethod
    def my_function(self) -> None:
        """Abstract method."""


class Bar(Foo): ...


class Baz(Foo):
    def my_function(self) -> None:
        """Implemented empty method."""


class Bing(Bar):
    def my_function(self) -> None:
        """Implemented empty method."""


def func_decor() -> Callable:
    def inner(obj: T) -> T:
        obj._my_value = 1
        return obj

    return inner


####################
#     register     #
####################


def test_register_object_class() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    assert registry._state == {"tests.unit.test_registry.ClassToRegister": ClassToRegister}


def test_register_object_class_with_name() -> None:
    registry = Registry()
    registry.register_object(name="name", obj=ClassToRegister)
    assert registry._state == {"name": ClassToRegister}


def test_register_object_function() -> None:
    registry = Registry()
    registry.register_object(function_to_register)
    assert registry._state == {
        "tests.unit.test_registry.function_to_register": function_to_register
    }


def test_register_object_function_with_name() -> None:
    registry = Registry()
    registry.register_object(name="name", obj=function_to_register)
    assert registry._state == {"name": function_to_register}


def test_register_object_lambda_function() -> None:
    registry = Registry()
    with pytest.raises(
        IncorrectObjectFactoryError, match=r"It is not possible to register a lambda function."
    ):
        # Should fail because it is not possible to register a lambda function.
        registry.register_object(lambda x: x)


def test_register_object_incorrect_name() -> None:
    registry = Registry()
    with pytest.raises(TypeError, match=r"The name has to be a string"):
        # Should fail because name should be a string.
        registry.register_object(ClassToRegister, name=123)


def test_register_object_replace_object() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister, name="name")
    assert registry._state == {"name": ClassToRegister}
    registry.register_object(function_to_register, name="name")
    assert registry._state == {"name": function_to_register}


def test_register_object_replace_subregistry() -> None:
    registry = Registry()
    registry.other.register_object(ClassToRegister)
    with pytest.raises(
        InvalidNameFactoryError, match=r"The name `other` is already used by a sub-registry"
    ):
        # Should fail because the name already exists.
        registry.register_object(function_to_register, name="other")


def test_register_object_duplicate() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister, name="name")
    registry.register_object(ClassToRegister, name="name")
    assert len(registry) == 1


def test_register_class_without_name() -> None:
    registry = Registry()

    @registry.register()
    class ClassToRegister2:
        """Do nothing."""

    assert registry._state == {
        "tests.unit.test_registry.test_register_class_without_name.<locals>.ClassToRegister2": (
            ClassToRegister2
        )
    }


def test_register_class_with_name() -> None:
    registry = Registry()

    @registry.register("name")
    class ClassToRegister2:
        """Do nothing."""

    assert registry._state == {"name": ClassToRegister2}


def test_register_function_without_name() -> None:
    registry = Registry()

    @registry.register()
    def function_to_register2() -> None:
        """Do nothing."""

    assert registry._state == {
        "tests.unit.test_registry.test_register_function_without_name.<locals>.function_to_register2": (
            function_to_register2
        )
    }


def test_register_function_with_name() -> None:
    registry = Registry()

    @registry.register("name")
    def function_to_register2() -> None:
        """Do nothing."""

    assert registry._state == {"name": function_to_register2}


def test_register_function_incorrect_name() -> None:
    registry = Registry()
    with pytest.raises(TypeError, match=r"The name has to be a string"):
        # Should fail because name should be a string.
        @registry.register(123)
        def function_to_register3() -> None:
            """Do nothing."""


def test_register_class_multiple_decorators_1() -> None:
    # The goal is to tests that the decorator `register` does not mask the decorator `func_decor`.
    registry = Registry()

    @registry.register()
    @func_decor()
    class ClassToRegister2: ...

    assert (
        "tests.unit.test_registry.test_register_class_multiple_decorators_1.<locals>.ClassToRegister2"
        in registry._state
    )
    assert len(registry._state) == 1
    assert ClassToRegister2._my_value == 1


def test_register_class_multiple_decorators_2() -> None:
    # The goal is to tests that the decorator `register` does not mask the decorator `func_decor`.
    registry = Registry()

    @func_decor()
    @registry.register()
    class ClassToRegister2: ...

    assert (
        "tests.unit.test_registry.test_register_class_multiple_decorators_2.<locals>.ClassToRegister2"
        in registry._state
    )
    assert len(registry._state) == 1
    assert ClassToRegister2._my_value == 1


def test_get_attribute_new() -> None:
    registry = Registry()
    registry.other.register_object(ClassToRegister)
    assert "other" in registry._state
    assert registry.other._state == {
        "tests.unit.test_registry.ClassToRegister": ClassToRegister,
    }


def test_get_attribute_nested() -> None:
    registry = Registry()
    registry.other.other.register_object(ClassToRegister)
    assert len(registry._state) == 1
    assert "other" in registry._state
    assert len(registry.other._state) == 1
    assert "other" in registry.other._state
    assert registry.other.other._state == {
        "tests.unit.test_registry.ClassToRegister": ClassToRegister,
    }


def test_get_attribute_already_exist() -> None:
    registry = Registry()
    registry.other.register_object(ClassToRegister)
    registry.other.register_object(function_to_register)
    assert len(registry._state) == 1
    assert "other" in registry._state
    assert registry.other._state == {
        "tests.unit.test_registry.ClassToRegister": ClassToRegister,
        "tests.unit.test_registry.function_to_register": function_to_register,
    }


def test_get_attribute_invalid_subregistry() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister, name="other")
    with pytest.raises(
        InvalidAttributeRegistryError,
        match=(
            r"The attribute `other` is not a registry. You can use this function "
            "only to access a Registry object."
        ),
    ):
        # Should fail because other is not a sub-registry.
        registry.other.register_object(ClassToRegister)


def test_register_child_classes_ignore_abstract_foo() -> None:
    registry = Registry()
    registry.register_child_classes(Foo)
    assert registry.registered_names() == {
        "tests.unit.test_registry.Baz",
        "tests.unit.test_registry.Bing",
    }


def test_register_child_classes_ignore_abstract_bar() -> None:
    registry = Registry()
    registry.register_child_classes(Bar)
    assert registry.registered_names() == {"tests.unit.test_registry.Bing"}


def test_register_child_classes_ignore_abstract_bing() -> None:
    registry = Registry()
    registry.register_child_classes(Bing)
    assert registry.registered_names() == {"tests.unit.test_registry.Bing"}


def test_register_child_classes_with_abstract_foo() -> None:
    registry = Registry()
    registry.register_child_classes(Foo, ignore_abstract_class=False)
    assert registry.registered_names() == {
        "tests.unit.test_registry.Bar",
        "tests.unit.test_registry.Baz",
        "tests.unit.test_registry.Bing",
        "tests.unit.test_registry.Foo",
    }


def test_register_child_classes_with_abstract_bar() -> None:
    registry = Registry()
    registry.register_child_classes(Bar, ignore_abstract_class=False)
    assert registry.registered_names() == {
        "tests.unit.test_registry.Bar",
        "tests.unit.test_registry.Bing",
    }


def test_register_child_classes_with_abstract_bing() -> None:
    registry = Registry()
    registry.register_child_classes(Bing, ignore_abstract_class=False)
    assert registry.registered_names() == {"tests.unit.test_registry.Bing"}


###################
#     factory     #
###################


@pytest.mark.parametrize("target", ["ClassToRegister", "tests.unit.test_registry.ClassToRegister"])
def test_factory_class_target(target: str) -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    obj = registry.factory(_target_=target, arg1=6)
    assert isinstance(obj, ClassToRegister)
    assert obj.arg1 == 6


def test_factory_class_target_import() -> None:
    assert isinstance(Registry().factory(_target_="collections.OrderedDict"), OrderedDict)


@pytest.mark.parametrize("arg1", [-1, 1])
@pytest.mark.parametrize("arg2", ["arg2", "cba"])
def test_factory_class_args(arg1: int, arg2: str) -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    obj = registry.factory("tests.unit.test_registry.ClassToRegister", arg1, arg2)
    assert isinstance(obj, ClassToRegister)
    assert obj.arg1 == arg1
    assert obj.arg2 == arg2


@pytest.mark.parametrize("arg1", [-1, 1])
@pytest.mark.parametrize("arg2", ["arg2", "cba"])
def test_factory_class_kwargs(arg1: int, arg2: str) -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    obj = registry.factory(
        _target_="tests.unit.test_registry.ClassToRegister", arg1=arg1, arg2=arg2
    )
    assert isinstance(obj, ClassToRegister)
    assert obj.arg1 == arg1
    assert obj.arg2 == arg2


def test_factory_init_class_method() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    obj = registry.factory("tests.unit.test_registry.ClassToRegister", _init_="class_method")
    assert isinstance(obj, ClassToRegister)
    assert obj.arg1 == 35
    assert obj.arg2 == "bac"


def test_factory_init_class_method_with_arg() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    obj = registry.factory(
        "tests.unit.test_registry.ClassToRegister", "qwe", _init_="class_method_with_arg"
    )
    assert isinstance(obj, ClassToRegister)
    assert obj.arg1 == 333
    assert obj.arg2 == "qwe"


def test_factory_init_class_method_with_kwarg() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    obj = registry.factory(
        "tests.unit.test_registry.ClassToRegister", _init_="class_method_with_arg", arg2="meow"
    )
    assert isinstance(obj, ClassToRegister)
    assert obj.arg1 == 333
    assert obj.arg2 == "meow"


def test_factory_init_not_exist() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    with pytest.raises(
        IncorrectObjectFactoryError, match=r".* does not have `incorrect_init_method` attribute"
    ):
        # Should fail because the init function does not exist.
        registry.factory("tests.unit.test_registry.ClassToRegister", _init_="incorrect_init_method")


def test_factory_init_missing() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    with pytest.raises(IncorrectObjectFactoryError, match=r".* does not have `arg2` attribute"):
        # Should fail because the attribute arg2 is not initialized.
        registry.factory("tests.unit.test_registry.ClassToRegister", _init_="arg2")


def test_factory_duplicate_class_name() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister, name="ClassToRegister")
    registry.register_object(ClassToRegister, name="tests.unit.test_registry.ClassToRegister")
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=r"Unable to create the object `OrderedDict` because it is not registered.",
    ):
        # Should fail because the object name is not unique.
        registry.factory("OrderedDict")


def test_factory_unregistered_incorrect_class_name() -> None:
    registry = Registry()
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=r"Unable to create the object `collections.NotACounter` because it is not registered.",
    ):
        registry.factory("collections.NotACounter")


def test_factory_unregistered_incorrect_package() -> None:
    registry = Registry()
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=(
            r"Unable to create the object `my_incorrect_package.MyClass` "
            "because it is not registered."
        ),
    ):
        registry.factory("my_incorrect_package.MyClass")


@pytest.mark.parametrize(
    "target", ["function_to_register", "tests.unit.test_registry.function_to_register"]
)
def test_factory_function_target(target: str) -> None:
    registry = Registry()
    registry.register_object(function_to_register)
    obj = registry.factory(target, arg1=6)
    assert isinstance(obj, ClassToRegister)
    assert obj.arg1 == 6
    assert obj.arg2 == "abc"


######################
#     unregister     #
######################


def test_clear() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    registry.clear()
    assert registry._state == {}


def test_clear_nested_false() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    registry.other.register_object(ClassToRegister)
    registry.other.other.register_object(ClassToRegister)
    registry_other = registry.other
    registry_other2 = registry.other.other
    registry.clear()
    assert len(registry) == 0
    assert len(registry_other) == 2
    assert len(registry_other2) == 1


def test_clear_nested_true() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    registry.other.register_object(ClassToRegister)
    registry.other.other.register_object(ClassToRegister)
    registry_other = registry.other
    registry_other2 = registry.other.other
    registry.clear(nested=True)
    assert registry._state == {}
    assert registry_other._state == {}
    assert registry_other2._state == {}


def test_unregister_exact_name() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    registry.unregister("tests.unit.test_registry.ClassToRegister")
    assert registry._state == {}


def test_unregister_short_name() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    registry.unregister("ClassToRegister")
    assert registry._state == {}


def test_unregister_missing_object() -> None:
    registry = Registry()
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=r"It is not possible to remove an object which is not registered",
    ):
        # Should fail because the object is not registered.
        registry.unregister("tests.unit.test_registry.ClassToRegister")


##################
#     filter     #
##################


@pytest.mark.parametrize("cls", [ClassToRegister, OrderedDict])
def test_set_class_filter(cls: type) -> None:
    registry = Registry()
    registry.set_class_filter(cls)
    assert registry._filters == {registry._CLASS_FILTER: cls}


def test_set_class_filter_incorrect_object() -> None:
    registry = Registry()
    with pytest.raises(TypeError, match=r"The class filter has to be a class"):
        # Should raise an error because it is not a class or None.
        registry.set_class_filter("abc")


def test_set_class_filter_unset_exist() -> None:
    registry = Registry()
    registry.set_class_filter(ClassToRegister)
    registry.set_class_filter(None)
    assert registry._filters == {}


def test_set_class_filter_unset_do_not_exist() -> None:
    registry = Registry()
    registry.set_class_filter(None)
    assert registry._filters == {}


def test_set_class_filter_register_valid_object() -> None:
    registry = Registry()
    registry.set_class_filter(dict)
    registry.register_object(OrderedDict)
    assert registry._state == {"collections.OrderedDict": OrderedDict}


def test_set_class_filter_register_invalid_object() -> None:
    registry = Registry()
    registry.set_class_filter(dict)
    with pytest.raises(
        IncorrectObjectFactoryError,
        match=r"All the registered objects should inherit builtins.dict class",
    ):
        # Should raise an error because ClassToRegister is not a child class of dict.
        registry.register_object(int)


@pytest.mark.parametrize("nested", [True, False])
def test_clear_filters(nested: bool) -> None:
    registry = Registry()
    registry.set_class_filter(ClassToRegister)
    registry.register_object(ClassToRegister)
    assert registry._filters == {"class_filter": ClassToRegister}
    registry.clear_filters(nested)
    assert registry._filters == {}


def test_clear_filters_nested_false() -> None:
    registry = Registry()
    registry.set_class_filter(ClassToRegister)
    registry.other.set_class_filter(ClassToRegister)
    registry.other.other.set_class_filter(ClassToRegister)
    registry_other = registry.other
    registry_other2 = registry.other.other
    registry.clear_filters()
    assert registry._filters == {}
    assert registry_other._filters == {"class_filter": ClassToRegister}
    assert registry_other2._filters == {"class_filter": ClassToRegister}


def test_clear_filters_nested_true() -> None:
    registry = Registry()
    registry.set_class_filter(ClassToRegister)
    registry.other.set_class_filter(ClassToRegister)
    registry.other.other.set_class_filter(ClassToRegister)
    registry_other = registry.other
    registry_other2 = registry.other.other
    registry.clear_filters(nested=True)
    assert len(registry._filters) == 0
    assert len(registry_other._filters) == 0
    assert len(registry_other2._filters) == 0


#################
#     other     #
#################


def test_registry_len_0() -> None:
    assert len(Registry()) == 0


def test_registry_len_1() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    assert len(registry) == 1


def test_registry_len_2() -> None:
    registry = Registry()
    registry.register_object(ClassToRegister)
    registry.other.register_object(ClassToRegister)
    assert len(registry) == 2


def test_registered_names() -> None:
    registry = Registry()
    registry.register_object(int)
    registry.mapping.register_object(dict)
    assert registry.registered_names() == {"builtins.int", "mapping"}


def test_registered_names_include_registry_false() -> None:
    registry = Registry()
    registry.register_object(int)
    registry.mapping.register_object(dict)
    assert registry.registered_names(include_registry=False) == {"builtins.int"}
