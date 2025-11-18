# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`FeatureUnavailableBehavior`.
"""
import contextlib

import annize.project.materializer.behaviors


class FeatureUnavailableBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles ignore-unavailable-Feature nodes.
    """

    def __init__(self):
        self.__skip_node_feature_names = []

    @contextlib.contextmanager
    def early_node_context(self, early_node_materialization):
        with contextlib.ExitStack() as contexts:
            if isinstance(early_node_materialization.node, annize.project.IgnoreUnavailableFeatureNode):
                contexts.enter_context(self.__context_skip_node_feature_ignore_list(early_node_materialization.node))

            yield

    @contextlib.contextmanager
    def node_context(self, node_materialization, desperate):
        with contextlib.ExitStack() as contexts:
            if isinstance(node_materialization.node, annize.project.ObjectNode):
                contexts.enter_context(self.__context_catch_exceptions(node_materialization,
                                                                       self.__skip_node_feature_names))

            yield

    @contextlib.contextmanager
    def __context_skip_node_feature_ignore_list(self, node):
        self.__skip_node_feature_names.append(node.feature)
        try:
            yield
        finally:
            self.__skip_node_feature_names.remove(node.feature)

    @contextlib.contextmanager
    def __context_catch_exceptions(self, node_materialization, featureignorelist):
        try:
            yield
        except annize.project.FeatureUnavailableError as ex:
            if ex.feature_name in featureignorelist or "" in featureignorelist or "*" in featureignorelist:
                node_materialization.set_materialized_result(())
            else:
                raise
