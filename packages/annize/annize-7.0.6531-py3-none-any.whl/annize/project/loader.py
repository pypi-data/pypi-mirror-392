# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Loading Annize projects from disk.

See also :py:func:`load_project`.
"""
import typing as t

import hallyd

import annize.i18n
import annize.project
import annize.user_feedback

if t.TYPE_CHECKING:
    import annize.project.inspector


def load_project(project_location: hallyd.fs.TInputPath, *,
                 inspector: "annize.project.inspector.FullInspector|None" = None) -> "annize.project.ProjectNode|None":
    """
    Load a project from disk. Return :code:`None` if the given path does not lead to a location inside an Annize
    project.

    Do not use it directly. See :py:meth:`annize.project.load`.

    :param project_location: A path to somewhere inside an Annize project.
    :param inspector: The custom project inspector to use.
    """
    if annize_config_directory := project_annize_config_directory(project_location):
        return annize.project.ProjectNode.load(annize_config_directory)
    return None


def project_annize_config_main_file(project_location: hallyd.fs.TInputPath) -> hallyd.fs.Path|None:
    """
    Return the main configuration file for an Annize project given by a path (the path may point to somewhere inside
    the project; not only inside the Annize configuration directory), or :code:`None` if the given path does not lead
    to a location inside an Annize project.

    This is a file with a name like :file:`project.xml`.

    :param project_location: A location somewhere inside the Annize project.
    """
    current_location = hallyd.fs.Path(project_location)

    while current_location and current_location.exists():
        for possible_annize_configuration_directory_name in ANNIZE_CONFIGURATION_DIRECTORY_NAMES:
            if (possible_annize_config_main_file := current_location(
                    possible_annize_configuration_directory_name, "project.xml")).is_file(follow_symlinks=False):
                return possible_annize_config_main_file
        if current_location == current_location.parent:
            break
        current_location = current_location.parent

    return None


def project_annize_config_directory(project_location: hallyd.fs.TInputPath) -> hallyd.fs.Path|None:
    """
    Return the configuration directory for an Annize project given by a path (the path may point to somewhere inside
    the project; not only inside the Annize configuration directory), or :code:`None` if the given path does not lead
    to a location inside an Annize project.

    This is a directory with a name like :file:`-meta` (or another name in
    :py:data:`ANNIZE_CONFIGURATION_DIRECTORY_NAMES`).

    :param project_location: A location somewhere inside the Annize project.
    """
    if project_annize_config_main_file_ := project_annize_config_main_file(project_location):
        return project_annize_config_main_file_.parent
    return None


def project_root_directory(project_location: hallyd.fs.TInputPath) -> hallyd.fs.Path|None:
    """
    Return the project root directory for an Annize project given by a path (the path may point to somewhere inside
    the project; not only inside the Annize configuration directory), or :code:`None` if the given path does not lead
    to a location inside an Annize project.

    This is a directory with a subdirectory like :file:`-meta` (or another name in
    :py:data:`ANNIZE_CONFIGURATION_DIRECTORY_NAMES`).

    :param project_location: A location somewhere inside the Annize project.
    """
    if project_annize_config_directory_ := project_annize_config_directory(project_location):
        return project_annize_config_directory_.parent
    return None


def is_valid_annize_configuration_file_name(name: str) -> bool:
    """
    Return whether a given name is a valid Annize configuration file name.

    :param name: The file name to check.
    """
    bare_name = name.rpartition(".")[0]
    return bare_name and (bare_name == ANNIZE_CONFIGURATION_FILE_NAME_PREFIX
                          or bare_name.startswith(f"{ANNIZE_CONFIGURATION_FILE_NAME_PREFIX}."))


ANNIZE_CONFIGURATION_DIRECTORY_NAMES = tuple(f"{prefix}{name}"
                                             for prefix in ("-", ".", "=", "_", "~", "")
                                             for name in ("annize", "meta"))

ANNIZE_CONFIGURATION_FILE_NAME_PREFIX = "project"
