# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Configurations of objects and parts of it. Only used internally, e.g. by the functionality of :py:mod:`annize.object`.
"""
import dataclasses


def parameter_config(for_type: type, parameter_name: str) -> "ParameterConfig":
    """
    Return a parameter configuration for a given parameter of a given object's constructor.

    :param for_type: The type.
    :param parameter_name: The constructor's parameter name.
    """
    explicit_only = False

    for mro_type in for_type.mro():
        mro_type_ctor = getattr(mro_type, "__init__", mro_type)
        if mro_config := (getattr(mro_type_ctor, "__annize__parameter_configs", None) or {}).get(parameter_name):
            if mro_config.explicit_only is not None:
                explicit_only = mro_config.explicit_only

    return ParameterConfig(explicit_only)


@dataclasses.dataclass(frozen=True)
class ParameterConfig:
    """
    A parameter configuration. It contains additional, Annize-specific configuration for a parameter of an object's
    constructor.

    See :py:func:`parameter_config`.
    """

    #: Whether this parameter is marked as "explicit only". See :py:func:`annize.object.explicit_only`.
    explicit_only: bool


@dataclasses.dataclass
class InnerParameterConfig:
    """
    An inner parameter configuration. Similar to :py:class:`ParameterConfig` but not frozen and with default values.

    Used for keeping configuration data in memory. For usage, see :py:class:`ParameterConfig`.
    """

    explicit_only: bool|None = None
