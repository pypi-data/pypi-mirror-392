# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Tasks.
"""
import typing as t


class Task:

    def __init__(self, *, inner_tasks: t.Sequence[t.Callable], is_advanced: bool = False):
        self.__inner_tasks = tuple(inner_tasks)
        self.__is_advanced = is_advanced

    def __call__(self, *args, **kwargs):
        for inner_task in self.__inner_tasks:
            inner_task(*args, **kwargs)

    @property
    def is_advanced(self) -> bool:
        return self.__is_advanced
