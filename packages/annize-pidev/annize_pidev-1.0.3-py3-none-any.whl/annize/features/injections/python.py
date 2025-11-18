# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Python injections.
"""
import typing as t

import annize.data
import annize.features.base
import annize.features.injections.common
import annize.fs


class ProjectInfoInjection(annize.features.injections.common.Injection):

    def __init__(self, *, filename: str = "project_info.py", version: annize.data.Version|None):
        super().__init__()
        self.__filename = filename
        self.__version = version

    def inject(self, destination):
        content = ""
        for piece_key, piece_value in (
                ("homepage_url", annize.features.base.homepage_url()),
                ("version", str(self.__version))):
            if piece_value is not None:
                content += f"{piece_key} = {repr(piece_value)}\n"

        destination.mkdir(parents=True, exist_ok=True)
        destination(self.__filename).write_file(content)
