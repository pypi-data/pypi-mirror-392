from __future__ import annotations

import logging
from collections import Counter

import objectory

logger = logging.getLogger(__name__)


def check_abstract_factory() -> None:
    logger.info("Checking abstract factory...")

    class BaseClass(metaclass=objectory.AbstractFactory):
        pass

    class MyClass(BaseClass):
        pass

    obj = BaseClass.factory("MyClass")
    assert isinstance(obj, MyClass)

    counter = BaseClass.factory("collections.Counter", [1, 2, 1, 3])
    assert counter == Counter([1, 2, 1, 3])


def check_factory() -> None:
    logger.info("Checking factory function...")
    counter = objectory.factory("collections.Counter", [1, 2, 1, 3])
    assert counter == Counter([1, 2, 1, 3])


def check_registry() -> None:
    logger.info("Checking Registry...")
    registry = objectory.Registry()

    @registry.register()
    class MyClass: ...

    obj = registry.factory("MyClass")
    assert isinstance(obj, MyClass)

    counter = registry.factory("collections.Counter", [1, 2, 1, 3])
    assert counter == Counter([1, 2, 1, 3])


def main() -> None:
    check_abstract_factory()
    check_factory()
    check_registry()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
