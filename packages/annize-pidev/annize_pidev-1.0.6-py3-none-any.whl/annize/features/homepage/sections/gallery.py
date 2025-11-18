# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage media gallery section.
"""
import typing as t

import annize.features._pidev.i18n
import annize.features.documentation.sphinx.rst
import annize.features.homepage.common
import annize.features.media_galleries
import annize.flow.run_context
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, head=annize.features._pidev.i18n.TrStr.tr("an_HP_Head_Gallery"), sort_index=50_000,
                 media_galleries: t.Sequence[annize.features.media_galleries.Gallery]):
        super().__init__(head=head, sort_index=sort_index)
        self.__media_galleries = tuple(media_galleries)

    def pre_process_generate(self, info):
        info.custom_arg = {}
        for gallery in self.__media_galleries:
            gallery_name = annize.flow.run_context.object_name(gallery)
            gallery_dir = info.document_root_directory(gallery_name)
            gallery_dir.mkdir()
            info.custom_arg[gallery] = gallery_items = []
            for item in gallery.items:
                item_file_original = item.file.path()
                item_file = gallery_dir(item_file_original.name)
                item_file_original.copy_to(item_file)
                gallery_items.append((item, f"{info.document_root_url}{gallery_name}/{item_file.name}"))

    def generate_content(self, info):
        if len(self.__media_galleries) == 0:
            return None

        content = annize.features.homepage.common.HomepageSection.Content()
        for gallery in self.__media_galleries:
            if gallery.title:
                content.append_rst(annize.features.documentation.sphinx.rst.heading(gallery.title, level=0))
            gallery_rst = ".. rst-class:: annizedoc-mediagallery\n\n"
            for item, item_url in info.custom_arg[gallery]:
                title_str = str(item.description or "").replace("\n", " ").replace('"', "''")
                gallery_rst += f" `{title_str} <{item_url}#{item.media_type.value}>`__\n"
            content.append_rst(gallery_rst)
        return content
