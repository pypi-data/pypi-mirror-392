# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage download section.
"""
import hashlib
import locale
import typing as t

import annize.features._pidev.i18n
import annize.features.base
import annize.features.dependencies.common
import annize.features.documentation.sphinx.rst
import annize.features.distributables.common
import annize.features.homepage.common
import annize.fs
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, distributables: t.Sequence[annize.features.distributables.common.Group],
                 dependencies: t.Sequence[annize.features.dependencies.common.Dependency],
                 head=annize.features._pidev.i18n.TrStr.tr("an_HP_Head_Download"), sort_index=40_000):
        super().__init__(head=head, sort_index=sort_index)
        self.__distributables = tuple(distributables)
        self.__dependencies = tuple(dependencies)

    def pre_process_generate(self, info):
        for distributable_group in self.__distributables:
            for distributable_file in distributable_group.files():
                distributable_file.path()

    def post_process_generate(self, info):
        downloadable_files: t.Iterable[annize.fs.Path] = info.custom_arg
        for downloadable_file in downloadable_files:
            downloadable_file.copy_to(info.document_root_directory(downloadable_file.name))

    def generate_content(self, info):  # TODO make package generation in "en" culture context ?!
        project_name = annize.features.base.pretty_project_name()
        content = annize.features.homepage.common.HomepageSection.Content()
        dependencies = annize.features.dependencies.common.dependencies_to_rst_text(self.__dependencies)
        package_list = self.__generate_package_list(info)
        do_return = False
        if package_list:
            do_return = True
            head_str = annize.features._pidev.i18n.tr("an_HP_DL_PackagesAvailable")
            if dependencies:
                requirements_label = annize.features._pidev.i18n.tr("an_HP_DL_TheReqs")
                dependenciesref = f":ref:`{requirements_label}<hp_downl_deps>`"
                head_str += " " + annize.features._pidev.i18n.tr("an_HP_DL_CheckReqs").format(dependenciesref=dependenciesref)
            content.append_rst(head_str)
            content.append_rst(package_list)
        if dependencies:
            do_return = True
            content.append_rst(annize.features.documentation.sphinx.rst.heading(
                annize.features._pidev.i18n.tr("an_HP_DL_Deps"), level=0, anchor="hp_downl_deps"))
            content.append_rst(annize.features._pidev.i18n.tr("an_HP_DL_Uses3rdParty").format(project_name=project_name))
            content.append_rst(dependencies)
        return content if do_return else None

    def __generate_package_list(self, info: annize.features.homepage.common.HomepageSection._GenerateInfo):
        content = ""
        file_label = annize.features._pidev.i18n.tr("an_HP_DL_File")
        release_time_label = annize.features._pidev.i18n.tr("an_HP_DL_Releasedate")
        sha256sum_label = annize.features._pidev.i18n.tr("an_HP_DL_Sha256sum")
        size_label = annize.features._pidev.i18n.tr("an_HP_DL_Size")
        info.custom_arg = []  # TODO now we do that once per language (as its called in generate_content())
        for distributable_group in self.__distributables:
            group_content = f".. rubric:: {distributable_group.title}\n\n{distributable_group.description}\n\n"
            for distributable_file_item in distributable_group.files():
                distributable_file = distributable_file_item.path()
                info.custom_arg.append(distributable_file)
                ctime = distributable_file.ctime().strftime("%x")
                distributable_file_hash = filehash(distributable_file)
                distributable_file_size = friendly_file_size(distributable_file.file_size())
                group_content += (f".. rst-class:: downloadblock\n\n"
                                  f":{file_label}: `{distributable_file.name} <{info.document_root_url}{distributable_file.name}>`_\n"
                                  f":{release_time_label}: {ctime}\n"
                                  f":{sha256sum_label}: :samp:`{distributable_file_hash}`\n"
                                  f":{size_label}: {distributable_file_size}\n\n")
            content += group_content
        return content


def friendly_file_size(value: int) -> str:
    unit_str = annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_B")
    for unit_str_ in (
            annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_kB"),
            annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_MB"),
            annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_GB"),
            annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_TB"),
            annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_PB"),
            annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_EB"),
            annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_ZB"),
            annize.features._pidev.i18n.tr("an_HP_DL_FriendlySize_YB")):
        if value > 1024:
            value = value / 1024.0
            unit_str = unit_str_
        else:
            break

    return f"{locale.format_string("%.1f", value)} {unit_str}"


def filehash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            block = f.read(1024 ** 2)
            if block == b"":
                break
            hasher.update(block or b"")
    return hasher.hexdigest()


# TODO noh packagestore (show last three versions via packagestore)
