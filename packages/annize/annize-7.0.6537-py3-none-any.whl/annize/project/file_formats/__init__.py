# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
File formats for Annize configuration files.

See also the submodules.
"""
import abc
import typing as t

import hallyd

import annize.project

if t.TYPE_CHECKING:
    import annize.project.inspector


class FileFormat(abc.ABC):
    """
    A file format for Annize configuration files.
    """

    class Marshaler(abc.ABC):
        """
        Base class for marshalers. A marshaler is responsible for one configuration file (i.e. it is associated to one
        :py:class:`annize.project.FileNode`). It is provided by the :py:class:`FileFormat` implementation when it
        creates file nodes and is responsible for keeping internal structures up-to-date whenever any changes to any
        node (inside that file node) get applied. Based on that, it provides functionality like
        :py:meth:`save_file_node` and others.
        """

        @abc.abstractmethod
        def add_change(self, change: "annize.project.Node.ChangeEvent") -> None:
            """
            Handle a given change, e.g. keep internal data structure up-to-date.
            Called for any change that occurs inside this file node.

            :param change: The change.
            """

        @abc.abstractmethod
        def save_file_node(self) -> None:
            """
            Save this file node back to disk.
            """

        @abc.abstractmethod
        def serialize_node(self, node: "annize.project.ArgumentNode") -> bytes:
            """
            Return a serialized byte string for a given node, e.g. for clipboard operations.

            :param node: The node to serialize.
            """

    class NullMarshaler(Marshaler):
        """
        A marshaler that does nothing.
        It should only be used in particular situations, like for temporarily created nodes.
        """

        def add_change(self, change):
            pass

        def save_file_node(self):
            pass

        def serialize_node(self, node):
            return b""

    @abc.abstractmethod
    def load_file_node(self, file: hallyd.fs.TInputPath,
                       inspector: "annize.project.inspector.FullInspector") -> "annize.project.FileNode":
        """
        Read the given file and return a project file node for it.

        That file node has a marshaler, which keeps track of changes (it gets notified by the infrastructure for each
        change) and is able to save the node back to its file.

        :param file: The file to load.
        :param inspector: The project inspector to use.
        """

    @abc.abstractmethod
    def new_file_node(self, file: hallyd.fs.TInputPath,
                      inspector: "annize.project.inspector.FullInspector") -> "annize.project.FileNode":
        """
        Return a new empty project file node.

        That file node has a marshaler; see :py:meth:`load_file_node`.

        :param file: The new file. It should not exist already.
        :param inspector: The project inspector to use.
        """

    def serialize_node(self, node: "annize.project.ArgumentNode") -> bytes:
        """
        Return a serialized byte string for a node, e.g. for clipboard operations.

        :param node: The node to serialize.
        """
        return node.file.marshaler.serialize_node(node)

    @abc.abstractmethod
    def deserialize_node(self, s: bytes,
                         inspector: "annize.project.inspector.FullInspector") -> "annize.project.ArgumentNode":
        """
        Return a node for a serialized string, e.g. for clipboard operations.

        :param s: The serialized string.
        :param inspector: The project inspector to use.
        """


_formats = {}


def register_file_format(format_name: str) -> t.Callable:
    """
    Return a decorator that registers a file format.

    :param format_name: The format name.
    """
    def decor(format_type: type[FileFormat]):
        _formats[format_name.lower()] = format_type
        return format_type
    return decor


def file_format(format_name: str) -> FileFormat|None:
    """
    Return a file format by its name (or :code:`None` if not available). See also :py:func:`all_file_format_names`.

    :param format_name: The format name. A typical name is :code:`"xml"`.
    """
    format_type = _formats.get(format_name.lower())
    return None if format_type is None else format_type()


def all_file_format_names() -> t.Sequence[str]:
    """
    Return all known file format names.
    """
    return sorted(_formats.keys())


def load_project(project_annize_config_directory: hallyd.fs.TInputPath, *,
                 inspector: "annize.project.inspector.FullInspector") -> "annize.project.ProjectNode":
    """
    Load an Annize project from its configuration directory.

    Do not use it directly. See :py:meth:`annize.project.load`.

    :param project_annize_config_directory: The Annize project configuration directory
    :param inspector: The project inspector to use.
    """
    import annize.project.file_formats.xml as _
    project_annize_config_directory = hallyd.fs.Path(project_annize_config_directory).absolute()

    project_node = annize.project.ProjectNode(project_annize_config_directory)
    for project_file in sorted(project_annize_config_directory.iterdir(), key=lambda _: _.stem):
        if annize.project.loader.is_valid_annize_configuration_file_name(project_file.name):
            project_node.append_child(file_format(project_file.suffix[1:]).load_file_node(project_file, inspector))
    return project_node
