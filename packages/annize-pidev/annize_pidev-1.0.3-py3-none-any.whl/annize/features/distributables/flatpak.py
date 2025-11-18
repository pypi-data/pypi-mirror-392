# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Flatpaks.
"""
import abc
import dataclasses
import enum
import os
import subprocess
import typing as t

import annize.data
import annize.features._pidev.i18n
import annize.features.base
import annize.features.distributables.common
import annize.features.gpg.common
import annize.fs
import annize.i18n


class Group(annize.features.distributables.common.Group):

    def __init__(self, *, source: annize.fs.FilesystemContent, title: str, description: annize.i18n.TrStr|None,
                 repository: "Repository", package_name: str, project_short_hint_name: str|None,
                 shares: t.Sequence["Share|str"], sockets: t.Sequence["Socket|str"],
                 environment_variables: t.Sequence["EnvironmentVariable"],
                 filesystems: t.Sequence["Filesystem"],
                 devices: t.Sequence["Device|str"],
                 system_features: t.Sequence["SystemFeature|str"],
                 package_short_name: str|None,
                 menu_entries: t.Sequence["MenuEntry"], command: str|None,
                 sdk: str = "org.freedesktop.Sdk",
                 runtime: str = "org.freedesktop.Platform",
                 runtime_repository_url: str|None,
                 kit_version: str = "19.08", gpg_key: annize.features.gpg.common.Key|None):
        super().__init__(title=title, description=description, package_store=None, files=(
            _FlatpakRefFile(name=package_short_name, package_name=package_name,
                            title=project_short_hint_name, repository=repository,
                            runtime_repository_url=runtime_repository_url,
                            gpg_public_key_ascii=gpg_key.public_key_ascii if gpg_key else None),
            *((_GpgFile(name=package_short_name, gpg_public_key_ascii=gpg_key.public_key_ascii),) if gpg_key else ())))
        self.__environment_variables = tuple(environment_variables)
        self.__repository = repository
        self.__source = source
        self.__package_name = package_name
        self.__project_short_hint_name = project_short_hint_name
        self.__package_short_name = package_short_name
        self.__sdk = sdk
        self.__runtime = runtime
        self.__kit_version = kit_version
        self.__command = command
        self.__menu_entries = tuple(menu_entries)
        self.__shares = tuple(shares)
        self.__sockets = tuple(sockets)
        self.__filesystems = tuple(filesystems)
        self.__devices = tuple(devices)
        self.__system_features = tuple(system_features)
        self.__flatpak_built = False

    def files(self):
        if not self.__flatpak_built:
            self.__repository.upload(_FlatpakImage(
                source=self.__source, package_name=self.__package_name,
                sdk=self.__sdk, runtime=self.__runtime, kit_version=self.__kit_version,
                environment_variables={_.name: _.value for _ in self.__environment_variables},
                devices=tuple(str(_) for _ in self.__devices),
                menu_entries=self.__menu_entries, command=self.__command,
                system_features=tuple(str(_) for _ in self.__system_features),
                filesystems=tuple(str(_) for _ in self.__filesystems),
                shares=tuple(_ if isinstance(_, str) else _.value for _ in self.__shares),
                sockets=tuple(_ if isinstance(_, str) else _.value for _ in self.__sockets)))
            self.__flatpak_built = True
        return super().files()

    @property
    def description(self):
        project_short_hint_name = self.__project_short_hint_name or annize.features.base.pretty_project_name()
        repository_friendly_name = self.__repository.friendly_name_suggestion
        repository_public_url = self.__repository.public_url
        package_name = self.__package_name

        part_1 = annize.features._pidev.i18n.TrStr.tr("an_Dist_FlatpakDesc").format(project_short_hint_name=project_short_hint_name,
                                                                    package_name=package_name,
                                                                    repository_public_url=repository_public_url)
        outro_text = annize.features._pidev.i18n.TrStr.tr("an_Dist_FlatpakDescOutro")
        outro_post_text = annize.features._pidev.i18n.TrStr.tr("an_Dist_FlatpakDescOutroPost")
        part_2 = annize.i18n.to_trstr(
            "{outro_text}\n\n"
            ".. code-block:: sh\n\n"
            "  $ flatpak remote-add --user {repository_friendly_name} {repository_public_url}\n"
            "  $ flatpak install --user {repository_friendly_name} {package_name}\n"
            "  $ flatpak run {package_name}\n\n"
            "{outro_post_text}").format(outro_text=outro_text, repository_friendly_name=repository_friendly_name,
                                        repository_public_url=repository_public_url, package_name=package_name,
                                        outro_post_text=outro_post_text)

        return annize.i18n.to_trstr("{part_1}\n\n{part_2}").format(part_1=part_1, part_2=part_2)


class Repository(abc.ABC):

    def __init__(self, *, public_url: str, friendly_name_suggestion: str|None):
        self.__public_url = public_url
        self.__friendly_name_suggestion = friendly_name_suggestion

    @abc.abstractmethod
    def upload(self, source: annize.fs.FilesystemContent) ->None:
        pass

    @property
    def public_url(self) -> str:
        return self.__public_url

    @property
    def friendly_name_suggestion(self) -> str:
        return self.__friendly_name_suggestion or os.path.basename(self.public_url)


class MenuEntry:

    def __init__(self, *, name: str, title: annize.i18n.TrStr,
                 category: annize.features.distributables.common.FreedesktopMenuCategory, command: str, is_gui: bool,
                 icon: annize.fs.FilesystemContent|None):
        self.__name = name
        self.__title = title
        self.__category = category
        self.__command = command
        self.__is_gui = is_gui
        self.__icon = icon

    @property
    def name(self) -> str:
        return self.__name

    @property
    def title(self) -> annize.i18n.TrStr:
        return self.__title

    @property
    def category(self) -> annize.features.distributables.common.FreedesktopMenuCategory:
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


class Filesystem:

    def __init__(self, *, location: "str|FilesystemLocation", read_only: bool = False, create: bool = False):
        if read_only and create:
            raise ValueError("`read_only` and `create` cannot both be enabled")
        self.__location = location if isinstance(location, str) else location.value
        self.__read_only = read_only
        self.__create = create

    def __str__(self):
        return f"{self.__location}{":ro" if self.__read_only else ""}{":create" if self.__create else ""}"


class FilesystemLocation(enum.Enum):
    HOME = "home"
    HOST = "host"
    HOST_OS = "host-os"
    HOST_ETC = "host-etc"
    XDG_DESKTOP = "xdg-desktop"
    XDG_DOCUMENTS = "xdg-documents"
    XDG_DOWNLOAD = "xdg-download"
    XDG_MUSIC = "xdg-music"
    XDG_PICTURES = "xdg-pictures"
    XDG_PUBLIC_SHARE = "xdg-public-share"
    XDG_TEMPLATES = "xdg-templates"
    XDG_VIDEOS = "xdg-videos"
    XDG_RUN = "xdg-run"
    XDG_CONFIG = "xdg-config"
    XDG_CACHE = "xdg-cache"
    XDG_DATA = "xdg-data"


class Share(enum.Enum):
    NETWORK = "network"
    IPC = "ipc"


class Device(enum.Enum):
    DRI = "dri"
    INPUT = "input"
    USB = "usb"
    KVM = "kvm"
    SHM = "shm"
    ALL = "all"


class SystemFeature(enum.Enum):
    DEVEL = "devel"
    MULTIARCH = "multiarch"
    BLUETOOTH = "bluetooth"
    CANBUS = "canbus"
    PER_APP_DEV_SHM = "per-app-dev-shm"


class Socket(enum.Enum):
    X11 = "x11"
    WAYLAND = "wayland"
    FALLBACK_X11 = "fallback-x11"
    PULSEAUDIO = "pulseaudio"
    SYSTEM_BUS = "system-bus"
    SESSION_BUS = "session-bus"
    SSH_AUTH = "ssh-auth"
    PCSC = "pcsc"
    CUPS = "cups"
    GPG_AGENT = "gpg-agent"
    INHERIT_WAYLAND_SOCKET = "inherit-wayland-socket"


class EnvironmentVariable:

    def __init__(self, *, name: str, value: str):
        self.__name = name
        self.__value = value

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> str:
        return self.__value


class LocalRepository(Repository):

    def __init__(self, *, public_url: str, friendly_name_suggestion: str|None,
                 root_dir: annize.fs.TFilesystemContent):
        super().__init__(public_url=public_url, friendly_name_suggestion=friendly_name_suggestion)
        self.__root_dir = annize.fs.content(root_dir)

    def upload(self, source: annize.fs.FilesystemContent):
        source.path().copy_to(self.__root_dir.path(), overwrite=True)


"""TODO zz (maybe this should be even mentioned first?!)
or install it with just:

