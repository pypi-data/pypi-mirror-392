# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Tarballs.
"""
import subprocess
import tarfile

import annize.data
import annize.features._pidev.i18n
import annize.features.licensing
import annize.fs
import annize.i18n
import annize.object


class Package(annize.fs.FilesystemContent):

    __ = annize.features._pidev.i18n.tr("an_int_SourceTarPackage", culture="en")  # to be used by Annize projects

    @annize.object.explicit_only("documentation")
    def __init__(self, *, package_name: str|None, package_name_postfix: str|None,
                 source: annize.fs.FilesystemContent, version: annize.data.Version|None,
                 license: annize.features.licensing.License|None,
                 documentation: annize.fs.FilesystemContent|None):
        super().__init__(self._path)
        self.__package_name = package_name
        self.__package_name_postfix = package_name_postfix
        self.__source = source
        self.__version = version
        self.__license = license
        self.__documentation = documentation

    def _path(self):
        package_name = self.__package_name or annize.features.base.project_name()
        aux_version_str = f"-{self.__version}" if self.__version else ""
        aux_name_postfix_str = f"-{self.__package_name_postfix}" if self.__package_name_postfix else ""
        package_full_name = f"{package_name}{aux_version_str}{aux_name_postfix_str}"

        source = self.__source.path().temp_clone(basename=package_full_name)
        if self.__documentation:
            self.__documentation.path().copy_to(source, destination_as_parent=True)

        licenses = tuple( (self.__license,) if self.__license else annize.features.licensing.project_licenses()  )
        for license_ in licenses:
            source(f"LICENSE_{license_.name}" if len(licenses) > 1 else "LICENSE").write_file(license_.text)

        result = annize.fs.fresh_temp_directory().path(f"{package_full_name}.tgz")

        with tarfile.open(result, "w:gz") as tar_archive:
            tar_archive.add(source, arcname=package_full_name)

        return result
