# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
If-Feature-unavailable node representation handler.
"""
import annize.project.file_formats.xml.marshaler


class NodeReader(annize.project.file_formats.xml.NodeReader):

    def read(self, xml_element, context):
        if xml_element.tag == "{annize}ignore_unavailable":
            xml_attributes = dict(xml_element.attrib)

            result_node = annize.project.IgnoreUnavailableFeatureNode()
            result_node.feature = xml_attributes.pop("feature", None)

            if xml_attributes:
                raise RuntimeError(f"invalid attribute: {tuple(xml_attributes.keys())[0]}")

            if (xml_element.text or "").strip():
                raise RuntimeError(f"text content not allowed there: {xml_element.text.strip()}")
            if (xml_element.tail or "").strip():
                raise RuntimeError(f"text content not allowed there: {xml_element.tail.strip()}")

            return NodeReader.ReadResult(result_node, tuple(xml_element), result_node)


class NodeEditor(annize.project.file_formats.xml.marshaler.NodeEditor):

    def can_handle(self, node):
        return isinstance(node, annize.project.IgnoreUnavailableFeatureNode)

    def representation_tag(self, node):
        return "{annize}ignore_unavailable"

    def properties(self):
        return *super().properties(), NodeEditor.SimpleOptionalStringProperty("feature", "feature",
                                                                              additional_none_values=("*",))
