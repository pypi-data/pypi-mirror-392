# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Support for Annize configuration XML files.

All submodules are only used internally by this one.
"""
import abc
import contextlib
import dataclasses
import io
import typing as t

import hallyd
import lxml.etree

import annize.project.file_formats.xml.marshaler


@annize.project.file_formats.register_file_format("xml")
class FileFormat(annize.project.file_formats.FileFormat):
    """
    XML file format.
    """

    def __init__(self):
        super().__init__()
        self.__node_readers = _node_readers()

    def load_file_node(self, file, inspector):
        return self.__new_file_node(file, file, inspector)

    def new_file_node(self, file, inspector):
        return self.__new_file_node(file, io.BytesIO(b'<a:project xmlns:a="annize"></a:project>'), inspector)

    def deserialize_node(self, s, inspector):
        result = self.__new_file_node("/dev/null",
                                      io.BytesIO(f'<a:project xmlns:a="annize">{s.decode()}</a:project>'.encode()),
                                      inspector).children[0].clone()

        if not isinstance(result, annize.project.ArgumentNode):
            raise ValueError("invalid node")

        result.arg_name = None
        return result

    def __new_file_node(self, file: hallyd.fs.TInputPath, content_source: io.BytesIO|hallyd.fs.TInputPath,
                        inspector: "annize.project.inspector.FullInspector") -> annize.project.FileNode:
        """
        Create and return a new file node.

        :param file: The file path to associate to the new file node. This is not always the same as `content_source`.
        :param content_source: The content source.
        :param inspector: The project inspector to use.
        """
        marshaler_ = annize.project.file_formats.xml.marshaler.Marshaler(inspector)
        file_node = annize.project.FileNode(file, marshaler_)
        xml_tree_file_node = lxml.etree.parse(content_source)
        xml_file_node = xml_tree_file_node.getroot()
        marshaler_.initialize(file_node, xml_tree_file_node)

        context = FileFormat.LoadFileContext(file, marshaler_)
        with context.in_xml_element(xml_file_node):
            if xml_file_node.tag != "{annize}project":
                raise RuntimeError(f"invalid root tag: {xml_file_node.tag}")
            if xml_file_node.attrib:
                raise RuntimeError(f"invalid attribute: {tuple(xml_file_node.attrib.keys())[0]}")
            if (xml_file_node.text or "").strip():
                raise RuntimeError(f"text content not allowed there: {xml_file_node.text.strip()}")
            self.__parse_children(context, xml_file_node, file_node)

        return file_node

    def __parse_children(self, context: "FileFormat.LoadFileContext", xml_elements: t.Iterable[lxml.etree.Element],
                         node: annize.project.Node) -> None:
        """
        Parse all children of the given XML element and transfer these data to the given node (e.g. by adding child
        nodes).

        :param context: The load file context.
        :param xml_elements: The XML elements to parse as children (or their parent XML element).
        :param node: The node to extend with the children of :code:`xml_element`.
        """
        for xml_child_element in xml_elements:
            if xml_child_element.tag is lxml.etree.Comment:
                if (xml_child_element.tail or "").strip():
                    raise RuntimeError(f"text content not allowed there: {xml_child_element.tail.strip()}")
                continue

            with context.in_xml_element(xml_child_element):
                for node_representation_handler in self.__node_readers:
                    parsed_child_element = node_representation_handler.read(xml_child_element, context)
                    if parsed_child_element:
                        break
                else:
                    raise RuntimeError(f"unable to find a node reader for: {xml_child_element}")

                context.file_marshaler.set_node_representation(parsed_child_element.node, xml_child_element)

                node.append_child(parsed_child_element.node)
                self.__parse_children(context, parsed_child_element.xml_children,
                                      parsed_child_element.children_target_node)

    #: The prefix of a special attribute value (e.g. references or non-string scalar values).
    #: See also :py:attr:`_ATTRIBUTE_COMMAND_END`.
    _ATTRIBUTE_COMMAND_START = "{"

    #: The postfix of a special attribute value (e.g. references or non-string scalar values).
    #: See also :py:attr:`_ATTRIBUTE_COMMAND_START`.
    _ATTRIBUTE_COMMAND_END = "}"

    class LoadFileContext:
        """
        Keeps some state info for the procedure of loading a file node (:py:meth:`FileFormat.load_file_node`), mostly in
        order to generate useful error messages (and some trivial things like access to the marshaler).
        """

        def __init__(self, file: hallyd.fs.TInputPath,
                     marshaler: "annize.project.file_formats.xml.marshaler.Marshaler"):
            self.__file = hallyd.fs.Path(file)
            self.__file_marshaler = marshaler
            self.__current_xml_element = None
            self.__consumed_in_error_report = False

        @property
        def file_marshaler(self) -> "annize.project.file_formats.xml.marshaler.Marshaler":
            return self.__file_marshaler

        def __str__(self):
            result = f"in {self.__file}"
            if self.__current_xml_element is not None:
                result += f" (around: {self.__xml_element_str(self.__current_xml_element)})"
            return result

        @contextlib.contextmanager
        def in_xml_element(self, xml_element: lxml.etree.Element):
            original_xml_element = self.__current_xml_element
            self.__current_xml_element = xml_element
            try:
                yield
            except Exception as ex:
                if not self.__consumed_in_error_report:
                    self.__consumed_in_error_report = True
                    raise annize.project.ParserError(f"reading project definition failed {self}: {ex}") from ex
                raise
            finally:
                self.__current_xml_element = original_xml_element

        @staticmethod
        def __xml_element_str(xml_element: lxml.etree.Element, *, max_length: int = 100) -> str:
            node_str = lxml.etree.tostring(xml_element).decode().strip().replace("\r", "").replace("\n", "\u21b5")
            if len(node_str) > max_length:
                node_str = node_str[:max_length-1] + "\u1801"
            return node_str


class NodeReader(abc.ABC):
    """
    Node readers are responsible for reading the XML representation of nodes.
    """

    @abc.abstractmethod
    def read(self, xml_element: lxml.etree.Element,
             context: FileFormat.LoadFileContext) -> "NodeReader.ReadResult|None":
        """
        Read the given XML representation of a node and return a result if this reader was able to understand the
        representation, or :py:code:`None` otherwise.

        :param xml_element: The XML element to read.
        :param context: The context. Only needed in particular situations.
        """

    @dataclasses.dataclass(frozen=True)
    class ReadResult:
        """
        The result of :py:meth:`NodeReader.read`.
        """

        #: The result node.
        node: annize.project.Node

        #: The XML elements to parse in order to reach further children of :py:attr:`children_target_node`.
        xml_children: t.Sequence[lxml.etree.Element]

        #: The node that shall receive the children coming from :py:attr:`xml_children`. This is not always the same as
        #: :py:attr:`node`.
        children_target_node: annize.project.Node


def _node_readers() -> t.Sequence["NodeReader"]:
    """
    Create and return all node readers.
    """
    import annize.project.file_formats.xml.node_representation_handlers.ignore_unavailable_feature as _ignore_unavailable_feature
    import annize.project.file_formats.xml.node_representation_handlers.object as _object
    import annize.project.file_formats.xml.node_representation_handlers.reference as _reference
    import annize.project.file_formats.xml.node_representation_handlers.scalar_value as _scalar_value

    return (_ignore_unavailable_feature.NodeReader(), _object.NodeReader(), _reference.NodeReader(),
            _scalar_value.NodeReader())
