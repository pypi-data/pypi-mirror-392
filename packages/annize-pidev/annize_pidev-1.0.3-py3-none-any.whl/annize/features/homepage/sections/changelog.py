# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage changelog section.
"""
import datetime

import annize.features._pidev.i18n
import annize.features.changelog.common
import annize.features.documentation.sphinx.rst
import annize.features.homepage.common
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, changelog: annize.features.changelog.common.Changelog|None,
                 head=annize.features._pidev.i18n.TrStr.tr("an_HP_Head_Changelog"), sort_index=60_000):
        super().__init__(head=head, sort_index=sort_index)
        self.__changelog = changelog

    def generate_content(self, info):
        changelog = self.__changelog or annize.features.changelog.common.default_changelog()
        if not changelog:
            return None

        entries = sorted(changelog.entries, key=lambda e: (e.time, e.version), reverse=True)
        if len(entries) == 0:
            return None

        content = annize.features.homepage.common.HomepageSection.Content()
        now = datetime.datetime.now()
        for i_entry, entry in enumerate(entries):
            if (i_entry > 0) and entry.time and (now - entry.time > datetime.timedelta(days=365)):
                break
            entry_head = []
            if entry.time:
                entry_head.append(entry.time.date().strftime("%x"))
            if entry.version:
                entry_head.append(str(entry.version))
            if len(entry_head) == 0:
                raise ValueError("Changelog entries must have a `time` or a `version`")
            content.append_rst(annize.features.documentation.sphinx.rst.heading(
                ", ".join(entry_head), level=0))
            for entry_item in entry.items:
                content.append_rst("- " + str(entry_item.text).strip().replace("\n", "  \n"))

        return content
