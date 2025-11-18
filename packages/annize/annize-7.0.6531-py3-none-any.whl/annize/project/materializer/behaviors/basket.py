# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`BasketBehavior`.
"""
import contextlib

import annize.data
import annize.project.materializer.behaviors


class BasketBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles baskets.
    """

    @contextlib.contextmanager
    def node_context(self, node_materialization, desperate):
        yield
        if node_materialization.has_result:
            new_result = []
            for result_item in node_materialization.result:
                if getattr(result_item, "_is_annize_basket", False) or isinstance(result_item, annize.data.Basket):
                    new_result += result_item
                else:
                    new_result.append(result_item)
            node_materialization.set_materialized_result(new_result)
