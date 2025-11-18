# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Annize objects.

There is no particular subclass that all Annize objects inherit from! Annize objects can be of arbitrary types (as long
as their constructor has a signature that Annize can deal with).

There are some decorators for optional configuration and finetuning of Annize objects' methods and attributes here.
"""
import annize.object.config
import annize.project.materializer.object_factory


def explicit_only(parameter_name: str):
    """
    Return a decorator function that marks a given parameter as "explicit only", so potential arguments without an
    :code:`arg_name` will never automatically be matched to that parameter.

    Note: For any parameter with a type that already appeared at earlier parameters of the constructor signature, a
    similar effect will occur implicitly, because the materializer would always take the first possible parameter when
    it tries to auto-assign arguments.

    :param parameter_name: The name of the constructor parameter to mark as "explicit only".
    """
    def decorator(func):
        param_configs = func.__annize__parameter_configs = getattr(func, "__annize__parameter_configs", None) or {}
        param_config = param_configs[parameter_name] = (param_configs.get(parameter_name)
                                                        or annize.object.config.InnerParameterConfig())
        param_config.explicit_only = True
        return func

    return decorator
