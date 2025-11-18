from __future__ import annotations

import collections
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar

import pytest

from objectory.abstract_factory import (
    AbstractFactory,
    is_abstract_factory,
    register,
    register_child_classes,
)
from objectory.errors import (
    AbstractClassFactoryError,
    AbstractFactoryTypeError,
    IncorrectObjectFactoryError,
    UnregisteredObjectFactoryError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")

# Define some classes to register them in the AbstractFactory metaclass.


class BaseClass(metaclass=AbstractFactory):
    pass


class BaseClassWithArgument(metaclass=AbstractFactory):
    def __init__(self, arg1: int) -> None:
        self.arg1 = arg1


class ChildClass(BaseClassWithArgument):
    """Child class of ``BaseClassWithArgument``."""


class AbstractChildClass(ABC, BaseClassWithArgument):
    """Abstract child class."""

    @abstractmethod
    def method(self) -> None:
        """Abstract method."""


class Class1(metaclass=AbstractFactory):
    def __init__(self, arg2: int, arg3: int = 0) -> None:
        self.arg2 = arg2
        self.arg3 = arg3


class Class2(Class1):
    pass


class Class3(Class2):
    @classmethod
    def class_method(cls) -> Class3:
        return cls(arg2=111, arg3=222)

    @classmethod
    def class_method_with_arg(cls, arg3: int) -> Class3:
        return cls(arg2=333, arg3=arg3)


class Foo(ABC):
    @abstractmethod
    def my_method(self) -> None:
        """Abstract method."""


class Bar(Foo): ...


class Baz(Foo):
    def my_method(self) -> None:
        """Implement an empty method."""


class Bing(Bar):
    def my_method(self) -> None:
        """Implement an empty method."""


class ClassToRegister:
    pass


def function_to_register(arg2: int, arg3: int) -> Class1:
    return Class1(arg2, arg3)


def func_decor() -> Callable:
    def inner(obj: T) -> T:
        obj._my_value = 1
        return obj

    return inner


def reset_base_class() -> None:
    BaseClass.inheritors.clear()
    BaseClass.register_object(BaseClass)
    assert len(BaseClass.inheritors) == 1


def reset_base_class_with_argument() -> None:
    BaseClassWithArgument.inheritors.clear()
    BaseClassWithArgument.register_object(BaseClassWithArgument)
    BaseClassWithArgument.register_object(ChildClass)
    BaseClassWithArgument.register_object(AbstractChildClass)
    assert len(BaseClassWithArgument.inheritors) == 3


def reset_class1() -> None:
    Class1.inheritors.clear()
    Class1.register_object(Class1)
    Class1.register_object(Class2)
    Class1.register_object(Class3)
    assert len(Class1.inheritors) == 3


@pytest.fixture(autouse=True)
def _reset_factory() -> None:
    reset_base_class()
    reset_base_class_with_argument()
    reset_class1()


def test_inheritors() -> None:
    assert len(BaseClassWithArgument.inheritors) == 3
    assert BaseClassWithArgument.inheritors == {
        "tests.unit.test_abstract_factory.BaseClassWithArgument": BaseClassWithArgument,
        "tests.unit.test_abstract_factory.ChildClass": ChildClass,
        "tests.unit.test_abstract_factory.AbstractChildClass": AbstractChildClass,
    }


###################
#     factory     #
###################


@pytest.mark.parametrize("target", ["BaseClass", "tests.unit.test_abstract_factory.BaseClass"])
def test_factory_target(target: str) -> None:
    obj = BaseClass.factory(target)
    assert isinstance(obj, BaseClass)


def test_factory_args() -> None:
    obj = BaseClassWithArgument.factory("ChildClass", 42)
    assert obj.arg1 == 42
    assert isinstance(obj, BaseClassWithArgument)
    assert isinstance(obj, ChildClass)


def test_factory_kwargs() -> None:
    obj = BaseClassWithArgument.factory("ChildClass", arg1=42)
    assert obj.arg1 == 42
    assert isinstance(obj, BaseClassWithArgument)
    assert isinstance(obj, ChildClass)


def test_factory_grand_child() -> None:
    obj = Class1.factory("Class3", 42)
    assert obj.arg2 == 42
    assert obj.arg3 == 0
    assert isinstance(obj, Class1)
    assert isinstance(obj, Class2)
    assert isinstance(obj, Class3)


def test_factory_grand_parent() -> None:
    obj = Class3.factory("Class1", 42)
    assert obj.arg2 == 42
    assert obj.arg3 == 0
    assert isinstance(obj, Class1)
    assert not isinstance(obj, Class2)
    assert not isinstance(obj, Class3)


def test_factory_init_class_method() -> None:
    obj = Class1.factory("Class3", _init_="class_method")
    assert obj.arg2 == 111
    assert obj.arg3 == 222
    assert isinstance(obj, Class3)


def test_factory_init_class_method_with_arg() -> None:
    obj = Class1.factory("Class3", 1, _init_="class_method_with_arg")
    assert obj.arg2 == 333
    assert obj.arg3 == 1
    assert isinstance(obj, Class3)


def test_factory_init_class_method_with_kwarg() -> None:
    obj = Class1.factory("Class3", _init_="class_method_with_arg", arg3=2)
    assert obj.arg2 == 333
    assert obj.arg3 == 2
    assert isinstance(obj, Class3)


def test_factory_init_not_exist() -> None:
    with pytest.raises(
        IncorrectObjectFactoryError, match=r".* does not have `incorrect_init_method` attribute"
    ):
        # Should fail because the init function does not exist.
        Class1.factory("Class3", _init_="incorrect_init_method")


def test_factory_init_missing() -> None:
    with pytest.raises(IncorrectObjectFactoryError, match=r".* does not have `arg2` attribute"):
        # Should fail because the attribute arg2 is not initialized.
        Class1.factory("Class3", _init_="arg2")


def test_factory_duplicate_class_name() -> None:
    BaseClass.register_object(collections.Counter)

    class Counter:
        pass

    BaseClass.register_object(Counter)
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=r"Unable to create the object `Counter` because it is not registered.",
    ):
        # Should fail because the class name Counter is not unique.
        BaseClass.factory("Counter")


