# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Marshaler`.
"""
import abc
import copy
import dataclasses
import typing as t

import lxml.etree

import annize.project.file_formats.xml
import annize.project.inspector


class Marshaler(annize.project.file_formats.FileFormat.Marshaler):
    """
    Marshaler for XML files.
    """

    def __init__(self, inspector: "annize.project.inspector.FullInspector"):
        """
        :param inspector: The project inspector to use.
        """
        super().__init__()
        self.__file_node = None
        self.__element_tree = None
        self.__node_representations: Marshaler.NodeRepresentations = {}
        self.__inspector = inspector
        self.__node_editors = _node_editors(self.__node_representations)
        self.__indentation = ""

    def add_change(self, change):
        target_node_editor = self._node_editor(change.target_node)
        target_node_editor.expand(NodeEditor.ExpandRequest(change.target_node, self.__node_representations,
                                                           self.__inspector, self.__indentation, change))

        if isinstance(change, annize.project.Node.ChildAddedEvent):
            self.__handle_child_added(change)
        elif isinstance(change, annize.project.Node.ChildRemovedEvent):
            self.__handle_child_removed(change)
        elif isinstance(change, annize.project.Node.PropertyChangedEvent):
            self.__handle_property_changed(change)
        else:
            raise RuntimeError(f"invalid type of change event: {change!r}")

        target_node_editor.compact(NodeEditor.CompactRequest(change.target_node, self.__node_representations,
                                                             self.__inspector))

    def save_file_node(self):
        self.__element_tree.write(self.__file_node.path, encoding="UTF-8")

    def serialize_node(self, node):
        node_representation = self.__node_representations[node]
        if node_representation.attrib_name:
            parent_node_clone = node.parent.clone()
            node_clone = parent_node_clone.children[node.parent.children.index(node)]
            xml_parent_node_clone = copy.deepcopy(self.__node_representations[node.parent].element)
            cloned_node_representations = {parent_node_clone: Marshaler.XmlDocumentLocation(xml_parent_node_clone),
                   node_clone: Marshaler.XmlDocumentLocation(xml_parent_node_clone, node_representation.attrib_name)}

            self._node_editor(node_clone).expand(NodeEditor.ExpandRequest(node_clone, cloned_node_representations,
                                                                          self.__inspector, 4 * " ", None))
            return lxml.etree.tostring(cloned_node_representations[node_clone].element)

        else:
            return lxml.etree.tostring(self.__node_representations[node].element)

    def initialize(self, node: "annize.project.FileNode", xml_tree: lxml.etree.ElementTree) -> None:
        """
        To be called once after creation of the marshaler, with the file node and its XML content.

        :param node: The file node this marshaler is associated to.
        :param xml_tree: The file's XML content.
        """
        self.__file_node = node
        self.__element_tree = xml_tree
        xml_root_element = xml_tree.getroot()
        self.set_node_representation(node, xml_root_element)
        self.__indentation = (xml_root_element.text or "").split("\n")[-1] or 4 * " "

    def set_node_representation(self, node: "annize.project.Node", xml_element: lxml.etree.Element|None, *,
                                 attrib_name: str|None = None) -> None:
        """
        Store the XML representation location for a particular node, so it can be found for later modifications.

        :param node: The node.
        :param xml_element: The XML element, or :code:`None` if the node was removed and has no representation anymore.
        :param attrib_name: The XML element attribute name, or :code:`None` if it is represented by the entire XML
                            element.
        """
        NodeEditor.Request(node, self.__node_representations, self.__inspector).set_node_representation(
            node, xml_element, attrib_name=attrib_name)

    @staticmethod
    def remove_element(xml_element: lxml.etree.Element) -> None:
        """
        Remove an XML element from its parent and correct indentations.

        :param xml_element: The XML element to remove.
        """
        parent_xml_element = xml_element.getparent()
        i_xml_element = parent_xml_element.index(xml_element)
        parent_xml_element.remove(xml_element)
        if not (parent_xml_element.text or "").strip() and len(parent_xml_element) == 0:
            parent_xml_element.text = None
        if len(parent_xml_element) > 0 and len(parent_xml_element) == i_xml_element:
            parent_xml_element[-1].tail = (parent_xml_element[-1].tail or "").rstrip() + (xml_element.tail or "")

    def _node_editor(self, node: annize.project.Node) -> "NodeEditor":
        """
        Return the node editor that can handle the given node.

        :param node: The node.
        """
        for node_editor in self.__node_editors:
            if node_editor.can_handle(node):
                return node_editor
        raise ValueError(f"invalid type of node: {node!r}")

    @staticmethod
    def _indent_element(xml_element: lxml.etree.Element, indentation_slice: str) -> None:
        """
        Fix the indentation of the given XML element (obeying the outer indentation).

        :param xml_element: The XML element to indent.
        :param indentation_slice: One slice of indentation.
        """
        original_indentation = ""
        xml_element_ = xml_element.getparent()
        while xml_element_ is not None:
            xml_element_ = xml_element_.getparent()
            if xml_element_ is not None and "\n" in (xml_element_.text or ""):
                original_indentation = xml_element_.text.split("\n")[-1]
                break

        new_tail = "\n" + indentation_slice + original_indentation
        i_xml_element = xml_element.getparent().index(xml_element)
        if i_xml_element == 0:
            xml_element.getparent().text = (xml_element.getparent().text or "").rstrip() + new_tail
        else:
            xml_element.getparent()[i_xml_element-1].tail = (xml_element.getparent()[i_xml_element-1].tail
                                                             or "").rstrip() + new_tail
        xml_element.tail = (xml_element.tail or "").rstrip() + "\n" + original_indentation

    def __handle_child_added(self, change: annize.project.Node.ChildAddedEvent) -> None:
        target_document_location = self.__node_representations[change.target_node]
        child_node_editor = self._node_editor(change.child_node)

        xml_child_element = lxml.etree.Element(
            child_node_editor.representation_tag(change.child_node),
            nsmap=child_node_editor.representation_namespace_prefix_map(change.child_node))

        target_document_location.element.insert(
            Marshaler.__child_position_to_insertion_index(
                target_document_location.element, change.child_position), xml_child_element)

        self.set_node_representation(change.child_node, xml_child_element)

        Marshaler._indent_element(xml_child_element, self.__indentation)

        for editor_property in child_node_editor.properties():
            self.__handle_property_changed(annize.project.Node.PropertyChangedEvent(
                change.child_node, editor_property.name, None, getattr(change.child_node, editor_property.name)))

        for i, child_child_node in enumerate(change.child_node.children):
            self.add_change(annize.project.Node.ChildAddedEvent(change.child_node, child_child_node, i))

        child_node_editor.compact(NodeEditor.CompactRequest(change.child_node, self.__node_representations,
                                                            self.__inspector))

    def __handle_child_removed(self, change: annize.project.Node.ChildRemovedEvent) -> None:
        self._node_editor(change.child_node).expand(
            NodeEditor.ExpandRequest(change.target_node, self.__node_representations, self.__inspector,
                                     self.__indentation, None))

        Marshaler.remove_element(self.__node_representations[change.child_node].element)

        nodes = [change.child_node]
        while nodes:
            node = nodes.pop()
            self.set_node_representation(node, None)
            nodes += node.children

    def __handle_property_changed(self, change: annize.project.Node.PropertyChangedEvent) -> None:
        target_node_editor = self._node_editor(change.target_node)
        target_node_editor_property = target_node_editor.property_by_name(change.property_name)
        if not target_node_editor_property:
            raise ValueError(f"invalid property on {change.target_node}: {change.property_name}")

        target_node_editor_property.apply_value_to_representation(change.new_value,
                                                                  self.__node_representations[change.target_node])

    @staticmethod
    def __child_position_to_insertion_index(parent_xml_element: lxml.etree.Element, child_node_position: int) -> int:
        """
        Return the insertion index in the children list of a given element and a given child node position (i.e. it
        converts a node index to an XML element index, skipping elements like comments).

        :param parent_xml_element: The parent XML element.
        :param child_node_position: The insertion position in terms of child nodes.
        """
        children_seen = 0
        for i_xml_element, xml_element in enumerate(parent_xml_element):
            if child_node_position == children_seen:
                return i_xml_element

            if not (xml_element.tag is lxml.etree.Comment):
                children_seen += 1

        return len(parent_xml_element)

    @dataclasses.dataclass
    class XmlDocumentLocation:
        """
        An XML document location is an XML element and an optional attribute name.
        """

        #: The XML element.
        element: lxml.etree.Element

        #: The attribute name.
        attrib_name: str|None = None

    #: Node representations.
    type NodeRepresentations = dict[annize.project.Node, Marshaler.XmlDocumentLocation]


class NodeEditor(abc.ABC):
    """
    Node editors are responsible for modification operations on (the XML representation of) nodes.

    - The marshaler owns these handlers; typically an instance per non-abstract subclass. It is assumed that each
      :py:class:`annize.project.Node` can be handled by exactly one handler (see :py:meth:`can_handle`). The typical
      criterion for that is the node type.
    - The marshaler will use this handler for the following operations on the node (after the associated file has been
      read; i.e. only for changes afterward):
      - It will call :py:meth:`representation_tag` and others in order to create representations for new nodes.
      - It will call :py:meth:`properties` for changes on properties of nodes.
      - It will sometimes :py:meth:`expand` and :py:meth:`compact` nodes in order to switch their representation shape.
    """

    def __init__(self, node_representations: Marshaler.NodeRepresentations):
        """
        :param node_representations: The node representations.
        """
        self.__node_representations = node_representations

    @abc.abstractmethod
    def can_handle(self, node: annize.project.Node) -> bool:
        """
        Return whether this node editor can handle the given node.

        :param node: The node.
        """

    def expand(self, request: "NodeEditor.ExpandRequest") -> None:
        """
        Transform the XML representation of the given node into 'expanded' shape. This is always a complete XML element
        (in contrast to an attribute, as it might be in compacted shape).

        In expanded shape, the XML representation is not optimized for readability, but it supports various operations:
        - Before a new node gets added, its parent will be expanded, so the new node's representation can easily be
          added as child to the parent's one. Both involved node representations are XML elements.
        - Before a node gets removed, this node and its parent will be expanded for the same reason.
        - Before a node property gets changed, this node will be expanded. All properties can now be mapped easily to
          attributes of the XML representation.

        After these operations, the caller will :py:meth:`compact` it again.

        There might be a :py:attr:`NodeEditor.ExpandRequest.event`. This allows to make less invasive expansion in cases
        where it is not actually needed. Note: Ignoring this argument would not lead to errors, but is less retaining.

        :param request: The expand request. It contains request information and provides some actions as methods.
        """

    def compact(self, request: "NodeEditor.CompactRequest") -> None:
        """
        Transform the XML representation of the given node into 'compact' shape. This is typically the most compact one.
        See also :py:meth:`expand`.

        Note: This method must not assume that the representation is in expanded shape before. It can be in any shape.

        :param request: The compact request. It contains request information and provides some actions as methods.
        """

    @abc.abstractmethod
    def representation_tag(self, node: annize.project.Node) -> str:
        """
        Return the XML representation's tag for a node.

        :param node: The node.
        """

    def representation_namespace_prefix_map(self, node: annize.project.Node) -> t.Mapping[str|None, str]|None:
        """
        Return the XML representation's namespace prefix map for a node.

        :param node: The node.
        """
        return None

    def properties(self) -> t.Sequence["NodeEditor.Property"]:
        """
        Return all node properties of this node editor.
        """
        return ()

    def property_by_name(self, property_name: str) -> "NodeEditor.Property|None":
        """
        Return a node property of this node editor by name.

        :param property_name: The node property name.
        """
        for editor_property in self.properties():
            if editor_property.name == property_name:
                return editor_property
        return None

    class Property[T](abc.ABC):
        """
        Base class for a node editor property, associated to a particular node property.
        """

        @property
        @abc.abstractmethod
        def name(self) -> str:
            """
            The name of this property (as it is named on the node).
            """

        @abc.abstractmethod
        def apply_value_to_representation(self, value: T, node_representation: Marshaler.XmlDocumentLocation) -> None:
            """
            Apply the given value to a given node representation.

            This method can assume that node's XML representation is 'expanded' (see :py:meth:`NodeEditor.expand`). So
            it should always be a simple mapping to some attribute or the text of that representation.

            :param value: The value to apply.
            :param node_representation: The node representation to apply the value to.
            """

    class SimpleOptionalStringProperty(Property[str|None]):
        """
        A simple node editor property for a :code:`str|None` node property.
        """

        def __init__(self, name: str, attribute_name: str, *, additional_none_values: t.Iterable[str] = ()):
            """
            :param name: The name of this property (as it is named on the node).
            :param attribute_name: The name of the XML element attribute.
            :param additional_none_values: Additional strings (beyond :code:`""`) to be treated as :code:`None`.
            """
            self.__name = name
            self.__attribute_name = attribute_name
            self.__additional_none_values = tuple(additional_none_values)

        @property
        def name(self):
            return self.__name

        def apply_value_to_representation(self, value, node_representation):
            if value and value not in self.__additional_none_values:
                node_representation.element.attrib[self.__attribute_name] = value
            else:
                node_representation.element.attrib.pop(self.__attribute_name, None)

    class Request:
        """
        Base class for a request for some node editor action. It provides some common functionality needed in any
        of them.
        """

        def __init__(self, node: annize.project.Node, node_representations: Marshaler.NodeRepresentations,
                     inspector: "annize.project.inspector.FullInspector"):
            """
            :param node: The node to act on.
            :param node_representations: The node representations.
            :param inspector: The project inspector to use.
            """
            self.__node = node
            self.__node_representations = node_representations
            self.__inspector = inspector

        @property
        def node(self) -> annize.project.Node:
            """
            The node to act on.
            """
            return self.__node

        @property
        def inspector(self) -> "annize.project.inspector.FullInspector":
            """
            The project inspector.
            """
            return self.__inspector

        def node_representation(self, node: annize.project.Node) -> Marshaler.XmlDocumentLocation|None:
            """
            Return the node representation for a given node (or none). See also :py:meth:`set_node_representation`.

            :param node: The node.
            """
            return self.__node_representations.get(node)

        def set_node_representation(self, node: "annize.project.Node", xml_element: lxml.etree.Element|None, *,
                                    attrib_name: str|None = None) -> None:
            """
            Set the node representation for a given node. See also :py:meth:`node_representation`.

            :param node: The node.
            :param xml_element: The XML element.
            :param attrib_name: The (optional) attribute name.
            """
            if xml_element is not None:
                self.__node_representations[node] = Marshaler.XmlDocumentLocation(xml_element, attrib_name or None)
            else:
                self.__node_representations.pop(node, None)

    class ExpandRequest(Request):
        """
        Request object for a :py:meth:`NodeEditor.expand` call.
        """

        def __init__(self, node: annize.project.Node, node_representations,
                     inspector: "annize.project.inspector.FullInspector", indentation_slice: str,
                     event: annize.project.Node.ChangeEvent|None):
            super().__init__(node, node_representations, inspector)
            self.__indentation_slice = indentation_slice
            self.__event = event

        @property
        def event(self) -> annize.project.Node.ChangeEvent|None:
            """
            The event that directly led to the expansion request (or none). This is available in some cases and can then
            be used for being less invasive with the expansion.
            """
            return self.__event

        def indent_element(self, xml_element: lxml.etree.Element) -> None:
            """
            Fix the indentation of the given XML element (obeying the outer indentation).

            :param xml_element: The XML element to indent.
            """
            Marshaler._indent_element(xml_element, self.__indentation_slice)

    class CompactRequest(Request):
        """
        Request object for a :py:meth:`NodeEditor.compact` call.
        """


def _node_editors(node_representations) -> t.Sequence["NodeEditor"]:
    """
    Create and return all node editors.
    """
    import annize.project.file_formats.xml.node_representation_handlers.file as _file
    import annize.project.file_formats.xml.node_representation_handlers.ignore_unavailable_feature as _ignore_unavailable_feature
    import annize.project.file_formats.xml.node_representation_handlers.object as _object
    import annize.project.file_formats.xml.node_representation_handlers.reference as _reference
    import annize.project.file_formats.xml.node_representation_handlers.scalar_value as _scalar_value

    return (_file.NodeEditor(node_representations),
            _ignore_unavailable_feature.NodeEditor(node_representations),
            _object.NodeEditor(node_representations),
            _reference.NodeEditor(node_representations),
            _scalar_value.NodeEditor(node_representations))
