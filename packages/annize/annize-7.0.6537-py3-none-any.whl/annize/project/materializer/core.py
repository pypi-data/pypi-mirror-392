# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Inner core parts of the project materializer. Only used internally by the parent package.
"""
import contextlib
import itertools
import logging
import typing as t

import annize.flow.run_context
import annize.project

if t.TYPE_CHECKING:
    import annize.project.feature_loader
    import annize.project.materializer.behaviors


_logger = logging.getLogger(__name__)

_Material = t.Any

_Materialization = tuple[annize.project.Node, t.Sequence[_Material]]


class EarlyNodeMaterialization:

    def __init__(self, materializer: "ProjectMaterializer", node: annize.project.Node, store: dict):
        self.__node = node
        self.__materializer = materializer
        self.__store = store

    @property
    def node(self) -> annize.project.Node:
        return self.__node

    @contextlib.contextmanager
    def early_materialize_children(self):
        with contextlib.ExitStack() as stack:
            for child_node in self.__node.children:
                stack.enter_context(self.__materializer._early_materialize(child_node, self.__store))
            yield


class NodeMaterialization:

    def __init__(self, materializer: "ProjectMaterializer", node: annize.project.Node, store: dict):
        self.__node = node
        self.__materializer = materializer
        self.__store = store
        self.__result = None
        self.__problems = ()

    @property
    def node(self) -> annize.project.Node:
        return self.__node

    def set_materialized_result(self, result: t.Iterable[t.Any]) -> None:
        self.__result = tuple(result)

    def set_problems(self, problems: t.Iterable[Exception]):
        self.__problems = tuple(problems)

    def materialized_children_tuples(self, *, desperate: bool):
        return self.__materializer._materialize_hlp_childobjs(self.__node, self.__store, desperate)

    def materialized_children(self, *, desperate: bool) -> t.Iterable[_Material]:
        return list(itertools.chain.from_iterable([_[1]
                                                   for _ in self.materialized_children_tuples(desperate=desperate)]))

    def try_get_materialization_for_node(self, node: annize.project.Node):
        return self.__store.get(node, None)

    @property
    def has_result(self):
        return self.__result is not None

    @property
    def result(self) -> t.Sequence[t.Any]:
        if not self.has_result:
            raise RuntimeError("no result available")
        return self.__result

    @property
    def problems(self) -> t.Sequence[Exception]:
        return self.__problems


class ProjectMaterializer:

    def __init__(self, node: annize.project.Node, *,
                 behaviors: t.Iterable["annize.project.materializer.behaviors.Behavior"]):
        self.__node = node
        self.__behaviors = behaviors

    def materialize(self) -> tuple[t.Sequence[t.Any]|None, dict[annize.project.Node, t.Sequence[Exception]]]:
        early_materialization_store = {}
        materialization_store = {}
        erroneous_nodes = None
        retry = True
        desperate = False

        with self._early_materialize(self.__node, early_materialization_store):
            while retry or not desperate:
                desperate = not retry
                _logger.debug("Beginning project materialization attempt.")
                self.__materialize(self.__node, materialization_store, desperate)
                erroneous_nodes, retry = ProjectMaterializer.__erroneous_nodes(materialization_store, erroneous_nodes)

        node_materialization = self.__materialization_for_node(self.__node, materialization_store)
        _logger.debug("Materialization succeeded" if node_materialization.has_result else "Materialization failed")
        if node_materialization.has_result:
            for obj in node_materialization.result:
                annize.flow.run_context.current().mark_object_as_toplevel(obj)
            result = node_materialization.result
        else:
            result = None
        errors = {node: materialization_store[node].problems for node in erroneous_nodes}
        return result, errors

    @contextlib.contextmanager
    def _early_materialize(self, node, early_materialization_store):
        with contextlib.ExitStack() as stack:
            for behavior in self.__behaviors:
                stack.enter_context(behavior.early_node_context(
                    self.__early_materialization_for_node(node, early_materialization_store)))
            yield

    def _materialize_hlp_childobjs(self, node: annize.project.Node, materialization_store: dict,
                                   desperate: bool) -> list[_Materialization]:
        _logger.debug("Starting materialization of the children of '%s'", node)
        result = []
        children_have_errors = False
        for child_node in node.children:
            self.__materialize(child_node, materialization_store, desperate)
            node_materialization = self.__materialization_for_node(child_node, materialization_store)
            if node_materialization.has_result:
                result.append((child_node, node_materialization.result))
            else:
                children_have_errors = True
        _logger.debug("Finished materialization of the children of '%s' to %d items", node, len(result))
        if children_have_errors:
            raise ChildrenNotMaterializableError(node)
        return result

    def __early_materialization_for_node(self, node: annize.project.Node,
                                         early_materialization_store: dict) -> EarlyNodeMaterialization:
        result = early_materialization_store.get(node, None)
        if not result:
            result = early_materialization_store[node] = EarlyNodeMaterialization(self, node,
                                                                                  early_materialization_store)
        return result

    def __materialization_for_node(self, node: annize.project.Node, materialization_store: dict) -> NodeMaterialization:
        result = materialization_store.get(node, None)
        if not result:
            result = materialization_store[node] = NodeMaterialization(self, node, materialization_store)
        return result

    def __materialize(self, node: annize.project.Node, materialization_store: dict, desperate: bool) -> None:
        node_materialization = self.__materialization_for_node(node, materialization_store)
        _logger.debug("Starting materialization of '%s'; has_result=%r", node, node_materialization.has_result)
        if not node_materialization.has_result:
            node_materialization.set_problems([])
            try:
                with contextlib.ExitStack() as stack:
                    for behavior in self.__behaviors:
                        stack.enter_context(behavior.node_context(node_materialization, desperate))
            except Exception as ex:
                node_materialization.set_problems([ex])
        if node_materialization.has_result:
            _logger.debug("Finalized materialization of '%s' to '%s'", node, node_materialization.result)
        else:
            _logger.debug("Finalized materialization of '%s' without result", node)

    @staticmethod
    def __erroneous_nodes(materialization_store, old_erroneous_nodes):
        new_erroneous_nodes = set()
        for node, node_materialization in materialization_store.items():
            if node_materialization.problems:
                new_erroneous_nodes.add(node)
        if new_erroneous_nodes:
            if old_erroneous_nodes is None:
                retry = True
            else:
                retry = len(old_erroneous_nodes - new_erroneous_nodes) > 0
        else:
            retry = False
        return new_erroneous_nodes, retry


class InternalError(Exception):
    pass


class ChildrenNotMaterializableError(InternalError):

    def __init__(self, node: annize.project.Node):
        super().__init__(f"Children of '{node}' not materializable")
