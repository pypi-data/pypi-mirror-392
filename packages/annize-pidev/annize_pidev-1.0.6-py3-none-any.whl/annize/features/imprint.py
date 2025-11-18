# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Imprints.
"""
import annize.flow.run_context
import annize.i18n


class Imprint:

    def __init__(self, *, text: annize.i18n.TrStr):
        self.__text = text

    @property
    def text(self) -> annize.i18n.TrStr:
        return self.__text


def imprint() -> annize.i18n.TrStr:
    for obj in annize.flow.run_context.objects_by_type(Imprint):
        return obj.text
    return ""
