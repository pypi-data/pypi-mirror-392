# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project base information.
"""
import datetime
import string
import typing as t

import annize.flow.run_context
import annize.data
import annize.fs
import annize.features.files
import annize.i18n
import annize.project.loader


class Data:

    def __init__(self, *, project_name: str = None,
                 pretty_project_name: annize.i18n.TrStr|None = None,
                 summary: annize.i18n.TrStr|None = None,
                 long_description: annize.i18n.TrStr|None = None,
                 homepage_url: str|None = None,
                 project_directory: str|None = None):
        if (project_name is not None) and project_name != sanitized_project_name(project_name):
            raise ValueError(f"invalid project_name: {project_name}")
        self.__project_name = project_name
        self.__pretty_project_name = pretty_project_name
        self.__summary = summary
        self.__long_description = long_description
        self.__homepage_url = homepage_url
        self.__project_directory = project_directory

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def pretty_project_name(self) -> annize.i18n.TrStr:
        return self.__pretty_project_name

    @property
    def summary(self) -> annize.i18n.TrStr:
        return self.__summary

    @property
    def long_description(self) -> annize.i18n.TrStr:
        return self.__long_description

    @property
    def homepage_url(self) -> str:
        return self.__homepage_url

    @property
    def project_directory(self) -> str:
        return self.__project_directory


class DateTime(datetime.datetime):

    def __new__(cls, *, iso: str):
        return datetime.datetime.fromisoformat(iso)


class Basket(annize.data.Basket):

    def __init__(self, *, items: list[object]):
        super().__init__(items)


class FirstOf(annize.data.Basket):

    def __init__(self, *, objects: list[object]):
        super().__init__(objects[:1])


def _get_data(key: str, default: t.Any) -> t.Any:
    result = default
    for obj in annize.flow.run_context.objects_by_type(Data):
        value = getattr(obj, key)
        if value:
            result = value
            break
    return result


def project_name() -> str:
    return _get_data("project_name", "")


def pretty_project_name() -> annize.i18n.TrStr:
    return _get_data("pretty_project_name", project_name())


def summary() -> annize.i18n.TrStr:
    return _get_data("summary", "")


def long_description() -> annize.i18n.TrStr:
    return _get_data("long_description", "")


def homepage_url() -> str:
    return _get_data("homepage_url", "")


def project_directory() -> annize.fs.Path:
    annize_config_directory = annize.fs.Path(annize.flow.run_context.object_by_name(
        annize.flow.run_context.RunContext.ANNIZE_CONFIG_DIRECTORY__NAME))

    result = _get_data("project_directory", None)
    if not result:
        result = annize.project.loader.project_root_directory(annize_config_directory)
    result = annize.fs.Path(result)
    if not result.is_absolute():
        result = annize_config_directory.parent(result)
    return result


_project_name_allowed_characters = tuple((*string.ascii_letters, *string.digits, *"+,-._"))
def sanitized_project_name(name: str) -> str:
    result = ""
    for character in name:
        if character not in _project_name_allowed_characters:
            character = "_"
        result += character
    return result
