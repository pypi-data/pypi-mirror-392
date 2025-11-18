# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Feature module loader.

See :py:class:`FeatureLoader`.
"""
import abc
import importlib.util
import os
import pkgutil
import sys
import threading
import typing as t


class FeatureLoader(abc.ABC):
    """
    Base class for a Feature module loader.
    """

    @abc.abstractmethod
    def load_feature(self, name: str) -> t.Any|None:
        pass

    @abc.abstractmethod
    def get_all_available_feature_names(self) -> list[str]:
        pass


class DefaultFeatureLoader(FeatureLoader):
    """
    Default Feature module loader.
    """

    _FEATURES_NAMESPACE = "annize.features"
    _COMMON_NAMESPACE_POSTFIX = "common"

    def __init__(self):
        self.__cache = {}
        self.__cachelock = threading.Lock()
        for modulename in list(sys.modules.keys()):
            if modulename.startswith(f"{self._FEATURES_NAMESPACE}."):
                sys.modules.pop(modulename)

    def load_feature(self, name):
        with self.__cachelock:
            result = self.__cache.get(name, None)
            if not result:
                try:
                    self.__cache[name] = result = importlib.import_module(f"{self._FEATURES_NAMESPACE}.{name}")
                except ImportError:
                    result = None
        if hasattr(result, "__path__"):
            result = self.load_feature(f"{name}.{self._COMMON_NAMESPACE_POSTFIX}")
        return result

    def get_all_available_feature_names(self):
        result = self.__find_feature_modules_in_package(self._FEATURES_NAMESPACE)
        result = [_[len(self._FEATURES_NAMESPACE)+1:] for _ in result]
        result = [(_[:-len(self._COMMON_NAMESPACE_POSTFIX)-1]
                   if _.endswith(f".{self._COMMON_NAMESPACE_POSTFIX}") else _) for _ in result]
        return sorted(set(result))

    def __find_feature_modules_in_package(self, package_name: str) -> list[str]:
        result = []

        def add_result(sub_module_name: str) -> None:
            nonlocal result
            result.append(f"{package_name}.{sub_module_name}")
            result += self.__find_feature_modules_in_package(f"{package_name}.{sub_module_name}")

        if (spec := importlib.util.find_spec(package_name)).submodule_search_locations:
            for subpath in spec.submodule_search_locations:
                for subsubname in os.listdir(subpath):
                    if os.path.isdir(f"{subpath}/{subsubname}") and not subsubname.startswith("_"):
                        add_result(subsubname)
            for submod in pkgutil.iter_modules(spec.submodule_search_locations):
                add_result(submod.name)
        return result
