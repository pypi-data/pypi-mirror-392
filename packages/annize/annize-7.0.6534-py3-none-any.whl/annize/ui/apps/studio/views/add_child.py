# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.i18n
import annize.project.inspector
import annize.ui.apps.studio.models.add_child


class AddChild(klovve.ui.ComposedView[annize.ui.apps.studio.models.add_child.AddChild]):

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                klovve.views.Label(
                    text=annize.i18n.tr("an_UI_chooseElementTypeToAdd"),
                    vertical_layout=klovve.ui.Layout(klovve.ui.Align.START),
                    margin=klovve.ui.Margin(all_em=0.4)),
                klovve.views.HorizontalBox(
                    items=[
                        klovve.views.List(
                            items=self.bind._visible_object_types,
                            item_label_func=lambda object_type: f"{f"{object_type[0]}." if object_type[0] else ""}"
                                                                f"{object_type[1]}"
                                                                f"{f".{object_type[3].name}" if object_type[3].name else ""}",
                            selected_item=self.bind._selected_item),
                        klovve.views.Scrollable(
                            body=klovve.views.Label(
                                text=self.bind._doc_text,
                                horizontal_layout=klovve.ui.Layout(klovve.ui.Align.FILL, min_size_em=13),
                                margin=klovve.ui.Margin(left_em=0.6)),
                            vertical_layout=klovve.ui.Layout(min_size_em=13))]),
                klovve.views.HorizontalBox(
                    items=[
                        klovve.views.TextField(
                            text=self.bind._search_term,
                            hint_text="\U0001F50D",
                            horizontal_layout=klovve.ui.Layout(klovve.ui.Align.START)),
                        klovve.views.HorizontalBox(),
                        klovve.views.Button(
                            text=annize.i18n.tr("an_UI_pasteFromClipboard"),
                            action_name="paste",
                            is_visible=self.model.bind.allow_paste_from_clipboard,
                            horizontal_layout=klovve.ui.Layout(klovve.ui.Align.END)),
                        klovve.views.Button(
                            text=annize.i18n.tr("an_UI_referenceToExisting"),
                            action_name="reference",
                            horizontal_layout=klovve.ui.Layout(klovve.ui.Align.END)),
                        klovve.views.Button(
                            text=annize.i18n.tr("an_UI_OK"),
                            action_name="ok",
                            is_enabled=self.bind._has_selected_item,
                            horizontal_layout=klovve.ui.Layout(klovve.ui.Align.END),
                            margin=klovve.ui.Margin(left_em=0.6))],
                    margin=klovve.ui.Margin(all_em=0.4))])

    _selected_item = klovve.ui.property()

    _search_term: str = klovve.ui.property(initial="")

    def _(self):
        if not self.model:
            return ()
        return self.model.object_types
    _all_object_types = klovve.ui.computed_list_property(_)

    def _(self):
        result = []
        search_terms = [_.lower() for _ in self._search_term.split(" ") if _]
        for object_type in self._all_object_types:
            if search_terms:
                matching = False
                for search_term in search_terms:
                    if search_term in (object_type[0] or "").lower() or search_term in object_type[1].lower():
                        matching = True
                        break
                if not matching:
                    continue
            result.append(object_type)
        return result
    _visible_object_types = klovve.ui.computed_list_property(_)

    def _(self):
        return self._selected_item is not None
    _has_selected_item: bool = klovve.ui.computed_property(_)

    def _(self):
        if self._selected_item is None or not self.model:
            return annize.i18n.tr("an_UI_chooseTypeToContinue")
        text_body = (self.model.annize_application.inspector.type_documentation(self._selected_item[2].type)
                     or annize.i18n.tr("an_UI_noDocAvailable"))
        return (f"{f"{self._selected_item[0]}." if self._selected_item[0] else ""}{self._selected_item[1]}:\n\n"
                f"{text_body}")
    _doc_text: str = klovve.ui.computed_property(_)

    @klovve.event.action("ok")
    def __handle_ok_clicked(self, event):
        event.stop_processing()
        self.trigger_event(klovve.app.BaseApplication.ActionTriggeredEvent(
            self, str(self._all_object_types.index(self._selected_item))))


class AddChildDialog(klovve.ui.dialog.Dialog):

    def __init__(self, annize_application, object_types: list[tuple[str|None, str, annize.project.inspector.FullInspector.CreatableTypeInfo, annize.project.inspector.FullInspector.CreatableInfo]], allow_paste_from_clipboard: bool, **kwargs):
        super().__init__(**kwargs)
        self.__annize_application = annize_application
        self.__object_types = tuple(object_types)
        self.__allow_paste_from_clipboard = allow_paste_from_clipboard

    def view(self):
        return AddChild(model=annize.ui.apps.studio.models.add_child.AddChild(
            annize_application=self.__annize_application,
            allow_paste_from_clipboard=self.__allow_paste_from_clipboard,
            object_types=self.__object_types))

    @klovve.event.event_handler
    def __handle_action_triggered(self, event: klovve.app.Application.ActionTriggeredEvent):
        event.stop_processing()
        self.close("reference" if event.action_name == "reference" else "paste" if event.action_name == "paste" else self.__object_types[int(event.action_name)])
