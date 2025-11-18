# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Behaviors.

See :py:class:`Behavior`.
"""
import abc
import contextlib
import typing as t

import annize.project.materializer.core


class Behavior(abc.ABC):
    """
    A behavior implements what the materializer does for a given node. See subclasses in the submodules.
    """

    @contextlib.contextmanager
    def early_node_context(self, early_node_materialization: "annize.project.materializer.core.EarlyNodeMaterialization"
                           ) -> t.ContextManager:
        """
        Context for early materialization steps. It works similar to :py:meth:`node_context`, but the early contexts
        get entered before the main work (of :py:meth:`node_context`) begins, and get left afterward. These early
        contexts are only used for very particular preparation steps. They do not participate in the actual
        materialization.
        """
        yield

    @abc.abstractmethod
    def node_context(self, node_materialization: "annize.project.materializer.core.NodeMaterialization",
                     desperate: bool) -> t.ContextManager:
        """
        For a node, the materializer will enter the context returned by this function for all behaviors.

        The materializer itself does that for the root node. Behaviors itself are responsible for triggering that
        same process on children.

        So, any node gets materialized in the context of all behaviors on all parent nodes. Actual materialization logic
        happens in this function, in the course of setting up and taking down all these contexts.

        Note: Behaviors might fail in some situation, e.g. if a reference is not resolvable yet. The outer routine will
        retry the materialization process until all behaviors finally succeed or some errors persist.

        :param node_materialization: The node materialization for the current node.
        :param desperate: Whether this is a desperate (i.e. late) attempt to materialize, so it is e.g. allowed to
                          consider an unresolvable reference as finally unresolvable.
        """
