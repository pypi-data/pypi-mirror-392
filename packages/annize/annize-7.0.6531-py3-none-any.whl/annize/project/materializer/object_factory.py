# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Creation of objects. See :py:func:`create_object`.
"""
import dataclasses
import typing as t

import annize.object.config
import annize.project.inspector


class _CreateObjectHelper:

    @staticmethod
    def create_object(of_type: type, args: t.Iterable, kwargs: dict):
        args, kwargs = tuple(args), dict(kwargs)

        inspector = annize.project.inspector.BasicInspector()
        parameter_info = inspector.parameter_info(of_type)
        args, kwargs = _CreateObjectHelper.__fill_empty_lists(parameter_info, args, kwargs)
        args, kwargs = _CreateObjectHelper.__shift_args_to_kwargs(of_type, inspector, args, kwargs)
        args, kwargs = _CreateObjectHelper.__fill_unspecified_optionals(parameter_info, args, kwargs)

        if args:
            raise TypeError(f"unable to assign argument {args[0]!r} to one of the keyword parameters")

        return of_type(*args, **kwargs)

    @staticmethod
    def __fill_empty_lists(parameter_info, args, kwargs):
        for param_name, param_type_info in parameter_info.items():
            if param_type_info.allows_multiple_args and (param_name not in kwargs):
                kwargs[param_name] = []

        return args, kwargs

    @staticmethod
    def __shift_args_to_kwargs(of_type, inspector, args, kwargs):
        args_new = []

        for arg in args:
            possible_argument_infos = inspector.possible_argument_infos_for_child_in_parent(type(arg), of_type)

            if len(possible_argument_infos) > 0:
                arg_name, arg_type_info = possible_argument_infos[0]
                _CreateObjectHelper.__put_item_into_kwargs(arg, kwargs, arg_name, arg_type_info)
            else:
                args_new.append(arg)

        return args_new, kwargs

    @staticmethod
    def __fill_unspecified_optionals(parameter_info, args, kwargs):
        for param_name, param_type_info in parameter_info.items():
            if param_type_info.is_optional and (param_name not in kwargs):
                kwargs[param_name] = None

        return args, kwargs

    @staticmethod
    def __put_item_into_kwargs(arg, kwargs, kwarg_name, param_type_info):
        if param_type_info.allows_multiple_args:
            kwargs[kwarg_name].append(arg)
        else:
            if kwarg_name in kwargs:
                raise MultipleValuesForSingleArgumentError(kwarg_name)
            kwargs[kwarg_name] = arg


create_object = _CreateObjectHelper.create_object


class MultipleValuesForSingleArgumentError(TypeError):

    def __init__(self, arg_name: str):
        super().__init__(f"more than one value given for the single-value argument {arg_name!r}")
        self.arg_name = arg_name
