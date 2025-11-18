# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage about section.
"""
import annize.features._pidev.i18n
import annize.features.base
import annize.features.homepage.common
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, head=annize.features._pidev.i18n.TrStr.tr("an_HP_Head_About"), sort_index=10_000):
        super().__init__(head=head, sort_index=sort_index)

    def generate_content(self, info):
        long_description = annize.features.base.long_description()
        return (annize.features.homepage.common.HomepageSection.Content(rst_text=long_description)
                if long_description else None)
