# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based documentation output.
"""
import abc
import typing as t

import annize.features.documentation.common as documentation
import annize.fs
import annize.i18n

if t.TYPE_CHECKING:
    import annize.features.documentation.sphinx.common as documentationsphinx


_output_generators = []


def register_output_generator(output_generator: type["OutputGenerator"]) -> type["OutputGenerator"]:
    _output_generators.append(output_generator)
    return output_generator


def output_generator(output_spec: documentation.OutputSpec) -> "OutputGenerator|None":
    for output_generator_ in _output_generators:
        if output_generator_.is_compatible_for(output_spec):
            return output_generator_(output_spec)
    return None


class OutputGenerator(abc.ABC):
    """
    Base class for documentation output specifications. See :py:func:`render`.
    """

    def __init__(self, output_spec: documentation.OutputSpec):
        super().__init__()
        self.__output_spec = output_spec

    @property
    def output_spec(self) -> documentation.OutputSpec:
        return self.__output_spec

    @classmethod
    @abc.abstractmethod
    def is_compatible_for(cls, output_spec: documentation.OutputSpec) -> bool:
        pass

    @abc.abstractmethod
    def format_name(self) -> str:
        """
        Returns the Sphinx format name.
        """

    def prepare_generate(self, info: "documentationsphinx.Document.GenerateInfo") -> None:
        pass

    def postprocess(self, out_dir: annize.fs.Path) -> annize.fs.Path:
        return out_dir

    def multi_language_frame(self, document: "documentationsphinx.Document"
                             ) -> documentation.Document.GeneratedAllCulturesResult:
        resultdir = annize.fs.fresh_temp_directory().path
        entrypathsforlanguages = {}
        for culture in document.available_cultures():
            variantresult = document.generate(self.output_spec, culture=culture)
            languagefilename = culture.full_name
            fvariantresult = variantresult.file.path()
            if fvariantresult.is_file():
                nampcs = fvariantresult.name.split(".")
                if len(nampcs) > 1:
                    languagefilename = f"{languagefilename}.{nampcs[-1]}"
            variantdir = resultdir(languagefilename)
            fvariantresult.move_to(variantdir)
            langentrypath = culture.full_name
            if variantresult.entry_path:
                langentrypath += f"/{variantresult.entry_path}"
            entrypathsforlanguages[culture.full_name] = langentrypath
        return documentation.Document.GeneratedAllCulturesResult(resultdir, "", entrypathsforlanguages)