def test_factory_unregistered_class() -> None:
    obj = Class1.factory("collections.Counter")
    assert isinstance(obj, collections.Counter)
    assert "collections.Counter" in Class1.inheritors


def test_factory_unregistered_incorrect_class_name() -> None:
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=r"Unable to create the object `collections.NotACounter` because it is not registered.",
    ):
        Class1.factory("collections.NotACounter")


def test_factory_unregistered_incorrect_package() -> None:
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=(
            r"Unable to create the object `my_incorrect_package.MyClass` "
            "because it is not registered."
        ),
    ):
        Class1.factory("my_incorrect_package.MyClass")


@pytest.mark.parametrize(
    "target", ["function_to_register", "tests.unit.test_abstract_factory.function_to_register"]
)
def test_factory_function_target(target: str) -> None:
    Class1.register_object(function_to_register)
    obj = Class1.factory(target, 42, 11)
    assert isinstance(obj, Class1)
    assert obj.arg2 == 42
    assert obj.arg3 == 11


####################
#     register     #
####################


def test_register_object_class() -> None:
    Class1.register_object(ClassToRegister)
    assert Class1.inheritors == {
        "tests.unit.test_abstract_factory.Class1": Class1,
        "tests.unit.test_abstract_factory.Class2": Class2,
        "tests.unit.test_abstract_factory.Class3": Class3,
        "tests.unit.test_abstract_factory.ClassToRegister": ClassToRegister,
    }


