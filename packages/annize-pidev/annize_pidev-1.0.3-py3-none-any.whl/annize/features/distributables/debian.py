# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Debian (.deb) packages.
"""
import dataclasses
import datetime
import gzip
import math
import os
import subprocess
import typing as t

import annize.data
import annize.features.authors
import annize.features.base
import annize.features.dependencies.common
import annize.features.distributables.common
import annize.fs
import annize.i18n
import annize.object


class Package(annize.fs.FilesystemContent):

    __ = annize.features._pidev.i18n.tr("an_int_DebianPackage", culture="en")  # to be used by Annize projects

    @annize.object.explicit_only("documentation")
    def __init__(self, *, source: annize.fs.FilesystemContent, menu_entries: t.Sequence["MenuEntry"],
                 executable_links: t.Sequence["ExecutableLink"],
                 package_name: str|None, description: annize.i18n.TrStr|None,
                 summary: annize.i18n.TrStr|None,
                 section: "Section|None",
                 homepage_url: str|None,
                 version: annize.data.Version|None,
                 documentation: annize.fs.FilesystemContent|None,
                 license: annize.features.licensing.License|None,
                 authors: t.Sequence[annize.features.authors.Author],
                 prerm: str = "", postinst: str = "", architecture: str = "all"):
        super().__init__(self._path)
        self.__source = source
        self.__menu_entries = tuple(menu_entries)
        self.__executable_links = tuple(executable_links)
        self.__package_name = package_name
        self.__description = description
        self.__summary = summary
        self.__section = section
        self.__homepage_url = homepage_url
        self.__version = version
        self.__documentation = documentation
        self.__license = license
        self.__authors = tuple(authors)
        self.__prerm = prerm
        self.__postinst = postinst
        self.__architecture = architecture

    def _path(self):
        licensename = self.__license.name if self.__license else None
        if not licensename:
            project_licenses = annize.features.licensing.project_licenses()
            if len(project_licenses) == 1:
                licensename = project_licenses[0].name

        with annize.i18n.culture_by_spec("en"):
            return self.__make_package(self._BuildInfo(
                source=self.__source, executable_links=self.__executable_links,
                name=self.__package_name or annize.features.base.project_name(), version=self.__version,
                description=str(self.__description or annize.features.base.long_description()),
                homepage=self.__homepage_url or annize.features.base.homepage_url(),
                author=annize.features.authors.join_authors(self.__authors or annize.features.authors.project_authors()),
                licensename=licensename,
                summary=str(self.__summary or annize.features.base.summary()),
                section=self.__section, menu_entries=self.__menu_entries or [], services=[],
                documentation_source=self.__documentation,
                prerm=self.__prerm, postinst=self.__postinst, architecture=self.__architecture)).path()

    @classmethod
    def __make_package(cls, info: "_BuildInfo") -> annize.fs.FilesystemContent:
        with annize.fs.fresh_temp_directory() as temp_dir:
            cls.__make_package__prepare_info(info, temp_dir)
            cls.__make_package__copyright(info)
            cls.__make_package__changelog(info)
            cls.__make_package__executable_links(info)
            cls.__make_package__menu_entries(info)
            cls.__make_package__services(info)
            cls.__make_package__package_size(info)
            cls.__make_package__pre_post_commands(info)
            cls.__make_package__control_file(info)
            cls.__make_package__conffiles(info)
            cls.__make_package__fix_permissions(info)
            cls.__make_package__dpkg_build(info)
            return info.result

    @classmethod
    def __make_package__prepare_info(cls, info: "_BuildInfo", tmpdir: annize.fs.TInputPath) -> None:
        version_str = f"-{info.version}" if info.version else ""
        info.author_str = f"{info.author.full_name} <{info.author.email_address or 'unknown@unknown'}>"
        info.package_root_dir = tmpdir / f"{info.name}{version_str}-{info.architecture}"
        info.pkgpath_debian = "/DEBIAN"
        info.pkgpath_documentation = f"/usr/share/doc/{info.name}"
        info.pkgpath_pixmaps = "/usr/share/pixmaps"
        info.pkgpath_usrbin = "/usr/bin"
        info.source.path().copy_to(info.package_root_dir)
        info.documentation_source.path().copy_to(info.package_root_dir / info.pkgpath_documentation,
                                                 destination_as_parent=True)
        for package_dir in (info.pkgpath_debian, info.pkgpath_documentation, info.pkgpath_pixmaps, info.pkgpath_usrbin):
            os.makedirs(f"{info.package_root_dir}/{package_dir}", exist_ok=True)
        info.config_files = []

    @classmethod
    def __make_package__copyright(cls, info: "_BuildInfo") -> None:
        copyrighttext = f"""
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: {info.name}
Source: {info.homepage or ''}
Upstream-Contact: {info.author_str}

