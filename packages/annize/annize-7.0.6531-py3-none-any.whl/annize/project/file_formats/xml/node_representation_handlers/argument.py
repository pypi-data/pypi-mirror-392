# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Argument node representation handler.
"""
import abc
import typing as t

import annize.project.file_formats.xml.marshaler


class NodeEditor(annize.project.file_formats.xml.marshaler.NodeEditor, abc.ABC):

    def properties(self):
        return *super().properties(), *(NodeEditor.SimpleOptionalStringProperty(name, f"{{annize}}{name}")
                                        for name in ("name", "append_to", "arg_name"))

    @staticmethod
    def attribute_str_to_node(key: str|None, value: str) -> annize.project.Node:
        """
        Return a node (typically scalar or reference) for an XML tag's attribute. See also
        :py:meth:`value_to_attribute_str`.

        :param key: The attribute key.
        :param value: The attribute value.
        """
        value_is_string = True
        if (value.startswith(annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_START)
                and value.endswith(annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_END)):
            value = value[1:-1]
            if not value.startswith(annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_START):
                value_is_string = False

        if not value_is_string:
            if value == "reference" or value.startswith("reference "):
                result = annize.project.ReferenceNode()
                result.reference_key = value[10:].strip() or None
                result.arg_name = key
                return result

            value = NodeEditor.__attribute_str_to_node__value(value)

        result = annize.project.ScalarValueNode()
        result.value = value
        result.arg_name = key
        return result

    @staticmethod
    def value_to_attribute_str(value: t.Any) -> str:
        """
        Return an XML attribute string for a given value. See also :py:meth:`attribute_str_to_node`.

        :param value: The value to translate.
        """
        if value in (True, False, None) or isinstance(value, float):
            return (f"{annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_START}{value}"
                    f"{annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_END}")

        if isinstance(value, str):
            if (value.startswith(annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_START)
                    and value.endswith(annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_END)):
                return (f"{annize.project.file_formats.xml.FileFormat._ATTRIBUTE_COMMAND_START}{value}"
                        f"{annize.project.file_formats.FileFormat.xml._ATTRIBUTE_COMMAND_END}")
            return value

        raise ValueError(f"invalid value: {value}")

    def _is_scalar_argument(self, inspector: "annize.project.inspector.FullInspector",
                            parent_node: annize.project.ObjectNode|None, arg_name: str) -> bool|None:
        if arg_name and isinstance(parent_node, annize.project.ObjectNode):
            if argument_matchings := inspector.match_arguments(parent_node):
                if argument_matching := argument_matchings.matching_by_arg_name(arg_name):
                    return not argument_matching.allows_multiple_args
        return None

    @staticmethod
    def __attribute_str_to_node__value(value_str: str) -> t.Any:
        for value in (True, False, None):
            if value_str == str(value):
                return value

        try:
            return int(value_str)
        except ValueError:
            pass

        try:
            return float(value_str)
        except ValueError:
            pass

        raise ValueError(f"invalid magic attribute value {value!r}")
