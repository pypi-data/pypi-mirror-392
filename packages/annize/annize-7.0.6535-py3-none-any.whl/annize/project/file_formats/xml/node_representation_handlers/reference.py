# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Reference node representation handler.
"""
import lxml.etree

import annize.project.file_formats.xml.node_representation_handlers.argument


class NodeReader(annize.project.file_formats.xml.NodeReader):

    def read(self, xml_element, context):
        if xml_element.tag == "{annize}reference":
            xml_attributes = dict(xml_element.attrib)

            result_node = annize.project.ReferenceNode()
            result_node.reference_key = xml_attributes.pop("name", None)
            if on_unresolvable_str := xml_attributes.pop("on_unresolvable", None):
                result_node.on_unresolvable = annize.project.ReferenceNode.OnUnresolvableAction(on_unresolvable_str)
            result_node.arg_name = xml_attributes.pop("{annize}arg_name", None)
            result_node.name = xml_attributes.pop("{annize}name", None)
            result_node.append_to = xml_attributes.pop("{annize}append_to", None)

            if xml_attributes:
                raise RuntimeError(f"invalid attribute: {tuple(xml_attributes.keys())[0]}")

            if (xml_element.text or "").strip():
                raise RuntimeError(f"text content not allowed there: {xml_element.text.strip()}")
            if (xml_element.tail or "").strip():
                raise RuntimeError(f"text content not allowed there: {xml_element.tail.strip()}")

            return NodeReader.ReadResult(result_node, tuple(xml_element), result_node)


class NodeEditor(annize.project.file_formats.xml.node_representation_handlers.argument.NodeEditor):

    def can_handle(self, node):
        return isinstance(node, annize.project.ReferenceNode)

    def expand(self, request):
        if (isinstance(request.event, annize.project.Node.PropertyChangedEvent)
                and request.event.property_name == "reference_key"):
            return

        node_representation = request.node_representation(request.node)
        if not node_representation.attrib_name:
            return

        node_representation.element.attrib.pop(node_representation.attrib_name, None)
        new_xml_element = lxml.etree.Element("{annize}reference", nsmap={"a": "annize"})
        for attrib_name, attrib_value in (("name", request.node.reference_key),
                                          ("on_unresolvable", request.node.on_unresolvable.value),
                                          ("{annize}append_to", request.node.append_to),
                                          ("{annize}arg_name", request.node.arg_name),
                                          ("{annize}name", request.node.name)):
            if attrib_value:
                new_xml_element.attrib[attrib_name] = attrib_value
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
                and self._is_scalar_argument(request.inspector, request.node.parent, request.node.arg_name)
                and request.node.on_unresolvable == annize.project.ReferenceNode.OnUnresolvableAction.FAIL):
            annize.project.file_formats.xml.marshaler.Marshaler.remove_element(node_representation.element)
            parent_xml_element.attrib[request.node.arg_name] = NodeEditor._reference_str(request.node.reference_key)
            request.set_node_representation(request.node, parent_xml_element, attrib_name=request.node.arg_name)

        elif request.node.on_unresolvable == annize.project.ReferenceNode.OnUnresolvableAction.FAIL:
            node_representation.element.attrib.pop("on_unresolvable", None)

    def representation_tag(self, node):
        return "{annize}reference"

    def properties(self):
        return *super().properties(), NodeEditor.ReferenceKeyProperty(), NodeEditor.OnUnresolvableProperty()

    @staticmethod
    def _reference_str(reference_key: str|None) -> str:
        return (f"{annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_START}"
                f"{f"reference {reference_key}" if reference_key else "reference"}"
                f"{annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_END}")

    class ReferenceKeyProperty(annize.project.file_formats.xml.marshaler.NodeEditor.Property[str|None]):

        name = "reference_key"

        def apply_value_to_representation(self, value, node_representation):
            if node_representation.attrib_name:
                node_representation.element.attrib[node_representation.attrib_name] = NodeEditor._reference_str(value)
            else:
                if value:
                    node_representation.element.attrib["name"] = value
                else:
                    node_representation.element.attrib.pop("name", None)

    class OnUnresolvableProperty(annize.project.file_formats.xml.marshaler.NodeEditor.Property[
                                     annize.project.ReferenceNode.OnUnresolvableAction]):

        name = "on_unresolvable"

        def apply_value_to_representation(self, value, node_representation):
            node_representation.element.attrib["on_unresolvable"] = value.value