Files: *
Copyright: {datetime.datetime.now().strftime("%Y")} {info.author.full_name}
License: {info.licensename}
        """[1:]
        for fdest in [f"{info.pkgpath_debian}/copyright", f"{info.pkgpath_documentation}/copyright"]:
            with open(f"{info.package_root_dir}/{fdest}", "w") as f:
                f.write(copyrighttext)

    @classmethod
    def __make_package__changelog(cls, info: "_BuildInfo") -> None:
        with open(f"{info.package_root_dir}/{info.pkgpath_documentation}/changelog.gz", "wb") as f:
            f.write(gzip.compress(f"""
{info.name} {info.version or '1.0'} unstable; urgency=low

* New upstream release.
* See website for details.

-- {info.author_str}  Mon, 14 Jan 2013 13:37:00 +0000
        """[1:].encode("utf-8")))

    @classmethod
    def __make_package__executable_links(cls, info: "_BuildInfo") -> None:
        for executable_link in info.executable_links:
            os.symlink(executable_link.path, f"{info.package_root_dir}/{info.pkgpath_usrbin}/{executable_link.name}")

    @classmethod
    def __make_package__menu_entries(cls, info: "_BuildInfo") -> None:
        def escapecmd(cmd):
            return cmd.replace('"', '\\"')
        os.makedirs(f"{info.package_root_dir}/usr/share/menu")
        os.makedirs(f"{info.package_root_dir}/usr/share/applications")
        for menuentry in info.menu_entries:
            if menuentry.icon:
                iconfname = f"{info.name}.{menuentry.name}.png"
                icondstroot = annize.fs.Path(info.package_root_dir)
                icondst = icondstroot(info.pkgpath_pixmaps)(iconfname)
                menuentry.icon.path().copy_to(icondst)
                sdebianiconspec = f'icon="/usr/share/pixmaps/{iconfname}"'
                sfreedesktopiconspec = f"Icon=/usr/share/pixmaps/{iconfname}"
            else:
                sdebianiconspec = sfreedesktopiconspec = ""
            with open(f"{info.package_root_dir}/usr/share/menu/{menuentry.name}", "w") as f:
                sdebianneeds = "X11" if menuentry.is_gui else "text"
                f.write(f'?package({menuentry.name}):'
                        f'  command="{escapecmd(menuentry.command)}"'
                        f'  needs="{sdebianneeds}"'
                        f'  section="{menuentry.category.debian_name}"'
                        f'  title="{menuentry.title}"'
                        f'  {sdebianiconspec}\n')
            with open(f"{info.package_root_dir}/usr/share/applications/{menuentry.name}.desktop", "w") as f:
                f.write(f"[Desktop Entry]\n"
                        f"Name={menuentry.title}\n"
                        f"Exec={menuentry.command}\n"
                        f"Terminal={'false' if menuentry.is_gui else 'true'}\n"
                        f"Type=Application\n"
                        f"Categories={menuentry.category.freedesktop_name};\n"
                        f"{sfreedesktopiconspec}\n")

    @classmethod
    def __make_package__services(cls, info: "_BuildInfo") -> None:
        os.makedirs(f"{info.package_root_dir}/etc/init")
        startservicescall = ""
        stopservicescall = ""
        for service in info.services:
            servicename = service.name
            servicecommand = service.command
            with open(f"{info.package_root_dir}/etc/init/{servicename}.conf", "w") as f:  # TODO systemd services
                f.write(f"""
