# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Media galleries.
"""
import enum
import mimetypes
import typing as t

import annize.fs
import annize.i18n


class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Gallery:

    class Item:

        def __init__(self, file: annize.fs.FilesystemContent, description: annize.i18n.TrStr|None, 
                     media_type: MediaType):
            self.__file = file
            self.__description = description
            self.__media_type = media_type

        @property
        def file(self) -> annize.fs.FilesystemContent:
            return self.__file

        @property
        def description(self) -> annize.i18n.TrStr|None:
            return self.__description

        @property
        def media_type(self) -> MediaType:
            return self.__media_type

    def __init__(self, *, source: annize.fs.FilesystemContent, title: annize.i18n.TrStr|None):
        self.__source = source
        self.__title = title or annize.i18n.to_trstr("")

    @property
    def items(self) -> list[Item]:
        result = []
        for item_file in self.__source.path().children():
            item_mimetype = mimetypes.guess_type(item_file.name)[0] or "/"
            media_type = {"image": MediaType.IMAGE,
                          "video": MediaType.VIDEO}.get(item_mimetype.split("/")[0])
            if media_type:
                result.append(self.Item(item_file, self._description_for_mediafile(item_file), media_type))
        return result

    @property
    def title(self) -> annize.i18n.TrStr:
        return self.__title

    def _description_for_mediafile(self, item_file: annize.fs.FilesystemContent) -> annize.i18n.TrStr:
        variants = {}
        item_file = annize.fs.Path(item_file)
        for description_file in (_ for _ in item_file.parent.children()
                                 if _.name.startswith(f"{item_file.name}.") and _.name.endswith(".txt")):
            variants[description_file.name[len(item_file.name)+1:-4]] = description_file.read_bytes().decode().strip()

        if (description_file := item_file.parent(f"{item_file.name}.txt")).exists():
            variants["?"] = description_file.read_bytes().decode()  # TODO

        class ATrStr(annize.i18n.TrStr):
            def get_variant(self, culture):
                return variants.get(culture.iso_639_1_language_code, None)

        return ATrStr()