def test_register_object_duplicate_class(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(level=logging.INFO):
        Class1.register_object(Class2)
        assert Class1.inheritors == {
            "tests.unit.test_abstract_factory.Class1": Class1,
            "tests.unit.test_abstract_factory.Class2": Class2,
            "tests.unit.test_abstract_factory.Class3": Class3,
        }
        assert caplog.messages == []


def test_register_object_function() -> None:
    Class1.register_object(function_to_register)
    assert Class1.inheritors == {
        "tests.unit.test_abstract_factory.Class1": Class1,
        "tests.unit.test_abstract_factory.Class2": Class2,
        "tests.unit.test_abstract_factory.Class3": Class3,
        "tests.unit.test_abstract_factory.function_to_register": function_to_register,
    }
    obj = Class1.factory("tests.unit.test_abstract_factory.function_to_register", arg2=42, arg3=11)
    assert obj.arg2 == 42
    assert obj.arg3 == 11
    assert isinstance(obj, Class1)


def test_register_object_function_duplicate(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(level=logging.INFO):

        def function_to_register2() -> None:
            return 1

        Class1.register_object(function_to_register2)

        def function_to_register2() -> None:
            return 2

        Class1.register_object(function_to_register2)
        assert len(caplog.messages) == 1


def test_register_object_lambda_function() -> None:
    with pytest.raises(
        IncorrectObjectFactoryError, match=r"It is not possible to register a lambda function."
    ):
        # Should fail because it is not possible to register a lambda function.
        Class1.register_object(lambda x: x)


def test_register_object_incorrect_type() -> None:
    with pytest.raises(
        IncorrectObjectFactoryError, match=r"It is possible to register only a class or a function"
    ):
        # Should fail because it is only possible to register a class or a function.
        Class1.register_object("abc")


def test_decorator_register_function() -> None:
    @register(Class1)
    def my_method_to_register(arg1: int, arg2: int) -> Class1:
        return Class1(arg1, arg2)

    function_name = "test_decorator_register_function.<locals>.my_method_to_register"
    function_path = f"tests.unit.test_abstract_factory.{function_name}"
    assert Class1.inheritors == {
        "tests.unit.test_abstract_factory.Class1": Class1,
        "tests.unit.test_abstract_factory.Class2": Class2,
        "tests.unit.test_abstract_factory.Class3": Class3,
        function_path: my_method_to_register,
    }
    obj = Class1.factory(function_path, 42, 11)
    assert obj.arg2 == 42
    assert obj.arg3 == 11
    assert isinstance(obj, Class1)


def test_decorator_register_class() -> None:
    @register(BaseClass)
    class MyClass:
        def __init__(self, arg: int) -> None:
            self.arg = arg

    assert (
        "tests.unit.test_abstract_factory.test_decorator_register_class.<locals>.MyClass"
        in BaseClass.inheritors
    )
    obj = BaseClass.factory(
        "tests.unit.test_abstract_factory.test_decorator_register_class.<locals>.MyClass", 42
    )
    assert obj.arg == 42


def test_register_object_multiple_decorators_1() -> None:
    # The goal is to tests that the decorator `register` does not mask the decorator `func_decor`.
    @register(BaseClass)
    @func_decor()
    def my_func() -> None:
        """Do nothing."""

    assert (
        "tests.unit.test_abstract_factory.test_register_object_multiple_decorators_1.<locals>.my_func"
        in BaseClass.inheritors
    )
    assert my_func._my_value == 1


def test_register_object_multiple_decorators_2() -> None:
    # The goal is to tests that the decorator `register` does not mask the decorator `func_decor`.
    @func_decor()
    @register(BaseClass)
    def my_func() -> None:
        """Do nothing."""

    assert (
        "tests.unit.test_abstract_factory.test_register_object_multiple_decorators_2.<locals>.my_func"
        in BaseClass.inheritors
    )
    assert my_func._my_value == 1


def test_factory_fails_to_instantiate_abstract_class() -> None:
    with pytest.raises(
        AbstractClassFactoryError,
        match=r"Cannot instantiate the class .* because it is an abstract class.",
    ):
        BaseClassWithArgument.factory("AbstractChildClass")


def test_factory_fails_to_instantiate_unregistered_class() -> None:
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=r"Unable to create the object `Class1` because it is not registered.",
    ):
        BaseClassWithArgument.factory("Class1")


def test_register_incorrect_object() -> None:
    with pytest.raises(
        IncorrectObjectFactoryError, match=r"It is possible to register only a class or a function"
    ):
        Class1.register_object(None)


def test_multiple_register() -> None:
    @register(Class1)
    @register(BaseClassWithArgument)
    class MyClass(BaseClass):
        """Do nothing."""

    assert (
        "tests.unit.test_abstract_factory.test_multiple_register.<locals>.MyClass"
        in BaseClass.inheritors
    )
    assert (
        "tests.unit.test_abstract_factory.test_multiple_register.<locals>.MyClass"
        in BaseClassWithArgument.inheritors
    )
    assert (
        "tests.unit.test_abstract_factory.test_multiple_register.<locals>.MyClass"
        in Class1.inheritors
    )


#################################
#     register_child_classes    #
#################################


def test_register_child_classes_ignore_abstract_foo() -> None:
    register_child_classes(BaseClass, Foo)
    assert "tests.unit.test_abstract_factory.Baz" in BaseClass.inheritors
    assert "tests.unit.test_abstract_factory.Bing" in BaseClass.inheritors


def test_register_child_classes_ignore_abstract_bar() -> None:
    register_child_classes(BaseClass, Bar)
    assert "tests.unit.test_abstract_factory.Bing" in BaseClass.inheritors


def test_register_child_classes_ignore_abstract_bing() -> None:
    register_child_classes(BaseClass, Bing)
    assert "tests.unit.test_abstract_factory.Bing" in BaseClass.inheritors


def test_register_child_classes_with_abstract_foo() -> None:
    register_child_classes(BaseClass, Foo, ignore_abstract_class=False)
    assert "tests.unit.test_abstract_factory.Bar" in BaseClass.inheritors
    assert "tests.unit.test_abstract_factory.Baz" in BaseClass.inheritors
    assert "tests.unit.test_abstract_factory.Bing" in BaseClass.inheritors
    assert "tests.unit.test_abstract_factory.Foo" in BaseClass.inheritors


def test_register_child_classes_with_abstract_bar() -> None:
    register_child_classes(BaseClass, Bar, ignore_abstract_class=False)
    assert "tests.unit.test_abstract_factory.Bar" in BaseClass.inheritors
    assert "tests.unit.test_abstract_factory.Bing" in BaseClass.inheritors


def test_register_child_classes_with_abstract_bing() -> None:
    register_child_classes(BaseClass, Bing, ignore_abstract_class=False)
    assert "tests.unit.test_abstract_factory.Bing" in BaseClass.inheritors


def test_register_child_classes_incorrect_factory_class() -> None:
    with pytest.raises(
        AbstractFactoryTypeError,
        match=(
            r"It is not possible to register child classes because the factory class does "
            "not implement the AbstractFactory metaclass"
        ),
    ):
        register_child_classes(ClassToRegister, ClassToRegister)


######################
#     unregister     #
######################


def test_unregister_exact_name() -> None:
    Class1.unregister("tests.unit.test_abstract_factory.Class3")
    assert Class1.inheritors == {
        "tests.unit.test_abstract_factory.Class1": Class1,
        "tests.unit.test_abstract_factory.Class2": Class2,
    }


def test_unregister_short_name() -> None:
    Class1.unregister("Class3")
    assert Class1.inheritors == {
        "tests.unit.test_abstract_factory.Class1": Class1,
        "tests.unit.test_abstract_factory.Class2": Class2,
    }


def test_unregister_missing_object() -> None:
    with pytest.raises(
        UnregisteredObjectFactoryError,
        match=r"It is not possible to remove an object which is not registered",
    ):
        Class1.unregister("Class4")


###############################
#     is_abstract_factory     #
###############################


def test_is_abstract_factory_true() -> None:
    assert is_abstract_factory(Class1)
    assert is_abstract_factory(Class2)
    assert is_abstract_factory(Class3)


def test_is_abstract_factory_false() -> None:
    assert not is_abstract_factory(ClassToRegister)


def test_is_abstract_factory_false_function() -> None:
    assert not is_abstract_factory(function_to_register)
