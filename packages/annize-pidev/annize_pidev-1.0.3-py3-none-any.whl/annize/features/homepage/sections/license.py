# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage license section.
"""
import annize.features._pidev.i18n
import annize.features.base
import annize.features.homepage.common
import annize.features.licensing
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, head=annize.features._pidev.i18n.TrStr.tr("an_HP_Head_License"), sort_index=20_000):
        super().__init__(head=head, sort_index=sort_index)

    def generate_content(self, info):
        licenses = annize.features.licensing.project_licenses()
        if len(licenses) > 0:
            project_name = annize.features.base.pretty_project_name() or annize.features._pidev.i18n.tr("an_ThisProject")

            for i_license, license in enumerate(licenses):
                if license.text:
                    license_file_name = f"_license_{i_license}.txt"
                    info.document_variant_directory(license_file_name).write_file(str(license.text))

            license_names = annize.i18n.friendly_join_string_list([str(_.name) for _ in licenses])
            return annize.features.homepage.common.HomepageSection.Content(
                rst_text=annize.features._pidev.i18n.tr("an_HP_Lic_Text").format(project_name=project_name,
                                                                 license_names=license_names))

        return None
