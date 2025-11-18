# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.i18n
import annize.project.inspector
import annize.ui.apps.studio.models.object_help


class ObjectHelp(klovve.ui.ComposedView[annize.ui.apps.studio.models.object_help.ObjectHelp]):

    def compose(self):
        return klovve.views.Scrollable(
            body=klovve.views.Label(text=self.model.bind.text),
            horizontal_layout=klovve.ui.Layout(min_size_em=20),
            vertical_layout=klovve.ui.Layout(min_size_em=20))


class ObjectHelpDialog(klovve.ui.dialog.Dialog):

    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self.__text = text

    def view(self):
        return ObjectHelp(model=annize.ui.apps.studio.models.object_help.ObjectHelp(text=self.__text))
