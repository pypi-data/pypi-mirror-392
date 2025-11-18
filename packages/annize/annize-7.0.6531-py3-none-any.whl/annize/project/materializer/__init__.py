# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Materializing of Annize projects into a working runtime structure (usually used by the Runner application).

See :py:func:`materialize`.

All submodules are only used internally by this one. There is a core part, some preprocessor functions, some behaviors
that implement what it does for different types of project nodes, and the object factory.
"""
import itertools
import typing as t

import annize.project.materializer.object_factory
import annize.project.feature_loader
import annize.project.materializer.core


class MaterializationResult:

    def __init__(self, root_objects: list[t.Any], node_association: dict[annize.project.Node, list[t.Any]],
                 problems: dict[annize.project.Node|None, list[Exception]]):
        self.__root_objects = root_objects
        self.__node_association = node_association
        self.__problems = problems

    @property
    def root_objects(self) -> list[t.Any]:
        return self.__root_objects

    def objects_for_node(self, node: annize.project.Node) -> list[t.Any]|None:
        return self.__node_association.get(node)

    def erroneous_nodes(self) -> list[annize.project.Node]:
        return [node for node in self.__problems.keys() if node]

    def errors_for_node(self, node: t.Any) -> list[Exception]:
        return self.__problems.get(node) or []


def materialize(
        project: "annize.project.ProjectNode", *,
        feature_loader: annize.project.feature_loader.FeatureLoader|None = None) -> MaterializationResult:
    import annize.project.materializer.behaviors.argument as argument
    import annize.project.materializer.behaviors.basket as basket
    import annize.project.materializer.behaviors.block as block
    import annize.project.materializer.behaviors.feature_unavailable as feature_unavailable
    import annize.project.materializer.behaviors.reference as reference
    import annize.project.materializer.preprocessors as preprocessors

    feature_loader = feature_loader or annize.project.feature_loader.DefaultFeatureLoader()

    top_node = project.clone()
    real_nodes_for_clones = _node_clone_link(project, top_node)
    top_node = preprocessors.resolve_appendtonodes(top_node)
    node_association = {}
    root_objects, errors = annize.project.materializer.core.ProjectMaterializer(
        top_node, behaviors=(
            argument.AssociateArgumentNodeBehavior(node_association),
            basket.BasketBehavior(),
            feature_unavailable.FeatureUnavailableBehavior(),
            reference.ReferenceBehavior(),
            block.BlockBehavior(),
            argument.ArgumentBehavior(annize.project.materializer.object_factory.create_object, feature_loader=feature_loader)
        )).materialize()
    node_association, errors = _translate_from_clone(real_nodes_for_clones, node_association, errors)
    return MaterializationResult(root_objects, node_association, errors)


def _translate_from_clone(real_nodes_for_clones, node_association, errors):
    node_association_orig = {}
    errors_orig = {}
    for k, v in errors.items():
        errors_orig[real_nodes_for_clones.get(k)] = [err for err in v if not isinstance(err, annize.project.materializer.core.InternalError)]
    for node_association_node, node_association_objects in node_association.items():
        real_node = real_nodes_for_clones.get(node_association_node)
        if real_node:
            node_association_orig[real_node] = node_association_objects
    return node_association_orig, errors_orig


def _node_clone_link(original_project_node: annize.project.ProjectNode,
                     cloned_project_node: annize.project.ProjectNode) -> dict[annize.project.Node, annize.project.Node]:
    result = {}
    node_tuples: list[tuple[annize.project.Node, annize.project.Node]] = [(original_project_node, cloned_project_node)]
    while node_tuples:
        original_node, cloned_node = node_tuples.pop()
        result[cloned_node] = original_node
        for i_child_node, cloned_child_node in enumerate(cloned_node.children):
            node_tuples.append((original_node.children[i_child_node], cloned_child_node))
    return result
