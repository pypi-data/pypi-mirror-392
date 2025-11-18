# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`BlockBehavior`.
"""
import contextlib

import annize.project.materializer.behaviors


class BlockBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles block.
    """

    @contextlib.contextmanager
    def early_node_context(self, early_node_materialization):
        with early_node_materialization.early_materialize_children():
            yield

    @contextlib.contextmanager
    def node_context(self, node_materialization, desperate):
        yield
        if isinstance(node_materialization.node, (annize.project.IgnoreUnavailableFeatureNode, annize.project.FileNode, annize.project.ProjectNode)):
            node_materialization.set_materialized_result(
                node_materialization.materialized_children(desperate=desperate))
