# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
File node representation handler.
"""
import annize.project.file_formats.xml.marshaler


class NodeEditor(annize.project.file_formats.xml.marshaler.NodeEditor):

    def read(self, xml_element, context):
        pass

    def can_handle(self, node):
        return isinstance(node, annize.project.FileNode)

    def representation_tag(self, node):
        return ""
