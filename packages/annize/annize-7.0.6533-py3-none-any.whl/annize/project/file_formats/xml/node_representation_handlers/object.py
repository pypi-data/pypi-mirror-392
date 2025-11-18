# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Object node representation handler.
"""
import annize.project.file_formats.xml.node_representation_handlers.argument


class NodeReader(annize.project.file_formats.xml.NodeReader):

    def read(self, xml_element, context):
        tag = NodeReader._TagParts(xml_element.tag)

        if tag.namespace.startswith("annize:"):
            feature = tag.namespace[7:]

            result_node = annize.project.ObjectNode(feature, tag.tag_name)
            result = NodeReader.ReadResult(result_node, xml_element, result_node)

            if (xml_element.text or "").strip():
                raise RuntimeError(f"text content not allowed there: {xml_element.text.strip()}")
            if (xml_element.tail or "").strip():
                raise RuntimeError(f"text content not allowed there: {xml_element.tail.strip()}")

            for attrib_key, attrib_value in xml_element.attrib.items():
                if attrib_key == "{annize}name":
                    result.node.name = attrib_value
                elif attrib_key == "{annize}append_to":
                    result.node.append_to = attrib_value
                elif attrib_key == "{annize}arg_name":
                    result.node.arg_name = attrib_value
                else:
                    attrib_node = NodeEditor.attribute_str_to_node(attrib_key, attrib_value)
                    context.file_marshaler.set_node_representation(attrib_node, xml_element, attrib_name=attrib_key)
                    result.node.append_child(attrib_node)

            return result

    class _TagParts:
        """
        A plain XML tag name and a namespace.
        """

        def __init__(self, name, namespace: str = ""):
            if name.startswith("{"):
                if namespace:
                    raise annize.project.BadStructureError("namespace is specified via argument and inside the name,"
                                                           " which is conflicting")
                i_namespace_end = name.find("}")
                self.__namespace, self.__tag_name = name[1:i_namespace_end], name[i_namespace_end + 1:]
            else:
                self.__namespace, self.__tag_name = namespace, name

        @property
        def tag_name(self) -> str:
            return self.__tag_name

        @property
        def namespace(self) -> str:
            return self.__namespace


class NodeEditor(annize.project.file_formats.xml.node_representation_handlers.argument.NodeEditor):

    def can_handle(self, node):
        return isinstance(node, annize.project.ObjectNode)

    def representation_tag(self, node):
        return f"{{annize:{node.feature}}}{node.type_name}"

    def representation_namespace_prefix_map(self, node):
        return {None: f"annize:{node.feature}"}
