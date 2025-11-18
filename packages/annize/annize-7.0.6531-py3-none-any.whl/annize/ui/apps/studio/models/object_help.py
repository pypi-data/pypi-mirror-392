# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve


class ObjectHelp(klovve.model.Model):

    text: str = klovve.model.property(initial="")
