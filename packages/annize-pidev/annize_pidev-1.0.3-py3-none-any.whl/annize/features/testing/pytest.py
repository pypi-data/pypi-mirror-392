# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
pytest testing.
"""
import os
import subprocess

import annize.features.base
import annize.features.testing.common
import annize.fs


class Test(annize.features.testing.common.Test):

    def __init__(self, *, test_directory: annize.fs.TInputPath, test_sub_directory: annize.fs.TInputPath|None,
                 source_directory: annize.fs.TInputPath):
        super().__init__()
        self.__source_directory = annize.fs.content(source_directory)
        self.__test_directory = annize.fs.content(test_directory)
        self.__test_sub_directory = annize.fs.Path(test_sub_directory or ".")

    def run(self):
        source_directory = self.__source_directory.path()
        test_directory = self.__test_directory.path()
        python_path = f"{os.environ.get("PYTHONPATH", "")}:{test_directory}"
        subprocess.check_call(["pytest", test_directory(self.__test_sub_directory)],
                              cwd=source_directory, env={**os.environb, b"PYTHONPATH": python_path})
