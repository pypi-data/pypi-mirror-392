# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based PDF documentation output.
"""
import os
import subprocess

import annize.features.documentation.sphinx.output.common
import annize.fs


@annize.features.documentation.sphinx.output.common.register_output_generator
class PdfOutputGenerator(annize.features.documentation.sphinx.output.common.OutputGenerator):
    """
    PDF documentation output generator.
    """

    @classmethod
    def is_compatible_for(cls, output_spec):
        return isinstance(output_spec, annize.features.documentation.common.PdfOutputSpec)

    def format_name(self):
        return "latex"

    def postprocess(self, out_dir):
        subprocess.check_call(("make",), cwd=out_dir)
        for out_dir_child in out_dir.children():
            if out_dir_child.name.endswith(".pdf"):
                return out_dir_child
        raise RuntimeError("no PDF found in build output")
