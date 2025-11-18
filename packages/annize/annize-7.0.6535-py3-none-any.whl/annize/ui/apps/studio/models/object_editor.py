# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import logging
import traceback

import hallyd
import klovve.variable
import pyperclip

import annize.i18n
import annize.project.file_formats
import annize.project.loader
import annize.ui.apps.studio.models.project_config
import annize.ui.apps.studio.models.problems_list
import annize.ui.apps.studio.views.add_child
import annize.ui.apps.studio.views.choose_reference_target
import annize.ui.apps.studio.views.object_help


_logger = logging.getLogger(__name__)


class ObjectEditor(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    project: "annize.project.ProjectNode|None" = klovve.ui.property()

    node: "annize.project.Node|None" = klovve.model.property()

    is_expanded: bool = klovve.model.property(initial=False)

    title: str = klovve.model.property(initial="")

    problems_by_node: dict["annize.project.Node", list["annize.ui.apps.studio.models.problems_list.Problem"]] = klovve.ui.property(initial=lambda: {})

    coloration: klovve.views.ObjectEditor.Coloration = klovve.model.property(initial=klovve.views.ObjectEditor.Coloration.GRAY)

    properties: list[tuple[str, list["ObjectEditor"], bool]] = klovve.model.list_property()

    all_actions: list[tuple[str, str, bool]] = klovve.model.list_property()

    _inited: bool = klovve.model.property(initial=False)

    def _(self):
        if not self.project:
            return

        with klovve.variable.no_dependency_tracking():
            inited = self._inited
        if self.node and self.annize_application and not inited:
            change_text = f"({annize.i18n.tr("an_UI_change")})"
            with klovve.variable.no_dependency_tracking():
                self._inited = True

            if isinstance(self.node, annize.project.ProjectNode):
                result = annize.i18n.tr("an_UI_projectFiles")
            elif isinstance(self.node, annize.project.FileNode):
                project_path = annize.project.loader.project_root_directory(self.project.annize_config_directory)
                node_path = hallyd.fs.Path(self.node.path)
                result = f"{node_path.relative_to(project_path, strict=False)}"
            elif isinstance(self.node, annize.project.ObjectNode):
                result = f"🗂️ {self.node.feature}.{self.node.type_name}"
            elif isinstance(self.node, annize.project.ScalarValueNode):
                result = f" 🔤 {self.node.value!r}"
            elif isinstance(self.node, annize.project.ReferenceNode):
                result = f"🖇️ {annize.i18n.tr("an_UI_referenceTo").format(r=repr(self.node.reference_key))}"
            elif isinstance(self.node, annize.project.IgnoreUnavailableFeatureNode):
                result = f" ✴️ {annize.i18n.tr("an_UI_ignoreUnavailableFeature").format(f=repr(self.node.feature))}"
            else:
                result = "?"
            aux_pieces = []
            if isinstance(self.node, annize.project.ArgumentNode):
                if self.node.name:
                    aux_pieces.append(self.node.name)
                if self.node.append_to:
                    aux_pieces.append(f"⇢{self.node.append_to}")
            if aux := ", ".join(aux_pieces):
                result += f" ({aux})"
            self.title = result

            result = []
            node = self.node
            tr = annize.i18n.tr
            result.append((f"*️⃣  {tr("an_UI_openInNewTab")}", "open_in_new_tab", True))
            if isinstance(node, annize.project.FileNode):
                result.append((f"⚙ {tr("an_UI_specifyFeatureUnavailable")}", "specify_feature_unavailable", True))
            if isinstance(node, annize.project.ArgumentNode):
                result.append((f"🏷️ {tr("an_UI_nameIs").format(n=node.name)} {change_text}"
                               if node.name else f"🏷️ {tr("an_UI_assignName")}",
                               "change_name", False))
                result.append((f"⇢ {tr("an_UI_usedAsArgumentFor").format(a=repr(node.append_to))}"
                               if node.append_to else f"⇢ {tr("an_UI_useAsArgumentFor")}",
                               "change_append_to", not node.append_to))
                if node.append_to:
                    result.append((f"↕️ {tr("an_UI_jumpToArgumentTarget").format(n=repr(node.append_to))}",
                                   "jump_to_append_to_target", False))
            if isinstance(node, annize.project.ScalarValueNode):
                result.append((f"🖊️ {tr("an_UI_setValue")}", "set_value", False))
            if isinstance(node, annize.project.ReferenceNode):
                result.append((f"️⛓️ {tr("an_UI_setReferenceTarget")}", "set_reference_target", False))
                if self.node.reference_key:
                    result.append((f"↕️ {tr("an_UI_jumpToReferenceTarget").format(n=repr(node.reference_key))}",
                                   "jump_to_reference_target", False))
            if isinstance(node, annize.project.IgnoreUnavailableFeatureNode):
                result.append((f"⚙️ {tr("an_UI_setIgnoreUnavailableFeatureName").format(f=repr(node.feature))}"
                               f" {change_text}", "change_on_feature_unavailable_node_feature", False))
            if isinstance(node, annize.project.ArgumentNode):
                result.append((f"🗐 {tr("an_UI_copyToClipboard")}", "clipboard_copy", True))
                result.append((f"✄ {tr("an_UI_cutToClipboard")}", "clipboard_cut", True))
            if isinstance(node, annize.project.ObjectNode):
                result.append((f"❓ {tr("an_UI_objectHelp")}", "object_help", True))
            self.all_actions = result

            node_properties = {}
            if not isinstance(self.node, (annize.project.ScalarValueNode,
                                          annize.project.ReferenceNode,
                                          annize.project.IgnoreUnavailableFeatureNode)):
                for matching in self.annize_application.inspector.match_arguments(self.node).all():
                    node_properties[matching.arg_name] = [], matching.allows_multiple_args or len(matching.nodes) == 0
                    for child_node in matching.nodes:
                        node_properties[matching.arg_name][0].append(ObjectEditor(
                            annize_application=self.annize_application, node=child_node,
                            problems_by_node=self.bind.problems_by_node,
                            project=self.project))
            self.properties = [(name, children, children_can_be_added_by_user)
                               for name, (children, children_can_be_added_by_user) in node_properties.items()]

            if isinstance(self.node, annize.project.FileNode):
                coloration = klovve.views.ObjectEditor.Coloration.GRAY
            elif isinstance(self.node, annize.project.ObjectNode):
                coloration = klovve.views.ObjectEditor.Coloration.BLUE
            elif isinstance(self.node, annize.project.ScalarValueNode):
                coloration = klovve.views.ObjectEditor.Coloration.GREEN
            elif isinstance(self.node, annize.project.ReferenceNode):
                coloration = klovve.views.ObjectEditor.Coloration.MAGENTA
            elif isinstance(self.node, annize.project.IgnoreUnavailableFeatureNode):
                coloration = klovve.views.ObjectEditor.Coloration.RED
            else:
                coloration = klovve.views.ObjectEditor.Coloration.GRAY
            self.coloration = coloration

            self.node.add_change_handler(self.__handle_node_changed, also_watch_children=False)  # TODO  who removes?
    __update_node_ui: None = klovve.model.computed_property(_)

    def _(self):
        result = []
        has_advanced_actions = False
        for action_title, action_name, action_is_advanced in self.all_actions:
            if action_is_advanced:
                has_advanced_actions = True
            else:
                result.append((action_title, action_name))
        if has_advanced_actions:
            result.append((annize.i18n.tr("an_UI_more"), "show_advanced_actions"))
        return result
    actions: list[tuple[str, str, bool]] = klovve.model.computed_list_property(_)

    def _(self):
        return not isinstance(self.node, annize.project.ProjectNode)
    is_removable_by_user: bool = klovve.model.computed_property(_)

    async def handle_action_triggered(self, triggering_view: klovve.ui.View, action_name: str) -> None:

        class AdvancedActionsDialog(klovve.ui.dialog.Dialog):

            def __init__(self, actions, **kwargs):
                super().__init__(**kwargs)
                self.__actions = actions

            def view(self):
                return klovve.views.VerticalBox(
                    items=[
                        klovve.views.Button(
                            text=action_title,
                            action_name=action_name,
                            horizontal_layout=klovve.ui.Layout(klovve.ui.Align.END),
                            style=klovve.views.Button.Style.LINK)
                        for action_title, action_name in self.__actions])

            @klovve.event.event_handler
            def __handle_action_triggered(self, event: klovve.app.Application.ActionTriggeredEvent):
                self.close(event.action_name)

        if action_name == "show_advanced_actions":
            advanced_actions = [(action_title, action_name) for action_title, action_name, action_is_advanced
                                in self.all_actions if action_is_advanced]
            if advanced_action_name := await self.annize_application.dialog(
                    AdvancedActionsDialog, (advanced_actions,),
                    is_closable_by_user=True, view_anchor=triggering_view):
                await self.handle_action_triggered(triggering_view, advanced_action_name)
        if action_name == "open_in_new_tab":
            self.annize_application.main_model.project_configs.append(
                annize.ui.apps.studio.models.project_config.ProjectConfig(
                    annize_application=self.bind.annize_application,
                    label=self.bind.title,
                    object_editor=self))
        if action_name == "specify_feature_unavailable":
            if (ignore_feature_name := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyIgnoreFeature")),
                    view_anchor=triggering_view)) is not None:
                new_node = annize.project.IgnoreUnavailableFeatureNode()
                new_node.feature = ignore_feature_name
                self.node.append_child(new_node)
                self.__snapshot()
        if action_name == "change_name":
            if (new_node_name := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyNewName").format(t=repr(self.title)),
                    suggestion=self.node.name or ""),
                    view_anchor=triggering_view)) is not None:
                self.node.name = new_node_name or None
                self.__snapshot()
        if action_name == "change_append_to":
            append_to_targets = self.annize_application.inspector.possible_append_to_targets_for_node(self.node)
            append_to_target_tuples = [("", None)]
            for append_to_target in append_to_targets:
                append_to_target_type = self.annize_application.inspector.argument_type_for_argument_node(append_to_target)
                details = append_to_target_type.__name__ if append_to_target_type else None
                append_to_target_tuples.append((append_to_target.name, details))
            if (new_append_to := await self.annize_application.dialog(
                    annize.ui.apps.studio.views.choose_reference_target.ChooseReferenceTargetDialog,
                    (self.annize_application, annize.i18n.tr("an_UI_chooseAppendToTarget").format(t=repr(self.title)),
                     append_to_target_tuples),
                    view_anchor=triggering_view,
                    is_closable_by_user=True)) is not None:
                self.node.append_to = new_append_to or None
                self.__snapshot()
        if action_name == "set_value":
            new_value = self.node.value
            converter = None
            if new_value is None:
                pass
            elif isinstance(new_value, bool):
                self.node.value = not self.node.value
                self.__snapshot()
            elif isinstance(new_value, int):
                converter = int
            elif isinstance(new_value, float):
                converter = float
            elif isinstance(new_value, str):
                converter = str
            if converter is not None:
                while True:
                    if (new_value := await self.annize_application.dialog(klovve.views.interact.TextInput(
                            message=annize.i18n.tr("an_UI_pleaseSpecifyNewValue"),
                            suggestion=str(new_value)),
                            view_anchor=triggering_view)) is None:
                        break
                    try:
                        new_value_ = converter(new_value)
                    except ValueError:
                        continue
                    self.node.value = new_value_
                    self.__snapshot()
                    break
        if action_name == "set_reference_target":
            arg_name = self.node.arg_name
            if not arg_name:
                if old_reference_type := self.annize_application.inspector.argument_type_for_argument_node(self.node):
                    arg_names = ()
                    if (parent_node_type := self.annize_application.inspector.argument_type_for_argument_node(self.node.parent)) is not None:
                        arg_names = self.annize_application.inspector.possible_argument_names_for_child_in_parent(
                                                                                    old_reference_type, parent_node_type)
                    if len(arg_names) > 0:
                        arg_name = arg_names[0]
            if arg_name:
                reference_targets = self.annize_application.inspector.possible_reference_targets_for_node_argument(
                    self.node.parent, arg_name)
            else:
                reference_targets = self.annize_application.inspector.all_named_nodes(self.node.project)

            reference_target_tuples = []
            for reference_target in reference_targets:
                reference_target_type = self.annize_application.inspector.argument_type_for_argument_node(reference_target)
                details = reference_target_type.__name__ if reference_target_type else None
                reference_target_tuples.append((reference_target.name, details))

            if (reference_target_name := await self.annize_application.dialog(
                    annize.ui.apps.studio.views.choose_reference_target.ChooseReferenceTargetDialog,
                    (self.annize_application, annize.i18n.tr("an_UI_chooseReferenceTarget"), reference_target_tuples),
                    view_anchor=triggering_view,
                    is_closable_by_user=True)) is not None:
                self.node.reference_key = reference_target_name
                self.__snapshot()
        if action_name == "jump_to_reference_target":
            if reference_target_node := self.annize_application.inspector.resolve_reference_node(self.node):
                self.annize_application.jump_to_node(reference_target_node)
        if action_name == "jump_to_append_to_target":
            if append_to_target_node := self.annize_application.inspector.node_by_name(
                    self.node.append_to, self.node.project):
                self.annize_application.jump_to_node(append_to_target_node)
        if action_name == "change_on_feature_unavailable_node_feature":
            if (new_feature := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyOfuFeature"),
                    suggestion=self.node.feature or ""),
                    view_anchor=triggering_view)) is not None:
                self.node.feature = new_feature or ""
                self.__snapshot()
        if action_name in ("clipboard_copy", "clipboard_cut"):
            node_bytes = annize.project.file_formats.file_format("xml").serialize_node(self.node)
            try:
                pyperclip.copy(node_bytes.decode())
            except Exception:
                _logger.debug(traceback.format_exc())
            if action_name == "clipboard_cut":
                self.node.parent.remove_child(self.node)
                self.__snapshot()
        if action_name == "object_help":
            text = annize.i18n.tr("an_UI_noDocAvailable")
            if object_type := self.annize_application.inspector.argument_type_for_argument_node(self.node):
                object_type_info = self.annize_application.inspector.creatable_type_info(object_type)
                if text_body := self.annize_application.inspector.type_documentation(object_type, with_parameters=True):
                    text = (f"{f"{object_type_info.feature_name}." if object_type_info.feature_name else ""}"
                            f"{object_type_info.type_short_name}:\n\n{text_body}")
            await self.annize_application.dialog(
                annize.ui.apps.studio.views.object_help.ObjectHelpDialog, (text,),
                view_anchor=triggering_view,
                is_closable_by_user=True)

    async def handle_remove_requested(self, triggering_view: klovve.ui.View) -> None:
        if await self.annize_application.dialog(klovve.views.interact.MessageYesNo(
                message=annize.i18n.tr("an_UI_doYouWantToRemove").format(t=repr(self.title))),
                view_anchor=triggering_view):
            self.node.parent.remove_child(self.node)
            self.__snapshot()

    async def handle_add_child_requested(self, triggering_view: klovve.ui.View, property_name: str) -> None:
        if isinstance(self.node, annize.project.ProjectNode):
            if not (name := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_enterFileName")),
                    view_anchor=triggering_view)):
                return

            new_node = annize.project.file_formats.file_format("xml").new_file_node(
                self.node.children[0].path.parent / f"project.{name}.xml", self.annize_application.inspector)

        else:
            suggested_types = self.annize_application.inspector.creatables_for_node_argument(self.node, property_name)

            child_type_tuples = [(suggested_type.type_info.feature_name, suggested_type.type_info.type_short_name, suggested_type.type_info, suggested_type)
                                 for suggested_type in suggested_types]

            try:
                clipboard_str = pyperclip.paste()
            except Exception:
                clipboard_str = None

            clipboard_node = None
            if isinstance(clipboard_str, str):
                for file_format_name in annize.project.file_formats.all_file_format_names():
                    try:
                        clipboard_node = annize.project.file_formats.file_format(file_format_name).deserialize_node(
                            clipboard_str.encode(), self.annize_application.inspector)
                        break
                    except Exception:
                        pass

            if (child_type_tuple := await self.annize_application.dialog(
                    annize.ui.apps.studio.views.add_child.AddChildDialog,
                    (self.annize_application, child_type_tuples, clipboard_node is not None),
                    view_anchor=triggering_view,
                    is_closable_by_user=True)) is None:
                return

            if child_type_tuple == "reference":
                new_node = annize.project.ReferenceNode()
                if property_name:
                    new_node.arg_name = property_name

            elif child_type_tuple == "paste":
                new_node = clipboard_node

            else:
                newtype = child_type_tuple[2]

                if newtype.feature_name:
                    new_node = annize.project.ObjectNode(newtype.feature_name, newtype.type_short_name)
                    for arg_name, arg_value in child_type_tuple[3].kwargs.items():
                        arg_node = annize.project.ScalarValueNode()
                        arg_node.arg_name = arg_name
                        arg_node.value = arg_value
                        new_node.append_child(arg_node)
                else:
                    new_node = annize.project.ScalarValueNode()
                    if newtype.type == type(None):
                        new_node.value = None
                    elif newtype.type == bool:
                        new_node.value = False
                    elif newtype.type == int:
                        new_node.value = 0
                    elif newtype.type == float:
                        new_node.value = 0.0
                    elif newtype.type == str:
                        new_node.value = ""
                    else:
                        raise RuntimeError(f"invalid node type: {newtype.type}")

            if property_name:
                new_node.arg_name = property_name

        self.node.append_child(new_node)
        self.__snapshot()

    def __handle_node_changed(self, event: annize.project.Node.ChangeEvent) -> None:
        # TODO
        self.node, node = None, self.node
        self._inited = False
        self.node = node

    def __snapshot(self):
        self.annize_application.main_model.snapshot()
