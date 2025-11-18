# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.i18n
import annize.project.inspector
import annize.ui.apps.studio.models.choose_reference_target


class ChooseReferenceTarget(
    klovve.ui.ComposedView[annize.ui.apps.studio.models.choose_reference_target.ChooseReferenceTarget]):

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                klovve.views.Label(
                    text=self.model.bind.head_text,
                    vertical_layout=klovve.ui.Layout(klovve.ui.Align.START),
                    margin=klovve.ui.Margin(all_em=0.4)),
                klovve.views.List(
                    items=self.model.bind.reference_targets,
                    item_label_func=lambda object_type: f"{object_type[0]}"
                                                        f"{f" ({object_type[1]})" if object_type[1] else ""}" if object_type[0] else annize.i18n.tr("an_UI_none"),
                    selected_item=self.bind._selected_item),
                klovve.views.Button(
                    text=annize.i18n.tr("an_UI_OK"),
                    action_name="ok",
                    is_enabled=self.bind._has_selected_item,
                    horizontal_layout=klovve.ui.Layout(klovve.ui.Align.END),
                    margin=klovve.ui.Margin(all_em=0.4, left_em=0.6))])

    _selected_item = klovve.ui.property()

    def _(self):
        return self._selected_item is not None
    _has_selected_item: bool = klovve.ui.computed_property(_)

    @klovve.event.action("ok")
    def __handle_ok_clicked(self, event):
        event.stop_processing()
        self.trigger_event(klovve.app.BaseApplication.ActionTriggeredEvent(self, self._selected_item[0]))


class ChooseReferenceTargetDialog(klovve.ui.dialog.Dialog):

    def __init__(self, annize_application, head_text, reference_targets: list[tuple[str, str|None]], **kwargs):
        super().__init__(**kwargs)
        self.__annize_application = annize_application
        self.__head_text = head_text
        self.__reference_targets = tuple(reference_targets)

    def view(self):
        return ChooseReferenceTarget(model=annize.ui.apps.studio.models.choose_reference_target.ChooseReferenceTarget(
            annize_application=self.__annize_application,
            head_text=self.__head_text,
            reference_targets=self.__reference_targets))

    @klovve.event.event_handler
    def __handle_action_triggered(self, event: klovve.app.Application.ActionTriggeredEvent):
        event.stop_processing()
        self.close(event.action_name)
