# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`ArgumentBehavior` and :py:class:`AssociateArgumentNodeBehavior`.
"""
import contextlib
import enum
import inspect
import typing as t

import annize.flow.run_context
import annize.data
import annize.project.feature_loader
import annize.project.inspector
import annize.project.materializer.behaviors


class ArgumentBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles argument nodes (incl. creation of an object for an object node).
    """

    def __init__(self, create_object_func, *, feature_loader: annize.project.feature_loader.FeatureLoader):
        self.__feature_loader = feature_loader
        self.__create_object_func = create_object_func
        self.__inspector = annize.project.inspector.FullInspector(feature_loader=feature_loader)

    @contextlib.contextmanager
    def node_context(self, node_materialization, desperate):
        yield
        if isinstance(node_materialization.node, annize.project.ObjectNode):
            args, kwargs = list(), dict()
            for child_node, child_arguments in node_materialization.materialized_children_tuples(desperate=desperate):
                if len(child_arguments) > 0:
                    if isinstance(child_node, annize.project.ArgumentNode) and child_node.arg_name:
                        arg_is_list = False
                        if (node_argument_type := self.__inspector.argument_type_for_argument_node(
                                node_materialization.node)):
                            if arg_type_info := self.__inspector.parameter_info(node_argument_type).get(
                                    child_node.arg_name):
                                arg_is_list = arg_type_info.allows_multiple_args
                        if arg_is_list:
                            arg_list = kwargs[child_node.arg_name] = kwargs.get(child_node.arg_name, [])
                            arg_list += child_arguments
                        else:
                            kwargs[child_node.arg_name] = child_arguments[0]
                    else:
                        args += child_arguments
            feature_module = self.__feature_loader.load_feature(node_materialization.node.feature)
            if not feature_module:
                raise annize.project.FeatureUnavailableError(node_materialization.node.feature)
            try:
                node_class = getattr(feature_module, node_materialization.node.type_name)
            except AttributeError as ex:
                raise annize.project.MaterializerError(
                    f"no item {node_materialization.node.type_name!r} in Feature module {node_materialization.node.feature!r}") from ex

            if issubclass(node_class, enum.Enum):
                enum_item_name = kwargs.pop("name")
                for enum_item in node_class:
                    if enum_item.name == enum_item_name:
                        kwargs["value"] = enum_item.value
                        break
                else:
                    raise annize.project.MaterializerError(f"invalid name for enum item {node_class.__name__!r}:"
                                                           f" {enum_item_name}")

            else:
                node_class_spec = inspect.getfullargspec(node_class)
                if len(node_class_spec.args) > 1 or node_class_spec.varargs:
                    raise annize.project.MaterializerError(f"callable {node_materialization.node.type_name!r} in {node_materialization.node.feature!r}"
                                                           f" has positional arguments, which is not allowed")

            try:
                value = self.__create_object_func(node_class, args, kwargs)
            except TypeError as ex:
                raise annize.project.MaterializerError(f"unable to construct"
                                                       f" '{node_materialization.node.feature}.{node_materialization.node.type_name}': {ex}") from ex
        elif isinstance(node_materialization.node, annize.project.ScalarValueNode):
            value = node_materialization.node.value
        else:
            return
        if node_materialization.node.name:
            annize.flow.run_context.set_object_name(value, node_materialization.node.name)
        node_materialization.set_materialized_result([value])
        annize.flow.run_context.add_object(value)


class AssociateArgumentNodeBehavior(annize.project.materializer.behaviors.Behavior):

    def __init__(self, association: dict[annize.project.ArgumentNode, list[t.Any]]):
        self.__association = association

    @contextlib.contextmanager
    def node_context(self, node_materialization, desperate):
        yield
        if isinstance(node_materialization.node, annize.project.ArgumentNode) and node_materialization.has_result:
            self.__association[node_materialization.node] = node_materialization.result