# {info.name} - {info.name} job file

description "{info.name} service '{servicename}'"
author "{info.author_str}"

start on runlevel [2345]

stop on runlevel [016]

exec {servicecommand}
        """[1:])
            info.postinst = f"{info.postinst}\nservice {servicename} start"
            info.prerm = f"service {servicename} stop &>/dev/null || true\n{info.prerm}"
            info.config_files.append(f"/etc/init/{servicename}.conf")

    @classmethod
    def __make_package__package_size(cls, info: "_BuildInfo") -> None:
        size = 0
        for dirpath, dirnames, filenames in os.walk(info.package_root_dir):
            for f in filenames:
                ff = f"{dirpath}/{f}"
                if not os.path.islink(ff):
                    size += os.path.getsize(ff)
        info.pkgsize = size

    @classmethod
    def __make_package__pre_post_commands(cls, info: "_BuildInfo") -> None:
        fdebian = f"{info.package_root_dir}/{info.pkgpath_debian}"
        with open(f"{fdebian}/prerm", "w") as f:
            f.write(f"#!/bin/bash\n"
                    f"set -e\n"
                    f"{info.prerm}\n")
        with open(f"{fdebian}/postinst", "w") as f:
            f.write(f"#!/bin/bash\n"
                    f"set -e\n"
                    f"{info.postinst}\n"
                    f"if test -x /usr/bin/update-menus; then update-menus; fi\n")

    @classmethod
    def __make_package__control_file(cls, info: "_BuildInfo") -> None:
        dependencies = [] #TODO info.dependencies; also sugdependencies?
        reqdependencies = [x for x in dependencies if isinstance(x.kind, annize.features.dependencies.common.Required)]
        recdependencies = [x for x in dependencies if isinstance(x.kind, annize.features.dependencies.common.Recommended)]
        sugdependencies = []
        sdepends = ("\nDepends: " + (", ".join(reqdependencies))) if len(reqdependencies) > 0 else ""
        srecommends = ("\nRecommends: " + (", ".join(recdependencies))) \
            if len(recdependencies) > 0 else ""
        ssuggests = ("\nSuggests: " + (", ".join(sugdependencies))) if len(sugdependencies) > 0 else ""
        sdescription = "\n".join([" " + x for x in (info.description or "").split("\n") if x.strip() != ""])
        with open(f"{info.package_root_dir}/{info.pkgpath_debian}/control", "w") as f:
            f.write(f"""
