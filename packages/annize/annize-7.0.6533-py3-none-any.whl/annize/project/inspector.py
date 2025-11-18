# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project inspector.

See :py:class:`FullInspector`.
"""
import abc
import builtins
import enum
import importlib
import inspect
import logging
import traceback
import types
import typing as t

import annize.i18n
import annize.object.config
import annize.project.feature_loader


_logger = logging.getLogger(__name__)


class BasicInspector:
    """
    Project inspectors are used in order to get various additional metadata about parts of a project, which are needed
    e.g. for project parsing and materialization or project configuration UIs.

    This inspector type has restricted functionality, but has no dependencies and so is simple to instantiate.
    See also :py:class:`FullInspector`.
    """

    def type_info(self, for_type: type) -> "BasicInspector.TypeInfo":
        """
        Return basic type information for a given type, e.g. whether it is a scalar or list and whether it is optional.

        :param for_type: The type to gather information for.
        """
        return self.__type_info(for_type)

    def parameter_info(self, for_type: t.Callable) -> t.Mapping[str, "BasicInspector.TypeInfo"]:
        """
        For a given type, return a mapping with type information for each of its constructor's keyword parameters.
        If it has a parameter for variable keyword arguments, it assumes that these refer to parameters of a superclass
        constructor and inspects them as well.

        It will always contain each keyword parameter, even the ones without type annotation.

        For some special types, like :code:`enum.Enum` subclasses, it returns a different mapping, which the
        materializer will understand when instantiating these objects!

        :param for_type: The type to gather constructor parameter information for.
        """
        if isinstance(for_type, type) and issubclass(for_type, enum.Enum):
            return {"name": self.type_info(str)}
    
        result = {}
        mro = for_type.mro() if isinstance(for_type, type) else (for_type,)
        arg_spec = inspect.getfullargspec(for_type)

        for parameter_name in arg_spec.kwonlyargs:
            for mro_type in mro:  # mro_type might also be just a callable!
                for mro_callable in (getattr(mro_type, "__init__", None), getattr(mro_type, "__new__", mro_type)):
                    if not getattr(mro_callable, "__module__", None):
                        parameter_type = t.get_type_hints(mro_callable).get(parameter_name, None)
                    else:
                        # avoid `get_type_hints` resolving types wrongly that appear with same name in multiple Features
                        parameter_type = t.get_type_hints(
                            mro_callable, None,
                            dict(importlib.import_module(mro_callable.__module__).__dict__)).get(parameter_name, None)
                    if parameter_type:
                        break

                if parameter_type:
                    result[parameter_name] = self.type_info(parameter_type)
                    break

        if arg_spec.varkw and isinstance(for_type, type):
            for superclass in inspect.getclasstree([for_type], unique=True)[-1][0][1]:
                for parameter_name, parameter_type_info in self.parameter_info(superclass).items():
                    if parameter_name not in result:
                        result[parameter_name] = parameter_type_info

        for parameter_name in arg_spec.kwonlyargs:
            if parameter_name not in result:
                result[parameter_name] = self.type_info(object)

        return result

    def all_named_nodes(self, root_node: annize.project.Node) -> t.Sequence[annize.project.ArgumentNode]:
        """
        Return all nodes that have a name assigned in a tree of nodes given by its root node.

        :param root_node: The root node. For the entire project, use its project node.
        """
        return (*((root_node,) if isinstance(root_node, annize.project.ArgumentNode) and root_node.name else ()),
                *(named_node for child_node in root_node.children for named_node in self.all_named_nodes(child_node)))

    def node_by_name(self, name: str, root_node: annize.project.Node) -> annize.project.Node|None:
        """
        Return the node with the given name in a tree of nodes given by its root node (or none).

        :param name: The node name.
        :param root_node: The root node. For the entire project, use its project node.
        """
        for node in self.all_named_nodes(root_node):
            if node.name == name:
                return node

        return None

    def resolve_reference_node(self, node: annize.project.ArgumentNode, *,
                               deep: bool = True) -> annize.project.ArgumentNode|None:
        """
        For a given argument node, resolve it if it is a reference node, or return the node itself otherwise. Return
        :code:`None` if it cannot be resolved.

        :param node: The node to resolve.
        :param deep: Whether to deeply resolve it until a non-reference node is reached (instead of only resolving
                     a single step at most).
        """
        seen_nodes = set()
        while isinstance(node, annize.project.ReferenceNode):
            if node in seen_nodes:
                return None
            seen_nodes.add(node)

            node = self.node_by_name(node.reference_key, node.project) if node.reference_key else None

            if not deep:
                break

        return node

    def possible_argument_names_for_child_in_parent(self, child_type: type, parent_type: type) -> t.Sequence[str]:
        """
        Return the list of possible argument names that a child with a given type can have in a parent with a given
        type, according to the parent's :py:meth:`parameter_info`.

        In the context of Annize objects, this list is only useful for children without an :code:`arg_name`, in order
        to determine it automatically. The first argument name in that list is the preferred one by convention (this is
        e.g. what the project materializer does). The list will also never contain argument names that are marked as
        "explicit only" in the parent implementation.

        See also :py:meth:`possible_argument_infos_for_child_in_parent`.

        :param child_type: The child type.
        :param parent_type: The parent type.
        """
        return self._possible_argument_names_for_child_in_parent(child_type, parent_type,
                                                                 self.parameter_info(parent_type))

    def possible_argument_infos_for_child_in_parent(
            self, child_type: type, parent_type: type) -> t.Sequence[tuple[str, "BasicInspector.TypeInfo"]]:
        """
        Similar to :py:meth:`possible_argument_names_for_child_in_parent`, but also returns the type info for each
        possible argument name.

        :param child_type: The child type.
        :param parent_type: The parent type.
        """
        parent_parameter_info = self.parameter_info(parent_type)
        return tuple(
            (_, parent_parameter_info[_])
            for _ in self._possible_argument_names_for_child_in_parent(child_type, parent_type, parent_parameter_info))

    def type_documentation(self, type_: type, *, with_parameters: bool = False) -> str:
        """
        Return documentation text for a given type. Parts of it might be in the current i18n culture, but most of it
        will be in English or whatever language was used in the docstrings.

        :param type_: The type.
        :param with_parameters: Whether to include documentation for its constructor parameters as well.
        """
        result = ""

        for mro_type_ in type_.mro():
            if mro_type_ in (object, enum.Enum):
                continue
            if mro_type_ == type(None):
                mro_type_doc = str(annize.i18n.TrStr.tr("an_Inspect_doc_None"))
            elif mro_type_ == str:
                mro_type_doc = str(annize.i18n.TrStr.tr("an_Inspect_doc_str"))
            elif mro_type_ == float:
                mro_type_doc = str(annize.i18n.TrStr.tr("an_Inspect_doc_float"))
            elif mro_type_ == int:
                mro_type_doc = str(annize.i18n.TrStr.tr("an_Inspect_doc_int"))
            elif mro_type_ == bool:
                mro_type_doc = str(annize.i18n.TrStr.tr("an_Inspect_doc_bool"))
            else:
                mro_type_doc = getattr(mro_type_, "__doc__", None)

            if mro_type_doc:
                if mro_type_ != type_:
                    result += (f"{annize.i18n.TrStr.tr("an_Inspect_documentationForType").format(t=mro_type_.__name__)}"
                               f"\n\n")
                result += self.__type_documentation__summary(mro_type_doc)
                break

        if with_parameters:
            if result:
                result += "\n\n\n"
            result += f"    {annize.i18n.TrStr.tr("an_Inspect_headParameters")}\n\n"

            for param_name in inspect.getfullargspec(type_).kwonlyargs:
                param_doc = (self.__type_documentation__parameter(type_, param_name)
                             or annize.i18n.TrStr.tr("an_Inspect_noDocAvailable"))
                result += f"# {param_name}:\n\n{param_doc}\n\n"

        return result

    def _possible_argument_names_for_child_in_parent(
            self, child_type: type, parent_type: type,
            parent_parameter_info: t.Mapping[str, "BasicInspector.TypeInfo"]) -> t.Sequence[str]:
        return tuple(parameter_name for parameter_name, parameter_type_info in parent_parameter_info.items()
                     if not annize.object.config.parameter_config(parent_type, parameter_name).explicit_only
                     and parameter_type_info.matches_inner_type(child_type))

    def __type_info(self, for_type: type, as_optional: bool = False) -> "BasicInspector.TypeInfo":
        if isinstance(for_type, (t._GenericAlias, types.GenericAlias, types.UnionType)):
            if getattr(for_type, "__origin__", None) is t.Union or isinstance(for_type, types.UnionType):
                type_args = getattr(for_type, "__args__", ())
                real_type_args = [_ for _ in type_args if _ is not type(None)]
                is_optional = len(real_type_args) < len(type_args)
                real_type_args = real_type_args or [object]
                if len(real_type_args) == 1:
                    return self.__type_info(real_type_args[0], is_optional)
                return BasicInspector._UnionTypeInfo(str(for_type), is_optional,
                                                     [self.__type_info(_) for _ in real_type_args])
            return BasicInspector._ListTypeInfo(str(for_type), as_optional, self.__type_info(for_type.__args__[0]))
        return BasicInspector._ScalarTypeInfo(for_type.__name__, for_type, as_optional)

    @staticmethod
    def __type_documentation__summary(type_doc: str) -> str:
        type_doc_lines = type_doc.split("\n")
        while len(type_doc_lines) > 0 and not type_doc_lines[0].strip():
            type_doc_lines.pop(0)
        while len(type_doc_lines) > 0 and not type_doc_lines[-1].strip():
            type_doc_lines.pop()
        indent = len(type_doc_lines[0]) - len(type_doc_lines[0].lstrip())
        return "\n".join(_[indent:] for _ in type_doc_lines)

    @staticmethod
    def __type_documentation__parameter(type_: type, param_name: str) -> str:
        for mro_type_ in type_.mro():
            for func_doc in (getattr(mro_type_, _).__doc__ or "" for _ in ("__init__", "__new__")):
                if param_doc_lines := BasicInspector.__type_documentation__parameter_block(func_doc, param_name):
                    return BasicInspector.__type_documentation__parameter_from_lines(param_doc_lines)
        return ""

    @staticmethod
    def __type_documentation__parameter_block(func_doc: str, param_name: str) -> t.Sequence[str]:
        func_doc_lines = f"{func_doc}\n:".split("\n")

        i_parameter_block_begin = None
        i_parameter_block_end = 0
        for i_line, line in enumerate(func_doc_lines):
            if i_parameter_block_begin is not None and line.lstrip().startswith(":"):
                i_parameter_block_end = i_line
                break
            if i_parameter_block_begin is None and line.lstrip().startswith(f":param {param_name}:"):
                i_parameter_block_begin = i_line

        if i_parameter_block_begin is None:
            return ()
        return func_doc_lines[i_parameter_block_begin:i_parameter_block_end]

    @staticmethod
    def __type_documentation__parameter_from_lines(param_doc_lines: t.Sequence[str]) -> str:
        param_doc_lines = [_ for _ in (_.strip() for _ in param_doc_lines) if _]
        if len(param_doc_lines) > 0:
            param_doc_lines[0] = param_doc_lines[0][param_doc_lines[0].find(":", 1)+1:].strip()
        return "\n".join(param_doc_lines)

    class TypeInfo(abc.ABC):

        @property
        @abc.abstractmethod
        def name(self) -> str:
            pass

        @property
        @abc.abstractmethod
        def type(self) -> type|None:
            pass

        @property
        @abc.abstractmethod
        def is_optional(self) -> bool:
            pass

        @property
        @abc.abstractmethod
        def allows_multiple_args(self) -> bool:
            pass

        @property
        @abc.abstractmethod
        def inner_type_info(self) -> "BasicInspector.TypeInfo|None":
            pass

        @abc.abstractmethod
        def matches_type(self, type_: builtins.type) -> bool:
            pass

        @abc.abstractmethod
        def matches_inner_type(self, type_: builtins.type) -> bool:
            pass

    class _ScalarTypeInfo(TypeInfo):

        def __init__(self, name: str, type_: type|None, is_optional: bool):
            self.__name = name
            self.__type = type_
            self.__is_optional = is_optional

        @property
        def name(self):
            return self.__name

        @property
        def type(self):
            if self.__type:
                # we sometimes get broken types from typing.get_type_hints that need this extra work
                try:
                    result = importlib.import_module(self.__type.__module__)
                    for segment in self.__type.__qualname__.split("."):
                        result = getattr(result, segment)
                    return result
                except AttributeError:
                    _logger.debug(traceback.format_exc())
            return self.__type

        def matches_type(self, type_):
            return self.type and issubclass(type_, self.type)

        def matches_inner_type(self, type_):
            if inner_type_info := self.inner_type_info:
                return inner_type_info.matches_type(type_)
            else:
                return self.matches_type(type_)

        @property
        def is_optional(self):
            return self.__is_optional

        @property
        def inner_type_info(self):
            return None

        @property
        def allows_multiple_args(self):
            return False

    class _ListTypeInfo(_ScalarTypeInfo):

        def __init__(self, name: str, is_optional: bool, inner_type_info):
            super().__init__(name, list, is_optional)
            self.__inner_type_info = inner_type_info

        @property
        def allows_multiple_args(self):
            return True

        @property
        def inner_type_info(self):
            return self.__inner_type_info

    class _UnionTypeInfo(_ScalarTypeInfo):

        def __init__(self, name: str, is_optional: bool, union_member_type_infos):
            super().__init__(name, None, is_optional)
            self.__union_member_type_infos = union_member_type_infos

        def matches_type(self, type_):
            return any(union_member_type_info.matches_type(type_)
                       for union_member_type_info in self.__union_member_type_infos)


class FullInspector(BasicInspector):
    """
    Project inspectors are used in order to get various additional metadata about parts of a project, which are needed
    e.g. for project parsing and materialization or project configuration UIs.

    This inspector type has full functionality, but has dependencies. See also :py:class:`BasicInspector`.
    """

    def __init__(self, *, feature_loader: annize.project.feature_loader.FeatureLoader|None = None):
        """
        :param feature_loader: The custom feature loader to use.
        """
        super().__init__()
        self.__feature_loader = feature_loader or annize.project.feature_loader.DefaultFeatureLoader()

    def match_arguments(self, node: annize.project.Node) -> "ArgumentMatchings":
        """
        For a given node, determine for each child node to which argument it matches, and return these argument
        matchings (taking care of type annotations and arguments' :code:`arg_name`).
        
        Whenever a child cannot be mapped to a particular argument, it is mapped to the :code:`""` argument.
        Whenever more than one argument name would be possible, the first one is taken.

        :param node: The node to check.
        """
        result = {"": node.children}
        not_allows_multiple_args = set()
        
        if isinstance(node, annize.project.ObjectNode):
            if (object_type := self.argument_type_for_argument_node(node)) is not None:
                result = {}
                parameter_info = self.parameter_info(object_type)

                for parameter_name, parameter_type_info in parameter_info.items():
                    result[parameter_name] = []
                    if not parameter_type_info.allows_multiple_args:
                        not_allows_multiple_args.add(parameter_name)
                result[""] = []

                for child_node in node.children:
                    assert isinstance(child_node, annize.project.ArgumentNode)
                    arg_name = child_node.arg_name
                    if not arg_name:
                        if child_argument_type := self.argument_type_for_argument_node(child_node):
                            matching_argument_names = self._possible_argument_names_for_child_in_parent(child_argument_type,
                                                                                               object_type,
                                                                                               parameter_info)
                            arg_name = "" if len(matching_argument_names) == 0 else matching_argument_names[0]
                    arg_result_list = result[arg_name] = result.get(arg_name, [])
                    arg_result_list.append(child_node)

        return FullInspector.ArgumentMatchings([
            FullInspector.ArgumentMatching(arg_name, sub_nodes, arg_name not in not_allows_multiple_args)
            for arg_name, sub_nodes in result.items()])

    def argument_type_for_argument_node(self, node: annize.project.ArgumentNode) -> type|None:
        """
        For a given argument node, return its argument type, or :code:`None` if it was unavailable.
        For reference nodes, it will resolve the reference and return :code:`None` if it was unresolvable.

        :param node: The argument node.
        """
        node = self.resolve_reference_node(node)
        if node is None:
            return None

        if isinstance(node, annize.project.ObjectNode):
            if feature_module := self.__feature_loader.load_feature(node.feature):
                return getattr(feature_module, node.type_name, None)
            return None

        if isinstance(node, annize.project.ScalarValueNode):
            return type(node.value)

        raise RuntimeError(f"invalid type of node: {node!r}")

    def creatable_type_info(self, for_type: type) -> "CreatableTypeInfo":
        """
        Return creatable type information for a given type. This includes the functionality of :py:meth:`type_info`,
        but it also includes information for turning it into an argument node.

        :param for_type: The type to gather information for.
        """
        for type_info in self.__all_creatable_types():
            if type_info.type == for_type:
                return type_info
        raise RuntimeError(f"invalid type: {for_type!r}")

    def creatables_for_node_argument(self, node: annize.project.Node,
                                     parameter_name: str) -> t.Sequence["FullInspector.CreatableInfo"]:
        """
        For a given node and parameter name, return a list of all creatable infos that would be valid for this
        parameter.

        :param node: The node.
        :param parameter_name: The parameter name.
        """
        result = []
        for type_info in self.creatable_types_for_node_argument(node, parameter_name):
            if issubclass(type_info.type, enum.Enum):
                for enum_item in type_info.type:
                    result.append(FullInspector.CreatableInfo(type_info, enum_item.name, {"name": enum_item.name}))
            else:
                result.append(FullInspector.CreatableInfo(type_info, "", {}))
        return result

    def creatable_types_for_node_argument(self, node: annize.project.Node,
                                          parameter_name: str) -> t.Sequence["FullInspector.CreatableTypeInfo"]:
        """
        For a given node and parameter name, return a list of all creatable type infos that would be valid for this
        parameter.

        This only returns a list of actual types. You probably should use :py:meth:`creatables_for_node_argument`
        instead.

        :param node: The node.
        :param parameter_name: The parameter name.
        """
        if isinstance(node, annize.project.ObjectNode):
            if object_type := self.argument_type_for_argument_node(node):
                if arg_info := self.parameter_info(object_type).get(parameter_name or ""):
                    return tuple(type_info for type_info in self.__all_creatable_types()
                                 if arg_info.matches_inner_type(type_info.type))
            return self.__all_creatable_types()

        if isinstance(node, annize.project.FileNode):
            return self.__all_creatable_types(with_value_types=False)

        else:
            return ()

    def possible_reference_targets_for_node_argument(
            self, node: annize.project.Node, parameter_name: str) -> t.Sequence[annize.project.ArgumentNode]:
        """
        For a given node and parameter name, return a list of all named nodes (so they can be referenced) that would be
        valid arguments for this parameter.

        :param node: The node.
        :param parameter_name: The parameter name.
        """
        parameter_name = parameter_name or ""
        if isinstance(node, annize.project.ObjectNode):
            if object_type := self.argument_type_for_argument_node(node):
                if arg_info := self.parameter_info(object_type).get(parameter_name):
                    return tuple(_ for _ in self.all_named_nodes(node.project)
                                 if arg_info.matches_inner_type(self.argument_type_for_argument_node(_)))

            return self.all_named_nodes(node.project)

        if isinstance(node, annize.project.FileNode):
            return self.all_named_nodes(node.project)

        else:
            raise RuntimeError(f"invalid type of node: {node!r}")

    def possible_append_to_targets_for_node(
            self, node: annize.project.ArgumentNode) -> t.Sequence[annize.project.ArgumentNode]:
        """
        For a given node, return a list of all named nodes that would be valid :code:`append_to` targets.

        :param node: The node.
        """
        object_node = self.resolve_reference_node(node)
        if object_node is None:
            return self.all_named_nodes(node.project)

        if (node_type := self.argument_type_for_argument_node(node)) is None:
            return self.all_named_nodes(node.project)

        result = []
        for node_ in self.all_named_nodes(node.project):
            object_node_ = self.resolve_reference_node(node_)
            if not isinstance(object_node_, annize.project.ObjectNode):
                continue
            possible_argument_names_for_child_in_parent = ()
            if (parent_type := self.argument_type_for_argument_node(object_node_)) is not None:
                possible_argument_names_for_child_in_parent = self.possible_argument_names_for_child_in_parent(node_type, parent_type)
            if len(possible_argument_names_for_child_in_parent) == 0:
                continue

            result.append(node_)

        return tuple(result)

    def __all_creatable_types(self, *, with_value_types: bool = True) -> t.Sequence["FullInspector.CreatableTypeInfo"]:
        if with_value_types:
            result = [FullInspector.CreatableTypeInfo(_.__name__, _, False, None, _.__name__)
                      for _ in (str, int, float, bool)]
        else:
            result = []

        for feature_name in self.__feature_loader.get_all_available_feature_names():
            feature = self.__feature_loader.load_feature(feature_name)
            for item_name in dir(feature):
                if not item_name.startswith("_"):
                    item = getattr(feature, item_name)
                    if inspect.isclass(item) and not inspect.isabstract(item):
                        result.append(FullInspector.CreatableTypeInfo(f"annize.features.{feature_name}.{item_name}",
                                                                      item, False, feature_name, item_name))

        return tuple(result)

    class ArgumentMatching:

        def __init__(self, arg_name: str, nodes: t.Iterable[annize.project.Node],
                     allows_multiple_args: bool):
            self.__arg_name = arg_name or ""
            self.__nodes = tuple(nodes)
            self.__allows_multiple_args = allows_multiple_args

        @property
        def arg_name(self) -> str:
            return self.__arg_name

        @property
        def allows_multiple_args(self) -> bool:
            return self.__allows_multiple_args

        @property
        def nodes(self) -> t.Sequence[annize.project.Node]:
            return self.__nodes

    class ArgumentMatchings:

        def __init__(self, all_matchings: t.Iterable["FullInspector.ArgumentMatching"]):
            self.__all = tuple(all_matchings)

        def matching_by_arg_name(self, arg_name: str) -> "FullInspector.ArgumentMatching|None":
            for matching in self.__all:
                if matching.arg_name == arg_name:
                    return matching
            return None

        def all(self) -> t.Sequence["FullInspector.ArgumentMatching"]:
            return self.__all

    class CreatableTypeInfo(BasicInspector._ScalarTypeInfo):

        def __init__(self, name, type_, is_optional, feature_name: str|None, type_short_name: str):
            super().__init__(name, type_, is_optional)
            self.__feature_name = feature_name
            self.__type_short_name = type_short_name

        @property
        def feature_name(self) -> str|None:
            return self.__feature_name

        @property
        def type_short_name(self) -> str:
            return self.__type_short_name

    class CreatableInfo:

        def __init__(self, type_info: "FullInspector.CreatableTypeInfo", name: str, kwargs):
            self.__type_info = type_info
            self.__name = name
            self.__kwargs = kwargs

        @property
        def type_info(self) -> "FullInspector.CreatableTypeInfo":
            return self.__type_info

        @property
        def name(self) -> str:
            return self.__name

        @property
        def kwargs(self):
            return self.__kwargs
