# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage documentation section.
"""
import typing as t

import annize.features._pidev.i18n
import annize.features.homepage.common
import annize.flow.run_context
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, documentation: t.Sequence[annize.features.documentation.common.Document],
                 head=annize.features._pidev.i18n.TrStr.tr("an_HP_Head_Documentation"), sort_index=30_000):
        super().__init__(head=head, sort_index=sort_index)
        self.__documentation = tuple(documentation)

    def pre_process_generate(self, info):
        info.custom_arg = {}
        for document in self.__documentation:
            document_name = annize.flow.run_context.object_name(document)
            document.generate_all_cultures(annize.features.documentation.common.HtmlOutputSpec()).file.path().move_to(
                info.document_root_directory(document_name))
            info.custom_arg[document] = f"{info.document_root_url}{document_name}/index.html"

    def generate_content(self, info):
        if len(self.__documentation) > 0:
            content = annize.features.homepage.common.HomepageSection.Content()
            content.append_rst(annize.features._pidev.i18n.tr("an_HP_Doc_DocsAvailable"))
            for document in self.__documentation:
                generated_document_url = info.custom_arg[document]
                content.append_rst(f"`{getattr(document, "title", generated_document_url)}"
                                   f" <{generated_document_url}>`_")
            return content
        return None
