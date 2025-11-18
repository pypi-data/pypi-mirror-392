# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage.
"""
import abc
import dataclasses
import typing as t

import annize.features.base
import annize.features.changelog.common
import annize.features.dependencies.common
import annize.features.documentation.common
import annize.features.documentation.sphinx.common
import annize.features.documentation.sphinx.output.html
import annize.features.documentation.sphinx.rst
import annize.features.distributables.common
import annize.features.i18n.common
import annize.features.media_galleries
import annize.flow.run_context
import annize.fs
import annize.i18n


class HomepageSection(abc.ABC):

    def __init__(self, *, head: annize.i18n.TrStr, sort_index: int = 0):
        self.__head = head
        self.__sort_index = sort_index

    @property
    def head(self) -> annize.i18n.TrStr:
        return self.__head

    @property
    def sort_index(self) -> int:
        return self.__sort_index

    def pre_process_generate(self, info: "_PrePostProcGenerateInfo") -> None:
        pass

    @abc.abstractmethod
    def generate_content(self, info: "_GenerateInfo") -> "Content":
        pass

    def post_process_generate(self, info: "_PrePostProcGenerateInfo") -> None:
        pass

    class Content:

        def __init__(self, *, rst_text: str = "", media_files: t.Sequence[annize.fs.FilesystemContent] = ()):
            self.__rst_text = rst_text or ""
            self.__media_files = tuple(media_files or ())

        @property
        def rst_text(self) -> str:
            return self.__rst_text

        @property
        def media_files(self) -> t.Sequence[annize.fs.FilesystemContent]:
            return self.__media_files

        def append_rst(self, rst_text) -> None:
            self.__rst_text += rst_text + "\n\n"

        def attach_media_file(self, file: annize.fs.FilesystemContent) -> None:
            self.__media_files = tuple((*self.__media_files, file))

    @dataclasses.dataclass
    class _GenerateInfo:
        culture: annize.i18n.Culture
        custom_arg: object|None
        document_root_url: str
        document_variant_directory: annize.fs.Path
        document_variant_url: str

    @dataclasses.dataclass
    class _PrePostProcGenerateInfo:
        document_root_directory: annize.fs.Path
        document_root_url: str
        custom_arg: object|None


class Homepage:

    def __init__(self, *, title: annize.i18n.TrStr|None, title_tagline: annize.i18n.TrStr|None,
                 sections: t.Sequence[HomepageSection], cultures: t.Sequence[annize.i18n.Culture]):
        self.__title = title
        self.__title_tagline = title_tagline
        self.__sections = tuple(sections)
        self.__cultures = tuple(cultures)

    @property
    def title(self) -> annize.i18n.TrStr:
        return self.__title or annize.features.base.pretty_project_name()

    @property
    def title_tagline(self) -> annize.i18n.TrStr:
        return self.__title_tagline or annize.features.base.summary()

    @property
    def cultures(self) -> t.Sequence[annize.i18n.Culture]:
        return self.__cultures or annize.features.i18n.common.project_cultures() or [annize.i18n.unspecified_culture]

    @property
    def sections(self) -> t.Sequence[HomepageSection]:
        return self.__sections

    def generate(self) -> annize.fs.Path:
        variants = []
        sections = sorted(self.sections, key=lambda x: x.sort_index)
        result = annize.fs.fresh_temp_directory(annize.flow.run_context.object_name(self)).path
        custom_args = {section: None for section in sections}
        document_root_url = "../"  # TODO nicer?! more robust?!
        self.__generate_pre_post_proc(custom_args=custom_args, is_pre=True, document_root_directory=result,
                                      document_root_url=document_root_url)

        rm_custom_args = set()
        for culture in self.cultures:
            document_variant_directory = result(culture.full_name)
            with culture:
                page = annize.features.documentation.sphinx.rst.heading(self.title, level=0,
                                                                        special=True)  # heading won't be visible
                for section in sections:
                    page_content = self.__generate_section(
                        section, custom_args=custom_args, culture=culture, document_root_directory=result,
                        document_root_url=document_root_url, document_variant_directory=document_variant_directory)
                    if not page_content:
                        rm_custom_args.add(section)
                    page += page_content
                variants.append(annize.features.documentation.sphinx.common.RstDocumentVariant(
                    culture=culture, source=annize.fs.dynamic_file(content=page, file_name="index.rst")))

        for rm_custom_arg in rm_custom_args:
            custom_args.pop(rm_custom_arg)

        document = annize.features.documentation.sphinx.common.RstDocument(
            variants=variants, project_name=self.title, version=None, release=None, authors=(), title=self.title,
            short_title=None, title_tagline=self.title_tagline)
        output_spec = annize.features.documentation.sphinx.output.html.HtmlOutputSpec(is_homepage=True)
        document.generate_all_cultures(output_spec).file.path().move_to(result, merge=True)

        self.__generate_pre_post_proc(custom_args=custom_args, is_pre=False,
                                    document_root_directory=result,
                                    document_root_url=document_root_url)

        return result

    def _append_section(self, section: HomepageSection) -> None:
        self.__sections = tuple((*self.__sections, section))

    @staticmethod
    def __generate_pre_post_proc(*, custom_args: dict, is_pre: bool,
                               document_root_directory: annize.fs.Path, document_root_url: str):
        for section, custom_arg in custom_args.items():
            pre_post_proc_generate_info = HomepageSection._PrePostProcGenerateInfo(
                custom_arg=custom_arg, document_root_directory=document_root_directory,
                document_root_url=document_root_url)
            (section.pre_process_generate if is_pre else section.post_process_generate)(pre_post_proc_generate_info)
            custom_args[section] = pre_post_proc_generate_info.custom_arg

    @staticmethod
    def __generate_section(section, *, custom_args: dict, culture: annize.i18n.Culture,
                           document_root_directory: annize.fs.Path, document_root_url: str,
                           document_variant_directory: annize.fs.Path):
        document_variant_directory.mkdir(exist_ok=True)
        generate_info = HomepageSection._GenerateInfo(
            culture=culture, custom_arg=custom_args[section],
            document_root_url=document_root_url, document_variant_url="",
            document_variant_directory=document_variant_directory)
        section_content = section.generate_content(generate_info)
        if section_content is not None:
            custom_args[section] = generate_info.custom_arg
            heading_rst = annize.features.documentation.sphinx.rst.heading(section.head, level=1, special=True)
            return f"{heading_rst}\n{section_content.rst_text}\n\n"
        return ""


class SimpleProjectHomepage(Homepage):

    def __init__(self, *, title: annize.i18n.TrStr|None, title_tagline: annize.i18n.TrStr|None,
                 sections: t.Sequence[HomepageSection], cultures: t.Sequence[annize.i18n.Culture],
                 changelog: annize.features.changelog.common.Changelog|None,
                 dependencies: t.Sequence[annize.features.dependencies.common.Dependency],
                 distributables: t.Sequence[annize.features.distributables.common.Group],
                 documentation: t.Sequence[annize.features.documentation.common.Document],
                 imprint: annize.i18n.TrStr|None,
                 media_galleries: t.Sequence[annize.features.media_galleries.Gallery]):
        import annize.features.homepage.sections.about
        import annize.features.homepage.sections.changelog
        import annize.features.homepage.sections.documentation
        import annize.features.homepage.sections.download
        import annize.features.homepage.sections.gallery
        import annize.features.homepage.sections.imprint
        import annize.features.homepage.sections.license
        sections_ = annize.features.homepage.sections
        super().__init__(title=title, title_tagline=title_tagline, sections=sections, cultures=cultures)
        self._append_section(sections_.about.Section())
        self._append_section(sections_.changelog.Section(changelog=changelog))
        self._append_section(sections_.documentation.Section(documentation=documentation))
        self._append_section(sections_.download.Section(distributables=distributables, dependencies=dependencies))
        self._append_section(sections_.gallery.Section(media_galleries=media_galleries))
        self._append_section(sections_.imprint.Section(imprint=imprint))
        self._append_section(sections_.license.Section())


class GeneratedHomepage(annize.fs.FilesystemContent):

    def __init__(self, *, homepage: Homepage):
        super().__init__(self._path)
        self.__homepage = homepage

    def _path(self):
        return self.__homepage.generate()