$ flatpak install --user --from https://pseudopolis.eu/wiki/pino/projs/foo/foo.flatpakref
"""


class _FlatpakRefFile(annize.fs.FilesystemContent):

    def __init__(self, *, name: str|None, package_name: str, title: str|None, branch: str = "master",
                 runtime_repository_url: str|None, gpg_public_key_ascii: str|None, repository: Repository):
        super().__init__(self._path)
        self.__name = name
        self.__package_name = package_name
        self.__title = title
        self.__branch = branch
        self.__runtime_repository_url = runtime_repository_url
        self.__gpg_public_key_ascii = gpg_public_key_ascii
        self.__repository = repository

    def _path(self):
        name = self.__name or annize.features.base.project_name()
        title = self.__title or name
        res = {"Title": title, "Name": self.__package_name, "Branch": self.__branch,
               "Url": self.__repository.public_url, "IsRuntime": "False"}
        if self.__gpg_public_key_ascii:
            res["GPGKey"] = self.__gpg_public_key_ascii
        if self.__runtime_repository_url:
            res["RuntimeRepo"] = self.__runtime_repository_url
        flatpak_ref_content = "\n".join([f"{x}={res[x]}" for x in res])
        return annize.fs.dynamic_file(content=f"[Flatpak Ref]\n{flatpak_ref_content}\n",
                                      file_name=f"{name}.flatpakref").path()


class _GpgFile(annize.fs.FilesystemContent):

    def __init__(self, *, name: str, gpg_public_key_ascii: str):
        super().__init__(self._path)
        self.__name = name
        self.__gpg_public_key_ascii = gpg_public_key_ascii

    def _path(self):
        name = self.__name or annize.features.base.project_name()
        return annize.fs.dynamic_file(content=self.__gpg_public_key_ascii, file_name=f"{name}.gpg").path()


class _FlatpakImage(annize.fs.FilesystemContent):

    __ = annize.features._pidev.i18n.tr("an_int_FlatpakPackage", culture="en")  # to be used by Annize projects

    def __init__(self, *, source: annize.fs.FilesystemContent, package_name: str,
                 sdk: str, runtime: str, kit_version: str,
                 menu_entries: t.Sequence["MenuEntry"], command: str|None,
                 sockets: t.Sequence[str],
                 environment_variables: t.Mapping[str, str],
                 devices: t.Sequence[str],
                 filesystems: t.Sequence[str],
                 system_features: t.Sequence[str],
                 shares: t.Sequence[str]):
        super().__init__(self._path)
        self.__source = source
        self.__sdk = sdk
        self.__runtime = runtime
        self.__kit_version = kit_version
        self.__environment_variables = dict(environment_variables)
        self.__package_name = package_name
        self.__command = command
        self.__menu_entries = tuple(menu_entries)
        self.__sockets = tuple(sockets)
        self.__devices = tuple(devices)
        self.__filesystems = tuple(filesystems)
        self.__system_features = tuple(system_features)
        self.__shares = tuple(shares)

    def _path(self):
        return self.__make_package(self._BuildInfo(
            source=self.__source,  name=self.__package_name, sdk=self.__sdk,
            runtime=self.__runtime, kit_version=self.__kit_version, sockets=self.__sockets,
            devices=self.__devices,
            system_features=self.__system_features,
            filesystems=self.__filesystems, shares=self.__shares, menu_entries=self.__menu_entries,
            command=self.__command,
            environment_variables=self.__environment_variables))

    @classmethod
    def __make_package(cls, info: "_BuildInfo") -> annize.fs.Path:
        with annize.fs.fresh_temp_directory() as temp_dir:
            cls.__make_package__prepare_info(info, temp_dir)
            cls.__make_package__flatpak_build_init(info)
            cls.__make_package__apply_source(info)
            cls.__make_package__flatpak_build_finish(info)
            cls.__make_package__flatpak_build_export(info)
            return info.result.path()

    @classmethod
    def __make_package__prepare_info(cls, info: "_BuildInfo", temp_dir: annize.fs.Path) -> None:
        info.package_source_dir = temp_dir / "pkg"
        share_dir = info.package_source_dir / "app/share"
        info.share_applications_dir = share_dir / "applications"
        info.share_icons_dir = share_dir / "icons"
        for share_stuff_dir in [info.share_applications_dir, info.share_icons_dir]:
            share_stuff_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def __make_package__flatpak_build_init(cls, info: "_BuildInfo") -> None:
        subprocess.check_call(["flatpak", "build-init", info.package_source_dir, info.name, info.sdk, info.runtime,
                               *([info.kit_version] if info.kit_version else [])])

    @classmethod
    def __make_package__apply_source(cls, info: "_BuildInfo") -> None:
        info.source.path().copy_to(info.package_source_dir, destination_as_parent=True, merge=True)

    @classmethod
    def __make_package__flatpak_build_finish(cls, info: "_BuildInfo") -> None:
        flatpak_args = []
        if info.command:
            flatpak_args.append(f"--command={info.command}")
        for s in info.sockets:
            flatpak_args.append(f"--socket={s}")
        for s in info.filesystems:
            flatpak_args.append(f"--filesystem={s}")
        for s in info.shares:
            flatpak_args.append(f"--share={s}")
        for s in info.devices:
            flatpak_args.append(f"--device={s}")
        for s in info.system_features:
            flatpak_args.append(f"--allow={s}")
        for key, value in info.environment_variables.items():
            flatpak_args.append(f"--env={key}={value}")
        subprocess.check_call(("flatpak", "build-finish", *flatpak_args, info.package_source_dir))

    @classmethod
    def __make_package__menu_entries(cls, info: "_BuildInfo") -> None:
        for menu_entry in info.menu_entries:
            icon_filename = f"{info.name}.{menu_entry.name}.png"

            entry_additionals = ""
            if menu_entry.icon:
                menu_entry.icon.copy_to(annize.fs.Path(info.share_icons_dir)(icon_filename))
                entry_additionals += f"Icon={icon_filename}\n"

            info.share_applications_dir(f"{info.name}.{menu_entry.name}.desktop").write_text(
                f"[Desktop Entry]\n"
                f"Name={menu_entry.title}\n"
                f"Exec={menu_entry.command}\n"
                f"Terminal={'false' if menu_entry.is_gui else 'true'}\n"
                f"Type=Application\n"
                f"Categories={menu_entry.category.value};\n"
                f"{entry_additionals}")

    @classmethod
    def __make_package__flatpak_build_export(cls, info: "_BuildInfo") -> None:
        info.result = annize.fs.fresh_temp_directory().path
        result_dir = info.result.path()
        flatpak_args = [] # TODO gpg stoff
        subprocess.check_call(["flatpak", "build-export", *flatpak_args, result_dir, info.package_source_dir])
        subprocess.check_call(["flatpak", "build-update-repo", *flatpak_args, result_dir])

    @dataclasses.dataclass
    class _BuildInfo:
        source: annize.fs.FilesystemContent
        name: str
        sdk: str
        runtime: str
        kit_version: str|None
        command: str|None
        sockets: t.Sequence[str]
        devices: t.Sequence[str]
        filesystems: t.Sequence[str]
        system_features: t.Sequence[str]
        shares: t.Sequence[str]
        menu_entries: t.Sequence[MenuEntry]
        environment_variables: dict[str, str]
        package_source_dir: annize.fs.Path|None = None
        share_applications_dir: annize.fs.Path|None = None
        share_icons_dir: annize.fs.Path|None = None
        result: annize.fs.FilesystemContent|None = None
