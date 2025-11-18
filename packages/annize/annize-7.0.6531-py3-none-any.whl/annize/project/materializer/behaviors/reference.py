# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`ReferenceBehavior`.
"""
import contextlib

import annize.flow.run_context
import annize.project.materializer.behaviors


class ReferenceBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles reference nodes.
    """

    def __init__(self):
        super().__init__()

    @contextlib.contextmanager
    def node_context(self, node_materialization, desperate):
        yield
        if isinstance(node_materialization.node, annize.project.ReferenceNode):
            obj = annize.flow.run_context.object_by_name(node_materialization.node.reference_key, self)

            if obj == self:
                if (node_materialization.node.on_unresolvable == annize.project.ReferenceNode.OnUnresolvableAction.FAIL
                        or not desperate):
                    raise annize.project.UnresolvableReferenceError(node_materialization.node.reference_key)
                if node_materialization.node.on_unresolvable == annize.project.ReferenceNode.OnUnresolvableAction.SKIP:
                    materialized_result = ()
                else:
                    raise ValueError(f"invalid on_unresolvable: {node_materialization.node.on_unresolvable}")

            else:
                materialized_result = (obj,)

            node_materialization.set_materialized_result(materialized_result)