Package: {info.name}
Version: {info.version or '1.0'}
Section: {(info.section or MiscellaneousSection()).name}
Priority: optional
Architecture: {info.architecture}{sdepends}{srecommends}{ssuggests}
Installed-Size: {int(math.ceil(info.pkgsize / 1024.))}
Maintainer: {info.author_str}
Provides: {info.name}
Homepage: {info.homepage or ''}
Description: {info.summary}
{sdescription}
"""[1:])

    @classmethod
    def __make_package__conffiles(cls, info: "_BuildInfo") -> None:
        with open(f"{info.package_root_dir}/{info.pkgpath_debian}/conffiles", "w") as f:
            f.write("\n".join(info.config_files))

    @classmethod
    def __make_package__fix_permissions(cls, info: "_BuildInfo") -> None:
        subprocess.check_call(["chmod", "-R", "u+rw,g+r,g-w,o+r,o-w", info.package_root_dir])
        subprocess.check_call(["chmod", "-R", "0755", f"{info.package_root_dir}/{info.pkgpath_debian}"])
        subprocess.check_call(["chmod", "0644", f"{info.package_root_dir}/{info.pkgpath_debian}/conffiles"])

    @classmethod
    def __make_package__dpkg_build(cls, info: "_BuildInfo") -> None:
        sauxversion = f"_{info.version}" if info.version else ""
        debfilename = f"{info.name}{sauxversion}_{info.architecture}.deb"
        result = annize.fs.fresh_temp_directory()
        subprocess.check_call(["fakeroot", "dpkg", "-b", info.package_root_dir, f"{result.path}/{debfilename}"])
        info.result = result.path(debfilename)

    @dataclasses.dataclass
    class _BuildInfo:
        source: annize.fs.FilesystemContent
        # TODO dependencies: "Optional[List['dependencies.Dependency']]" = None
        executable_links: t.Sequence["ExecutableLink"]
        menu_entries: t.Sequence["MenuEntry"]
        services: t.Sequence["ServiceDescription"]
        description: str
        name: str
        version: annize.data.Version
        homepage: str
        author: annize.features.authors.Author
        licensename: str
        section: "Section|None"
        summary: str
        documentation_source: annize.fs.FilesystemContent|None
        prerm: str
        postinst: str
        architecture: str
        author_str: str|None = None
        package_root_dir: annize.fs.Path|None = None
        pkgpath_debian: str|None = None
        pkgpath_documentation: str|None = None
        pkgpath_pixmaps: str|None = None
        pkgpath_usrbin: str|None = None
        config_files: list[str]|None = None
        pkgsize: int|None = None
        result: annize.fs.FilesystemContent|None = None


class Category:

    def __init__(self, *, debian_name: str, freedesktop_name: str):
        self.__debian_name = debian_name
        self.__freedesktop_name = freedesktop_name

    @property
    def debian_name(self) -> str:
        return self.__debian_name

    @property
    def freedesktop_name(self) -> str:
        return self.__freedesktop_name


class MenuEntry:

    @annize.object.explicit_only("icon")
    def __init__(self, *, name: str, title: annize.i18n.TrStr, category: Category, command: str, is_gui: bool,
                 icon: annize.fs.TFilesystemContent|None):
        self.__name = name
        self.__title = title
        self.__category = category
        self.__command = command
        self.__is_gui = is_gui
        self.__icon = None if icon is None else annize.fs.content(icon)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def title(self) -> annize.i18n.TrStr:
        return self.__title

    @property
    def category(self) -> Category:
        return self.__category

    @property
    def command(self) -> str:
        return self.__command

    @property
    def is_gui(self) -> bool:
        return self.__is_gui

    @property
    def icon(self) -> annize.fs.FilesystemContent|None:
        return self.__icon


class ExecutableLink:

    def __init__(self, *, path: str, name: str|None):
        self.__path = path
        self.__name = name or os.path.splitext(os.path.basename(path))[1]

    @property
    def path(self) -> str:
        return self.__path

    @property
    def name(self) -> str|None:
        return self.__name


class Section:

    def __init__(self, *, name: str):
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name


class ServiceDescription:
    """
    Description for Debian services to be included in a package.
    """

    def __init__(self, name: str, command: str):
        """
        :param name: The display name.
        :param command: The command to be executed.
        """
        self.__name = name
        self.__command = command

    @property
    def name(self) -> str:
        return self.__name

    @property
    def command(self) -> str:
        return self.__command


def _debian_category(debian_name: str, freedesktop_name: str) -> type[Category]:
    class ACategory(Category):
        def __init__(self):
            super().__init__(debian_name=debian_name, freedesktop_name=freedesktop_name)
    return ACategory


ApplicationsAccessibilityCategory = _debian_category("Applications/Accessibility", "System")
ApplicationsAmateurradioCategory = _debian_category("Applications/Amateur Radio", "Utility")
ApplicationsDatamanagementCategory = _debian_category("Applications/Data Management", "System")
ApplicationsEditorsCategory = _debian_category("Applications/Editors", "Utility")
ApplicationsEducationCategory = _debian_category("Applications/Education", "Education")
ApplicationsEmulatorsCategory = _debian_category("Applications/Emulators", "System")
ApplicationsFilemanagementCategory = _debian_category("Applications/File Management", "System")
ApplicationsGraphicsCategory = _debian_category("Applications/Graphics", "Graphics")
ApplicationsMobiledevicesCategory = _debian_category("Applications/Mobile Devices", "Utility")
ApplicationsNetworkCategory = _debian_category("Applications/Network", "Network")
ApplicationsNetworkCommunicationCategory = _debian_category("Applications/Network/Communication", "Network")
ApplicationsNetworkFiletransferCategory = _debian_category("Applications/Network/File Transfer", "Network")
ApplicationsNetworkMonitoringCategory = _debian_category("Applications/Network/Monitoring", "Network")
ApplicationsNetworkWebbrowsingCategory = _debian_category("Applications/Network/Web Browsing", "Network")
ApplicationsNetworkWebnewsCategory = _debian_category("Applications/Network/Web News", "Network")
ApplicationsOfficeCategory = _debian_category("Applications/Office", "Office")
ApplicationsProgrammingCategory = _debian_category("Applications/Programming", "Development")
ApplicationsProjectmanagementCategory = _debian_category("Applications/Project Management", "Development")
ApplicationsScienceCategory = _debian_category("Applications/Science", "Education")
ApplicationsScienceAstronomyCategory = _debian_category("Applications/Science/Astronomy", "Education")
ApplicationsScienceBiologyCategory = _debian_category("Applications/Science/Biology", "Education")
ApplicationsScienceChemistryCategory = _debian_category("Applications/Science/Chemistry", "Education")
ApplicationsScienceDataanalysisCategory = _debian_category("Applications/Science/Data Analysis", "Education")
ApplicationsScienceElectronicsCategory = _debian_category("Applications/Science/Electronics", "Education")
ApplicationsScienceEngineeringCategory = _debian_category("Applications/Science/Engineering", "Education")
ApplicationsScienceGeoscienceCategory = _debian_category("Applications/Science/Geoscience", "Education")
ApplicationsScienceMathematicsCategory = _debian_category("Applications/Science/Mathematics", "Education")
ApplicationsScienceMedicineCategory = _debian_category("Applications/Science/Medicine", "Education")
ApplicationsSciencePhysicsCategory = _debian_category("Applications/Science/Physics", "Education")
ApplicationsScienceSocialCategory = _debian_category("Applications/Science/Social", "Education")
ApplicationsShellsCategory = _debian_category("Applications/Shells", "System")
ApplicationsSoundsCategory = _debian_category("Applications/Sound", "AudioVideo")
ApplicationsSystemCategory = _debian_category("Applications/System", "System")
ApplicationsSystemAdministrationCategory = _debian_category("Applications/System/Administration", "System")
ApplicationsSystemHardwareCategory = _debian_category("Applications/System/Hardware", "System")
ApplicationsSystemLanguageenvironmentCategory = _debian_category("Applications/System/Language Environment", "System")
ApplicationsSystemMonitoringCategory = _debian_category("Applications/System/Monitoring", "System")
ApplicationsSystemPackagemanagementCategory = _debian_category("Applications/System/Package Management", "System")
ApplicationsSystemSecurityCategory = _debian_category("Applications/System/Security", "System")
ApplicationsTerminalemulatorsCategory = _debian_category("Applications/Terminal Emulators", "System")
ApplicationsTextCategory = _debian_category("Applications/Text", "Utility")
ApplicationsTvandradioCategory = _debian_category("Applications/TV and Radio", "AudioVideo")
ApplicationsViewersCategory = _debian_category("Applications/Viewers", "Utility")
ApplicationsVideoCategory = _debian_category("Applications/Video", "AudioVideo")
ApplicationsWebdevelopmentCategory = _debian_category("Applications/Web Development", "Development")
GamesActionCategory = _debian_category("Games/Action", "Game")
GamesAdventureCategory = _debian_category("Games/Adventure", "Game")
GamesBlocksCategory = _debian_category("Games/Blocks", "Game")
GamesBoardCategory = _debian_category("Games/Board", "Game")
GamesCardCategory = _debian_category("Games/Card", "Game")
GamesPuzzlesCategory = _debian_category("Games/Puzzles", "Game")
GamesSimulationCategory = _debian_category("Games/Simulation", "Game")
GamesStrategyCategory = _debian_category("Games/Strategy", "Game")
GamesToolsCategory = _debian_category("Games/Tools", "Game")
GamesToysCategory = _debian_category("Games/Toys", "Game")
HelpCategory = _debian_category("Help", "System")
ScreenSavingCategory = _debian_category("Screen/Saving", "System")
ScreenLockingCategory = _debian_category("Screen/Locking", "System")


def _debian_section(name: str) -> type[Section]:
    class ASection(Section):
        def __init__(self):
            super().__init__(name=name)
    return ASection


AdministrationUtilitiesSection = _debian_section("admin")
MonoCliSection = _debian_section("cli-mono")
CommunicationProgramsSection = _debian_section("comm")
DatabasesSection = _debian_section("database")
DebianInstallerUdebPackagesSection = _debian_section("debian-installer")
DebugPackagesSection = _debian_section("debug")
DevelopmentSection = _debian_section("devel")
DocumentationSection = _debian_section("doc")
EditorsSection = _debian_section("editors")
EducationSection = _debian_section("education")
ElectronicsSection = _debian_section("electronics")
EmbeddedSoftwareSection = _debian_section("embedded")
FontsSection = _debian_section("fonts")
GamesSection = _debian_section("games")
GnomeSection = _debian_section("gnome")
GnuRSection = _debian_section("gnu-r")
GnustepSection = _debian_section("gnustep")
GraphicsSection = _debian_section("graphics")
HamRadioSection = _debian_section("hamradio")
HaskellSection = _debian_section("haskell")
WebServersSection = _debian_section("httpd")
InterpretersSection = _debian_section("interpreters")
IntrospectionSection = _debian_section("introspection")
JavaSection = _debian_section("java")
JavascriptSection = _debian_section("javascript")
KdeSection = _debian_section("kde")
KernelsSection = _debian_section("kernel")
LibraryDevelopmentSection = _debian_section("libdevel")
LibrariesSection = _debian_section("libs")
LispSection = _debian_section("lisp")
LanguagePacksSection = _debian_section("localization")
MailSection = _debian_section("mail")
MathematicsSection = _debian_section("math")
MetaPackagesSection = _debian_section("metapackages")
MiscellaneousSection = _debian_section("misc")
NetworkSection = _debian_section("net")
NewsgroupsSection = _debian_section("news")
OcamlSection = _debian_section("ocaml")
OldLibrariesSection = _debian_section("oldlibs")
OtherOSsAndFSsSection = _debian_section("otherosfs")
PerlSection = _debian_section("perl")
PhpSection = _debian_section("php")
PythonSection = _debian_section("python")
RubySection = _debian_section("ruby")
RustSection = _debian_section("rust")
ScienceSection = _debian_section("science")
ShellsSection = _debian_section("shells")
SoundSection = _debian_section("sound")
TasksSection = _debian_section("tasks")
TexSection = _debian_section("tex")
TextProcessingSection = _debian_section("text")
UtilitiesSection = _debian_section("utils")
VersionControlSystemsSection = _debian_section("vcs")
VideoSection = _debian_section("video")
VirtualPackagesSection = _debian_section("virtual")
WebSoftwareSection = _debian_section("web")
XWindowSystemSoftwareSection = _debian_section("x11")
XfceSection = _debian_section("xfce")
ZopePloneFrameworkSection = _debian_section("zope")
