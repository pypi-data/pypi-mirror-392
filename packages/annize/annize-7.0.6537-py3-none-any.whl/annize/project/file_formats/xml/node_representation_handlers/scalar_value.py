# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Scalar value node representation handler.
"""
import lxml.etree

import annize.project.file_formats.xml.node_representation_handlers.argument


class NodeReader(annize.project.file_formats.xml.NodeReader):

    def read(self, xml_element, context):
        if xml_element.tag == "{annize}scalar":
            xml_attributes = dict(xml_element.attrib)

            result_node = NodeEditor.attribute_str_to_node(xml_attributes.pop("{annize}arg_name", None),
                                                           xml_element.text or "")
            result_node.name = xml_attributes.pop("{annize}name", None)
            result_node.append_to = xml_attributes.pop("{annize}append_to", None)

            if xml_attributes:
                raise RuntimeError(f"invalid attribute: {tuple(xml_attributes.keys())[0]}")

            return NodeReader.ReadResult(result_node, tuple(xml_element), result_node)


class NodeEditor(annize.project.file_formats.xml.node_representation_handlers.argument.NodeEditor):

    def can_handle(self, node):
        return isinstance(node, annize.project.ScalarValueNode)

    def expand(self, request):
        if (isinstance(request.event, annize.project.Node.PropertyChangedEvent)
                and request.event.property_name == "value"):
            return

        node_representation = request.node_representation(request.node)
        if not node_representation.attrib_name:
            return

        node_representation.element.attrib.pop(node_representation.attrib_name, None)
        new_xml_element = lxml.etree.Element("{annize}scalar", nsmap={"a": "annize"})
        for attrib_name, attrib_value in (("{annize}append_to", request.node.append_to),
                                          ("{annize}arg_name", request.node.arg_name),
                                          ("{annize}name", request.node.name)):
            if attrib_value:
                new_xml_element.attrib[attrib_name] = attrib_value
        new_xml_element.text = NodeEditor.value_to_attribute_str(request.node.value)

        node_representation.element.append(new_xml_element)
        request.set_node_representation(request.node, new_xml_element)
        request.indent_element(new_xml_element)

    def compact(self, request):
        node_representation = request.node_representation(request.node)
        parent_xml_element = node_representation.element.getparent()

        if node_representation.attrib_name:
            return

        if (not request.node.name and not request.node.append_to and request.node.arg_name
                and request.node.arg_name not in parent_xml_element.attrib
                and not NodeEditor.__is_lengthy_string(request.node.value)
                and self._is_scalar_argument(request.inspector, request.node.parent, request.node.arg_name)):
            value_str = NodeEditor.value_to_attribute_str(request.node.value)
            annize.project.file_formats.xml.marshaler.Marshaler.remove_element(node_representation.element)
            parent_xml_element.attrib[request.node.arg_name] = value_str
            request.set_node_representation(request.node, parent_xml_element, attrib_name=request.node.arg_name)

    def representation_tag(self, node):
        return "{annize}scalar"

    def properties(self):
        return *super().properties(), NodeEditor.ValueProperty()

    @staticmethod
    def __is_lengthy_string(value: object) -> bool:
        """
        Return whether a given value is a "lengthy string", i.e. a string that would be inconvenient for attributes.

        :param value: The value.
        """
        return isinstance(value, str) and (len(value) > 30 or ("(" in value and ("'" in value or "\"" in value)))

    class ValueProperty(annize.project.file_formats.xml.marshaler.NodeEditor.Property[object]):

        name = "value"

        def apply_value_to_representation(self, value, node_representation):
            value_str = NodeEditor.value_to_attribute_str(value)
            if node_representation.attrib_name:
                node_representation.element.attrib[node_representation.attrib_name] = value_str
            else:
                node_representation.element.text = value_str
