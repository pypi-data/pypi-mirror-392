# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.project.inspector


class AddChild(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    object_types: list[tuple[str|None, str, annize.project.inspector.FullInspector.CreatableTypeInfo, annize.project.inspector.FullInspector.CreatableInfo]] = klovve.model.list_property()

    allow_paste_from_clipboard: bool = klovve.model.property(initial=False)
