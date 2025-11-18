# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Some preprocessor functions used by the materializer.

Only used internally by the parent package.
"""
import itertools
import typing as t

import hallyd

import annize.data
import annize.project


def resolve_appendtonodes(topnode: annize.project.Node) -> annize.project.Node:
    referencetuples = []
    def plan_references(node: annize.project.Node|None, childnodes: t.Iterable[annize.project.Node]) -> None:
        if isinstance(node, annize.project.ArgumentNode) and node.append_to:
            pkey = node.name = (node.name or f"__{hallyd.lang.unique_id()}")
            referencetuples.append((pkey, node.append_to))
        for childnode in childnodes:
            plan_references(childnode, childnode.children)
    plan_references(None, [topnode])
    unresolved_referencetuples = list(referencetuples)
    def create_references(node: annize.project.Node|None) -> None:
        if isinstance(node, annize.project.ArgumentNode):
            for referencetuple in referencetuples:
                originname, appendttoname = referencetuple
                if node.name == appendttoname:
                    keyrefnode = annize.project.ReferenceNode()
                    keyrefnode.reference_key = originname
                    keyrefnode.on_unresolvable = annize.project.ReferenceNode.OnUnresolvableAction.SKIP
                    node.append_child(keyrefnode)
                    if referencetuple in unresolved_referencetuples:
                        unresolved_referencetuples.remove(referencetuple)
        for childnode in node.children:
            create_references(childnode)
    create_references(topnode)
    if unresolved_referencetuples:
        raise annize.project.UnresolvableReferenceError(unresolved_referencetuples[0][1])
    return topnode
