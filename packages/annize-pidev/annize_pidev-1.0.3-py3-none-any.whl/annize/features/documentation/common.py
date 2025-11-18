# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Documentation. See :py:class:`Document`.
"""
import abc
import typing as t

import annize.fs
import annize.i18n


class Document(abc.ABC):
    """
    Base class for documents. A document is an arbitrary content, available for some cultures. It can either be
    generated for all cultures or for a particular one, with a particular output spec.

    See also :py:class:`annize.features.documentation.sphinx.common.Document`.
    """

    @abc.abstractmethod
    def available_cultures(self) -> t.Sequence[annize.i18n.Culture]:
        """
        The cultures for which this document is available.
        """

    @abc.abstractmethod
    def generate(self, output_spec: "OutputSpec", *,
                 culture: annize.i18n.Culture = annize.i18n.unspecified_culture) -> "GeneratedResult":
        """
        Generate this document for a given culture. See also :py:meth:`generate_all_cultures`.

        :param output_spec: The output spec.
        :param culture: The culture.
        """

    @abc.abstractmethod
    def generate_all_cultures(self, output_spec: "OutputSpec") -> "GeneratedAllCulturesResult":
        """
        Generate this document for all available cultures. See also :py:meth:`generate`.

        :param output_spec: The output spec.
        """

    class GeneratedResult:
        """
        A result from :py:meth:`Document.generate`.
        """

        def __init__(self, file: annize.fs.FilesystemContent, entry_path: str):
            self.__file = file
            self.__entry_path = entry_path

        @property
        def file(self) -> annize.fs.FilesystemContent:
            return self.__file

        @property
        def entry_path(self) -> str:
            return self.__entry_path

        def _set_entry_path(self, entry_path: str) -> None:
            self.__entry_path = entry_path

    class GeneratedAllCulturesResult(GeneratedResult):
        """
        A result from :py:meth:`Document.generate_all_cultures`.
        """

        def __init__(self, file: annize.fs.FilesystemContent, entry_path: str,
                     entry_paths_for_languages: dict[str, str]):
            super().__init__(file, entry_path)
            self.__entry_paths_for_languages = entry_paths_for_languages

        def entry_path_for_language(self, language: str) -> str:
            return self.__entry_paths_for_languages[language]

        @property
        def culture_names(self) -> t.Sequence[str]:
            return tuple(self.__entry_paths_for_languages.keys())


class OutputSpec(abc.ABC):
    """
    Base class for documentation output specifications. Used for :py:meth:`Document.generate` and others.

    See its subclasses in this module.
    """


class HtmlOutputSpec(OutputSpec):
    """
    HTML documentation output.
    """

    def __init__(self, *, is_homepage: bool = False):
        """
        :param is_homepage: If to render output for a homepage with slight different styling and behavior.
        """
        super().__init__()
        self.__is_homepage = is_homepage

    @property
    def is_homepage(self) -> bool:
        return self.__is_homepage


class PdfOutputSpec(OutputSpec):
    """
    PDF documentation output.
    """


class PlaintextOutputSpec(OutputSpec):
    """
    Plaintext documentation output.
    """


class DocumentRendering(annize.fs.FilesystemContent):
    """
    A document rendering, to be generated from a source document and some rendering options.
    """

    def __init__(self, *, document: Document, output_spec: OutputSpec, culture: annize.i18n.Culture|None,
                 filename: str|None):
        """
        :param document: The source document to render.
        :param output_spec: The output spec.
        :param culture: The culture. For a rendering containing all available cultures, set it to :code:`None`.
        :param filename: The result filename. Default: auto-generated.
        """
        super().__init__(self._path)
        self.__document = document
        self.__output_spec = output_spec
        self.__culture = culture
        self.__filename = filename

    def _path(self):
        if self.__culture:
            result = self.__document.generate(self.__output_spec, culture=self.__culture).file.path()
        else:
            result = self.__document.generate_all_cultures(self.__output_spec).file.path()

        if self.__filename:
            original_result, result = result, annize.fs.fresh_temp_directory().path(self.__filename)
            original_result.move_to(result)

        return result
