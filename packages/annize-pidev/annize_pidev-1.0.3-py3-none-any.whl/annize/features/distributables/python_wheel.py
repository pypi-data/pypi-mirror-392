# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Python Wheels.
"""
import dataclasses
import subprocess
import typing as t

import annize.data
import annize.features._pidev.i18n
import annize.features.authors
import annize.features.base
import annize.features.dependencies.python
import annize.features.licensing
import annize.fs
import annize.i18n


class ExecutableLink:

    def __init__(self, *, link_name: str, module_name: str, method_name: str, is_gui: bool):
        self.__link_name = link_name
        self.__module_name = module_name
        self.__method_name = method_name
        self.__is_gui = is_gui

    @property
    def link_name(self) -> str:
        return self.__link_name

    @property
    def module_name(self) -> str:
        return self.__module_name

    @property
    def method_name(self) -> str:
        return self.__method_name

    @property
    def is_gui(self) -> bool:
        return self.__is_gui


class ExtraDependencies:

    def __init__(self, *, extra_name: str, dependencies: t.Sequence[annize.features.dependencies.python.PythonPackage]):
        self.__extra_name = extra_name
        self.__dependencies = tuple(dependencies)

    @property
    def extra_name(self) -> str:
        return self.__extra_name

    @property
    def dependencies(self) -> t.Sequence[annize.features.dependencies.python.PythonPackage]:
        return self.__dependencies


class Package(annize.fs.FilesystemContent):

    __ = annize.features._pidev.i18n.tr("an_int_PythonWheelPackage", culture="en")  # to be used by Annize projects

    def __init__(self, *, source: annize.fs.FilesystemContent, executable_links: t.Sequence[ExecutableLink],
                 package_name: str|None, description: annize.i18n.TrStr|None,
                 homepage_url: str|None, long_description: annize.i18n.TrStr|None,
                 version: annize.data.Version|None, keywords: annize.features.base.Keywords|None,
                 dependencies: t.Sequence[annize.features.dependencies.python.PythonPackage],
                 extra_dependencies: t.Sequence[ExtraDependencies],
                 license: annize.features.licensing.License|None,
                 authors: t.Sequence[annize.features.authors.Author]):
        super().__init__(self._path)
        self.__source = source
        self.__executable_links = tuple(executable_links)
        self.__package_name = package_name
        self.__description = description
        self.__homepage_url = homepage_url
        self.__long_description = long_description
        self.__version = version
        self.__keywords = keywords
        self.__dependencies = tuple(dependencies)
        self.__extra_dependencies = tuple(extra_dependencies)
        self.__license = license
        self.__authors = tuple(authors)

    def _path(self):
        with annize.i18n.culture_by_spec("en"):
            license = self.__license
            if not license:
                project_licenses = annize.features.licensing.project_licenses()
                if len(project_licenses) == 1:
                    license = project_licenses[0]

            return self.__make_package(self._BuildInfo(
                source=self.__source,
                long_description=self.__long_description or annize.features.base.long_description(),
                homepage=self.__homepage_url or annize.features.base.homepage_url(),
                description=self.__description or annize.features.base.summary(),
                keywords=self.__keywords or annize.features.base.project_keywords(),
                name=self.__package_name or annize.features.base.project_name(),
                author=annize.features.authors.join_authors(self.__authors or annize.features.authors.project_authors()),
                license=license,
                dependencies=self.__dependencies,
                extra_dependencies=self.__extra_dependencies,
                executable_links=self.__executable_links,
                version=self.__version)).path()

    @classmethod
    def __make_package(cls, info: "_BuildInfo") -> annize.fs.FilesystemContent:
        with annize.fs.fresh_temp_directory() as temp_dir:
            cls.__make_package__prepare_info(info, temp_dir)
            cls.__make_package__prepare_setup_py_conf(info)
            cls.__make_package__prepare_setup_py_conf_dependencies(info)
            cls.__make_package__prepare_setup_py_conf_classifiers(info)
            cls.__make_package__executable_links(info)
            cls.__make_package__setup_py_conf(info)
            cls.__make_package__manifest_in(info)
            cls.__make_package__bdist_wheel(info)
            return info.result.path().temp_clone()

    @classmethod
    def __make_package__prepare_info(cls, info: "_BuildInfo", temp_dir: annize.fs.Path) -> None:
        info.wheel_pkg_dir = temp_dir / "wheelpkg"
        info.source.path().copy_to(info.wheel_pkg_dir)
        info.setup_py_conf = {}
        info.setup_py_file = info.wheel_pkg_dir / "setup.py"
        if info.setup_py_file.exists():
            raise RuntimeError("there must be no setup.py in the project root")

    @classmethod
    def __make_package__prepare_setup_py_conf(cls, info: "_BuildInfo") -> None:
        info.setup_py_conf["name"] = info.name
        info.setup_py_conf["version"] = str(info.version)
        info.setup_py_conf["description"] = str(info.description)
        info.setup_py_conf["long_description"] = str(info.long_description)
        info.setup_py_conf["description_content_type"] = "text/plain"
        info.setup_py_conf["long_description_content_type"] = "text/plain"
        info.setup_py_conf["url"] = str(info.homepage)
        info.setup_py_conf["author"] = str(info.author.full_name)
        info.setup_py_conf["author_email"] = str(info.author.email_address)
        if info.license:
            info.setup_py_conf["license"] = str(info.license.name)
        info.setup_py_conf["include_package_data"] = True
        if info.keywords.keywords:
            info.setup_py_conf["keywords"] = " ".join([str(kwd) for kwd in info.keywords.keywords])

    @classmethod
    def __make_package__prepare_setup_py_conf_dependencies(cls, info: "_BuildInfo") -> None:
        info.setup_py_conf["install_requires"] = [f"{dependency.name} {dependency.version}"
                                                  for dependency in info.dependencies]
        info.setup_py_conf["extras_require"] = {
            extra_dependencies.extra_name: [f"{dependency.name} {dependency.version}"
                                            for dependency in extra_dependencies.dependencies]
            for extra_dependencies in info.extra_dependencies}

    @classmethod
    def __make_package__prepare_setup_py_conf_classifiers(cls, info: "_BuildInfo") -> None:
        info.setup_py_conf["classifiers"] = [] # TODO use ?!  e.g. license classifier

    @classmethod
    def __make_package__executable_links(cls, info: "_BuildInfo") -> None:
        console_scripts = []
        gui_scripts = []
        for executable_link in info.executable_links:
            scripts_list = gui_scripts if executable_link.is_gui else console_scripts
            scripts_list.append(f"{executable_link.link_name}={executable_link.module_name}"
                                f":{executable_link.method_name}")
        info.setup_py_conf["entry_points"] = {
            "console_scripts": console_scripts,
            "gui_scripts": gui_scripts}

    @classmethod
    def __make_package__setup_py_conf(cls, info: "_BuildInfo") -> None:
        setup_py_conf_code = ""
        for key, value in info.setup_py_conf.items():
            setup_py_conf_code += f"{key}={repr(value)},"

        info.setup_py_file.write_text(f"import setuptools\n"
                                      f"setuptools.setup(\n"
                                      f"    {setup_py_conf_code}\n"
                                      f"    packages=setuptools.find_packages()+setuptools.find_namespace_packages()\n"
                                      f")\n")

    @classmethod
    def __make_package__manifest_in(cls, info: "_BuildInfo") -> None:
        (info.wheel_pkg_dir / "MANIFEST.in").write_text("graft **\n"
                                                        "global-exclude *.py[cod]\n")

    @classmethod
    def __make_package__bdist_wheel(cls, info: "_BuildInfo") -> None:
        subprocess.check_call(["python3", "setup.py", "bdist_wheel", "--python-tag", "py3"], cwd=info.wheel_pkg_dir)
        info.result = annize.fs.Path(info.wheel_pkg_dir)("dist").children()[0]

    @dataclasses.dataclass
    class _BuildInfo:
        source: annize.fs.FilesystemContent
        description: str
        long_description: str
        keywords: annize.features.base.Keywords
        name: str
        version: annize.data.Version
        homepage: str
        author: annize.features.authors.Author
        license: annize.features.licensing.License|None
        executable_links: t.Sequence[ExecutableLink]
        dependencies: t.Sequence
        extra_dependencies: t.Sequence
        wheel_pkg_dir: annize.fs.Path|None = None
        setup_py_file: annize.fs.Path|None = None
        setup_py_conf: dict[str, t.Any|None]|None = None
        result: annize.fs.FilesystemContent|None = None
