# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve


class ChooseReferenceTarget(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    reference_targets: list[tuple[str, str|None]] = klovve.model.list_property()

    head_text = klovve.model.property(initial="")
