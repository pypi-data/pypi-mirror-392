r"""Contain the main features of the ``objectory`` package."""

from __future__ import annotations

__all__ = ["OBJECT_INIT", "OBJECT_TARGET", "AbstractFactory", "Registry", "factory"]

from objectory.abstract_factory import AbstractFactory
from objectory.constants import OBJECT_INIT, OBJECT_TARGET
from objectory.registry import Registry
from objectory.universal import factory
