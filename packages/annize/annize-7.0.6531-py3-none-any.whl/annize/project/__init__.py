# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Annize projects.

See :py:class:`Project`, :py:class:`Node` and also the submodules.
"""
import abc
import copy
import enum
import logging
import sys
import typing as t

import hallyd

import annize.features.base
import annize.project.file_formats
import annize.project.loader

if t.TYPE_CHECKING:
    import annize.project.inspector

_logger = logging.getLogger(__name__)


def load(project_path: hallyd.fs.TInputPath, *,
         inspector: "annize.project.inspector.FullInspector|None" = None) -> "ProjectNode|None":
    """
    Load a project from disk. Return :code:`None` if the given path does not point into an Annize project.

    :param project_path: A path somewhere inside the project to be opened.
    :param inspector: The custom project inspector to use.
    """
    return annize.project.loader.load_project(project_path, inspector=inspector)


def create_new(root_directory: hallyd.fs.TInputPath, subdirectory_name: str = "-meta", *,
               inspector: "annize.project.inspector.FullInspector|None" = None) -> "ProjectNode":
    """
    Create a new Annize project.

    This will create an initial version of the Annize project configuration on disk as well.

    :param root_directory: The project root path.
    :param subdirectory_name: The subdirectory name where to store the Annize configuration files inside the project
                              root directory. This is not arbitrary but must be one of the well known ones!
    :param inspector: The custom project inspector to use.
    """
    root_directory = hallyd.fs.Path(root_directory)
    if annize.project.loader.project_annize_config_main_file(root_directory):
        raise RuntimeError("Annize projects must not contain other Annize projects")
    if subdirectory_name not in annize.project.loader.ANNIZE_CONFIGURATION_DIRECTORY_NAMES:
        raise ValueError(f"invalid subdirectory name: {subdirectory_name}")
    annize_config_directory = hallyd.fs.Path(root_directory, subdirectory_name)

    annize_config_directory.mkdir()
    annize_config_directory("project.xml").write_text(
        f'<a:project xmlns:a="annize" xmlns="annize:base">\n'
        f'    <Data project_name="{annize.features.base.sanitized_project_name(root_directory.name)}"/>\n'
        f'</a:project>\n')
    return load(root_directory, inspector=inspector)


class Node(abc.ABC):
    """
    Nodes are the building blocks of a project.

    They exist in a serialized way in the project files (usually xml), and when the project is loaded to memory (see
    :py:mod:`annize.project.loader`) they are represented by a structure of :code:`Node` instances.

    Each :code:`Node` has various features (see methods and properties of this class), e.g. it can be observed for
    changes. Each node can also have children. This is just a base class for more specific node types, though. See also
    its subclasses in the same module.

    The most relevant subclass in many regards is :py:class:`ObjectNode`.
    """

    def __init__(self):
        self.__parent = None
        self.__children = []
        self.__changed_handlers = []

    def __str__(self):
        return self.description(with_children=False, multiline=False)

    def add_change_handler(self, handler: t.Callable[["ChangeEvent"], None], *, also_watch_children: bool) -> None:
        """
        Add a function that handles changes on this node.

        See also :py:meth:`remove_change_handler`.

        :param handler: The handler function to add.
        :param also_watch_children: Whether this function shall also observe this node's children.
        """
        self.__changed_handlers.append((handler, also_watch_children))

    def remove_change_handler(self, handler: t.Callable[["ChangeEvent"], None]) -> None:
        """
        Remove a change handler function that was added by :py:meth:`add_change_handler` earlier.

        If that function was added multiple times, it will remove all of them. If the function was not added, this will
        do nothing.

        :param handler: The handler function to remove.
        """
        for i, handler_tuple in reversed(list(enumerate(self.__changed_handlers))):
            if handler_tuple[0] == handler:
                self.__changed_handlers.pop(i)

    @property
    def parent(self) -> "Node|None":
        """
        This node's parent node.
        """
        return self.__parent

    @property
    def file(self) -> "FileNode|None":
        """
        The file node that contains this node, or itself for file nodes, or :code:`None` if it is not part of a file
        node.

        This is the same as going :py:attr:`parent` upwards until a file node is reached.
        """
        file_node = self
        while file_node and not isinstance(file_node, FileNode):
            file_node = file_node.parent
        return file_node

    @property
    def project(self) -> "ProjectNode|None":
        """
        The project node that contains this node, or itself for project nodes, or :code:`None` if it is not part of a
        project node.

        This is the same as going :py:attr:`parent` upwards until a project node is reached.
        """
        file_node = self.file
        return file_node.parent if file_node else None

    @property
    def children(self) -> t.Sequence["Node"]:
        """
        This node's child nodes.
        """
        return tuple(self.__children)

    def insert_child(self, i: int, node: "Node") -> None:
        """
        Insert a new child node.

        :param i: The position.
        :param node: The node to insert.
        """
        if node.__parent:
            raise BadStructureError("tried to add a child node that already has a parent")
        for allowed_child_type in self._allowed_child_types():
            if isinstance(node, allowed_child_type):
                break
        else:
            raise BadStructureError(f"unexpected node {node!r}")

        node.__parent = self
        self.__children.insert(i, node)
        self.__changed__child_added(node, i)

    def append_child(self, node: "Node") -> None:
        """
        Append a new child node.

        :param node: The node to append.
        """
        self.insert_child(len(self.__children), node)

    def remove_child(self, node: "Node") -> None:
        """
        Remove a child node.

        If that node is not a child node, it raises a :code:`ValueError`.

        :param node: The node to remove.
        """
        index = self.__children.index(node)
        self.__children.pop(index)
        self.__changed__child_removed(node, index)
        node.__parent = None

    def clone(self) -> "t.Self":
        """
        Clone this node and return that clone.

        The clone is not connected to the original in any way, has no real marshaler (so it cannot be saved) and no
        changed handler and does not contain the undo history of the original. It is typically used for materialization
        or similar runtime purposes.
        """
        result = copy.copy(self)

        self._clone__early(result)
        result.__parent = None
        result.__children = []
        result.__changed_handlers = []

        for child in self.children:
            result.append_child(child.clone())

        self._clone__late(result)
        return result

    def description(self, *, with_children: bool = True, multiline: bool = True) -> str:
        return self.__description(0, with_children, multiline)

    @classmethod
    @abc.abstractmethod
    def _allowed_child_types(cls) -> t.Iterable[type["Node"]]:
        """
        Return a list of node types that this node type allows to have as child nodes.
        """

    def _clone__early(self, new_node: "t.Self") -> None:
        """
        Execute arbitrary steps during an early stage of node cloning.

        :param new_node: The cloned node.
        """

    def _clone__late(self, new_node: "t.Self") -> None:
        """
        Execute arbitrary steps during a late stage of node cloning.

        :param new_node: The cloned node.
        """

    def _property_changed(self, property_name: str, old_value: t.Any) -> None:
        self.__changed__property_changed(self, property_name, old_value, getattr(self, property_name))

    @abc.abstractmethod
    def _str_helper(self) -> t.Iterable[str]:
        return []

    def __description(self, indent: int, with_children: bool, multiline: bool) -> str:
        linesep = "\n" if multiline else "; "
        indent_str = indent * "  "
        details = tuple(self._str_helper())
        result = f"{indent_str}- {type(self).__name__}: {details[0] if details else ''}{linesep}"
        for detail in details[1:]:
            result += f"{indent_str}  {detail}{linesep}"
        if with_children:
            for child in self.children:
                result += child.__description(indent+1, with_children, multiline)
        return result

    def __changed__child_added(self, child_node: "Node", child_position: int) -> None:
        self.__changed__call__handlers(self.ChildAddedEvent(child_node.parent, child_node, child_position))

    def __changed__child_removed(self, child_node: "Node", child_position: int) -> None:
        self.__changed__call__handlers(self.ChildRemovedEvent(child_node.parent, child_node, child_position))

    def __changed__property_changed(self, node: "Node", property_name: str, old_value: t.Any, new_value: t.Any) -> None:
        if old_value != new_value:
            self.__changed__call__handlers(self.PropertyChangedEvent(node, property_name, old_value, new_value))

    def __changed__call__handlers(self, event: "ChangeEvent") -> None:
        for handler, also_watch_children in tuple(self.__changed_handlers):
            if also_watch_children or (self is event.target_node):
                handler(event)
        if self.parent:
            self.parent.__changed__call__handlers(event)

    class ChangeEvent:
        """
        Base class for events on a :py:class:`Node`. See subclasses and :py:meth:`Node.add_change_handler`.
        """

        def __init__(self, target_node: "Node"):
            self.__target_node = target_node

        @property
        def target_node(self) -> "Node":
            """
            The target node this event is about.
            """
            return self.__target_node

    class __ChildrenListChangeEvent(ChangeEvent):
        """
        Base class for events on a :py:class:`Node` that are about changes on the list of children. See subclasses.
        """

        def __init__(self, target_node: "Node", child_node: "Node", child_position: int):
            super().__init__(target_node)
            self.__child_node = child_node
            self.__child_position = child_position

        @property
        def child_node(self) -> "Node":
            """
            The child node this event is about.
            """
            return self.__child_node

        @property
        def child_position(self) -> int:
            """
            The position of the child node in the list of children.
            """
            return self.__child_position

    class ChildAddedEvent(__ChildrenListChangeEvent):
        """
        Node event that occurs when a child node was added.
        """

    class ChildRemovedEvent(__ChildrenListChangeEvent):
        """
        Node event that occurs when a child node was removed.
        """

    class PropertyChangedEvent(ChangeEvent):
        """
        Node event that occurs when a property of a node was changed.
        """

        def __init__(self, target_node: "Node", property_name: str, old_value: t.Any, new_value: t.Any):
            super().__init__(target_node)
            self.__property_name = property_name
            self.__old_value = old_value
            self.__new_value = new_value

        @property
        def property_name(self) -> str:
            """
            The property name.
            """
            return self.__property_name

        @property
        def old_value(self) -> t.Any:
            """
            The old property value.
            """
            return self.__old_value

        @property
        def new_value(self) -> t.Any:
            """
            The new property value.
            """
            return self.__new_value


class ProjectNode(Node):
    """
    An Annize project root node.

    Each project has exactly one root node. It has no parent. Its children are the Annize project configuration files.
    It has no direct serialized representation (or, one could argue, it is the directory that contains these files).
    """

    def __init__(self, annize_config_directory: hallyd.fs.TInputPath):
        super().__init__()
        self.__annize_config_directory = hallyd.fs.Path(annize_config_directory)
        self.__changes = []
        self.__any_old_or_recent_file_nodes = []
        self.__reset_change_history()

    parent: None
    children: t.Sequence["FileNode"]

    @property
    def annize_config_directory(self) -> hallyd.fs.Path:
        """
        The "Annize config directory" of this Annize project.

        This is not the same as the project's "root directory", but a subdirectory like ':code:`-meta`' inside it.
        """
        return self.__annize_config_directory

    def save(self) -> None:
        """
        Store the current state to the Annize project configuration files.
        """
        existing_files = set()

        for file_node in self.children:
            assert isinstance(file_node, annize.project.FileNode)
            file_node.marshaler.save_file_node()
            existing_files.add(file_node.path)

        for old_file in set(_.path for _ in self.__any_old_or_recent_file_nodes).difference(existing_files):
            old_file.remove(not_exist_ok=True)

    def insert_child(self, i, node):
        node.add_change_handler(self.__handle_changed, also_watch_children=True)
        self.__any_old_or_recent_file_nodes.append(node)
        super().insert_child(i, node)
        self.__changes.append(Node.ChildAddedEvent(self, node, i))

    def remove_child(self, node):
        i_child = self.children.index(node)
        super().remove_child(node)
        self.__changes.append(Node.ChildRemovedEvent(self, node, i_child))
        node.remove_change_handler(self.__handle_changed)

    def changes(self, *, since: int = 0, until: int = sys.maxsize) -> t.Sequence["Node.ChangeEvent"]:
        """
        Return all changes that happened to the project, since the moment of loading it or any later point in time, and
        until now or any earlier point in time.

        All timestamp arguments are based on an artificial clock (which basically increases by 1 for each change).
        See also :py:meth:`undo_changes`.

        :param since: The timestamp where to start with returning changes (inclusive).
        :param until: The timestamp where to stop with return changes (non-inclusive).
        """
        return self.__compacted_changes(self.__changes[since:until])

    def undo_changes(self, since: int) -> None:
        """
        Undo all changes that happened to the project since a given point in time.
        Timestamps are based on an artificial clock; see :py:meth:`changes`.

        :param since: The timestamp where to start with undoing changes (inclusive).
        """
        for event in reversed(self.changes(since=since)):
            if not event:
                continue
            if isinstance(event, Node.ChildAddedEvent):
                event.target_node.remove_child(event.child_node)
            elif isinstance(event, Node.ChildRemovedEvent):
                event.target_node.insert_child(event.child_position, event.child_node)
            elif isinstance(event, Node.PropertyChangedEvent):
                setattr(event.target_node, event.property_name, event.old_value)
            else:
                raise RuntimeError(f"invalid type of change event: {event!r}")

    @staticmethod
    def load(project_location: hallyd.fs.TInputPath, *,
             inspector: "annize.project.inspector.FullInspector|None" = None) -> "ProjectNode":
        """
        Load and return a project node for a given Annize project location.

        Do not use it directly. See :py:meth:`annize.project.load`.

        :param project_location: A path to somewhere inside an Annize project.
        :param inspector: The custom project inspector to use.
        """
        import annize.project.inspector as _inspector
        project_annize_config_directory = annize.project.loader.project_annize_config_directory(project_location)
        project = annize.project.file_formats.load_project(project_annize_config_directory,
                                                           inspector=inspector or _inspector.FullInspector())
        project.__reset_change_history()
        return project

    @classmethod
    def _allowed_child_types(cls):
        return FileNode,

    def _clone__early(self, new_node):
        new_node.__reset_change_history()

    def _clone__late(self, new_node):
        new_node.__reset_change_history()

    def _str_helper(self):
        return ()

    def __reset_change_history(self) -> None:
        self.__changes = []

    def __handle_changed(self, event: "Node.ChangeEvent") -> None:
        self.__changes.append(event)

        if not isinstance(event.target_node, ProjectNode):
            marshaler = event.target_node.file.marshaler
            _logger.debug(f"Sending change event {event!r} to marshaler {marshaler}")
            marshaler.add_change(event)

    @staticmethod
    def __compacted_changes(events: t.Sequence["Node.ChangeEvent"]) -> t.Sequence["Node.ChangeEvent|None"]:
        result = []
        i_last = -1
        was_effective = False

        for i_event, event in enumerate(events):
            if not event:
                result.append(None)
            elif (i_last >= 0) and ProjectNode.__is_inverse_of(event, events[i_last]):
                result[i_last] = None
                result.append(None)
                i_last = -1
                was_effective = True
            else:
                result.append(event)
                i_last = i_event

        return ProjectNode.__compacted_changes(result) if was_effective else result

    @staticmethod
    def __is_inverse_of(event_1: Node.ChangeEvent, event_2: Node.ChangeEvent) -> bool:
        if isinstance(event_1, Node.ChildAddedEvent):
            return isinstance(event_2, Node.ChildRemovedEvent) and (event_1.child_node is event_2.child_node)
        elif isinstance(event_1, Node.ChildRemovedEvent):
            return isinstance(event_2, Node.ChildAddedEvent) and (event_1.child_node is event_2.child_node)
        elif isinstance(event_1, Node.PropertyChangedEvent):
            return (isinstance(event_2, Node.PropertyChangedEvent) and (event_1.target_node is event_2.target_node)
                    and (event_1.property_name == event_2.property_name) and (event_1.new_value == event_2.old_value))
        else:
            raise RuntimeError(f"invalid type of change event: {event_1!r}")


class FileNode(Node):
    """
    An Annize project file node.

    Each project has one file node per configuration file. They are the children of the :py:class:`ProjectNode`. The
    children of a file node are mostly of type :py:class:`ObjectNode`, but can also be different ones.
    """

    def __init__(self, path: hallyd.fs.TInputPath, marshaler: "annize.project.file_formats.FileFormat.Marshaler"):
        super().__init__()
        self.__path = hallyd.fs.Path(path)
        self.__marshaler = marshaler

    parent: ProjectNode

    @property
    def path(self) -> hallyd.fs.Path:
        """
        The file path.
        """
        return self.__path

    @property
    def marshaler(self) -> "annize.project.file_formats.FileFormat.Marshaler":
        """
        The marshaler of this file node. Do not use.
        """
        return self.__marshaler

    def _clone__early(self, new_node):
        new_node.__marshaler = annize.project.file_formats.FileFormat.NullMarshaler()

    def _str_helper(self):
        return [str(self.path)]

    @classmethod
    def _allowed_child_types(cls):
        return ArgumentNode, IgnoreUnavailableFeatureNode


class ArgumentNode(Node, abc.ABC):
    """
    Base class for nodes that can be used as an argument, usually in an :py:class:`ObjectNode`.

    See subclasses.
    """

    def __init__(self):
        super().__init__()
        self.__arg_name = None
        self.__name = None
        self.__append_to = None

    @property
    def name(self) -> str|None:
        """
        The name of this argument node.

        Names are used for a few purposes (the documentation will mention that where it is important), but primarily
        you can refer to a named argument with a :py:class:`ReferenceNode` and you can use it for :py:attr:`append_to`.
        """
        return self.__name

    @name.setter
    def name(self, _: str|None):
        old_name, self.__name = self.__name, _
        self._property_changed("name", old_name)

    @property
    def append_to(self) -> str|None:
        """
        The name of another argument node where this argument node gets appended to its children at runtime.

        This essentially makes this argument node appear twice at runtime. It will also be in the place where it was
        defined; just a reference to that argument is created as a result.
        """
        return self.__append_to

    @append_to.setter
    def append_to(self, _: str|None):
        old_append_to, self.__append_to = self.__append_to, _
        self._property_changed("append_to", old_append_to)

    @property
    def arg_name(self) -> str|None:
        """
        The argument name where this argument is associated to in the parent object.

        Valid argument names depend on the type of object that the parent is representing.
        """
        return self.__arg_name

    @arg_name.setter
    def arg_name(self, _: str|None):
        old_arg_name, self.__arg_name = self.__arg_name, _ or None
        self._property_changed("arg_name", old_arg_name)

    def _str_helper(self):
        return (*((f"arg_name: {self.arg_name}",) if self.arg_name else ()),
                *((f"append_to: {self.append_to}",) if self.append_to else ()))


class ObjectNode(ArgumentNode):
    """
    An Annize project object node.

    In a typical Annize project, most nodes are object nodes. Most structure in their project files represent them
    (usually the tags in xml files). All the other node types are basically related to containing object nodes
    (like file nodes or the project root node) or have other support purposes.

    Children are mostly other object nodes, :py:class:`ScalarValueNode` or :py:class:`ReferenceNode`. They are
    associated to a particular parameter name (of the object type) by their :py:attr:`ArgumentNode.arg_name`.
    """

    def __init__(self, feature: str, type_name: str):
        super().__init__()
        self.__feature = feature
        self.__type_name = type_name

    @property
    def feature(self) -> str:
        """
        The Annize Feature name that provides this object.
        """
        return self.__feature

    @property
    def type_name(self) -> str:
        """
        The name of the type of this object.
        """
        return self.__type_name

    def _str_helper(self):
        return f"{self.feature} :: {self.type_name}", *super()._str_helper()

    @classmethod
    def _allowed_child_types(cls):
        return ArgumentNode,


class ScalarValueNode(ArgumentNode):
    """
    An Annize project scalar value node.

    It represents a fixed string value.
    """

    def __init__(self):
        super().__init__()
        self.__value = None

    @property
    def value(self) -> t.Any:
        """
        The string that this node represents.
        """
        return self.__value

    @value.setter
    def value(self, _: t.Any):
        old_value, self.__value = self.__value, _
        self._property_changed("value", old_value)

    def _str_helper(self):
        return self.__shorten(self.value), *super()._str_helper()

    @classmethod
    def _allowed_child_types(cls):
        return ()

    @staticmethod
    def __shorten(obj: t.Any, max_length: int = 100) -> str:
        result = str(obj).replace("\r", "").replace("\n", "\u21b5")
        if len(result) > max_length:
            result = result[:max_length-1] + "\u1801"
        return result


class ReferenceNode(ArgumentNode):
    """
    A reference node.

    This node represents a reference to another argument node (by its :py:attr:`ArgumentNode.name`)
    """

    def __init__(self):
        super().__init__()
        self.__reference_key = None
        self.__on_unresolvable = ReferenceNode.OnUnresolvableAction.FAIL

    @property
    def reference_key(self) -> str|None:
        """
        The name of the node this node references to (or none).
        """
        return self.__reference_key

    @reference_key.setter
    def reference_key(self, _: str|None):
        old_reference_key, self.__reference_key = self.__reference_key, _
        self._property_changed("reference_key", old_reference_key)

    @property
    def on_unresolvable(self) -> "OnUnresolvableAction":
        return self.__on_unresolvable

    @on_unresolvable.setter
    def on_unresolvable(self, _: "OnUnresolvableAction"):
        old_on_unresolvable, self.__on_unresolvable = self.__on_unresolvable, _
        self._property_changed("on_unresolvable", old_on_unresolvable)

    def _str_helper(self):
        return f"name {self.reference_key}", *super()._str_helper()

    @classmethod
    def _allowed_child_types(cls):
        return ()

    class OnUnresolvableAction(enum.Enum):
        FAIL = "fail"
        SKIP = "skip"


class IgnoreUnavailableFeatureNode(Node):
    """
    An Annize project ignore-unavailable-Feature node.
    """

    def __init__(self):
        super().__init__()
        self.__feature = None

    @property
    def feature(self) -> "str":
        """
        The name of the Feature that gets checked by this node. Empty string or :code:`"*"` (the default) means all
        features.
        """
        return self.__feature or "*"

    @feature.setter
    def feature(self, _: "str"):
        old_feature, self.__feature = self.__feature, _
        self._property_changed("feature", old_feature)

    def _str_helper(self):
        return f"Feature {self.feature}", *super()._str_helper()

    @classmethod
    def _allowed_child_types(cls):
        return ()


class FeatureUnavailableError(ModuleNotFoundError):

    def __init__(self, feature_name: str):
        super().__init__(f"no Annize Feature named {feature_name!r}")
        self.feature_name = feature_name


class BadStructureError(ValueError):

    def __init__(self, message: str):
        super().__init__(f"bad project structure: {message}")


class MaterializerError(TypeError):

    def __init__(self, message: str):
        super().__init__(f"unable to materialize project structure: {message}")


class ParserError(ValueError):
    """
    Parsing error like bad input XML.
    """

    def __init__(self, message: str):
        super().__init__(f"unable to parse project definition: {message}")


class UnresolvableReferenceError(MaterializerError):

    def __init__(self, reference_key: str):
        super().__init__(f"reference {reference_key!r} is unresolvable")
        self.reference_key = reference_key
        self.retry_can_help = True
