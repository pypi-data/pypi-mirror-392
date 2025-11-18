# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
ssh-based file transfers.
"""
import contextlib
import subprocess
import typing as t

import annize.features.files.transfer.common
import annize.fs


class Endpoint(annize.features.files.transfer.common.Endpoint):

    def __init__(self, *, host: str, port: int = 22, username: str, identity_file: str|None,
                 has_shell_access: bool = False):
        super().__init__()
        self.__host = host
        self.__port = port
        self.__username = username
        self.__identity_file = identity_file
        self.__has_shell_access = has_shell_access

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def username(self) -> str:
        return self.__username

    @property
    def identity_file(self) -> str|None:
        return self.__identity_file

    @property
    def has_shell_access(self) -> bool:
        return self.__has_shell_access

    @contextlib.contextmanager
    def access_filesystem(self, root_directory):
        with annize.fs.fresh_temp_directory() as temp_dir:
            with annize.fs.ext.Mount(self.__location_str(f"/{root_directory.lstrip("/")}"), temp_dir,
                                     mount_command=["sshfs"], umount_command=["fusermount", "-u"],
                                     options=self.__ssh_arguments()) as mount:
                yield mount.destination

    def exec(self, cmdline: str) -> bytes:
        return subprocess.check_output(("ssh", *self.__ssh_arguments(), self.__location_str(), cmdline))

    def __ssh_arguments(self) -> t.Sequence[str]:
        ssh_arguments = ["-p", f"{self.__port}"]
        if self.__identity_file:
            ssh_arguments += ["-o", f"IdentityFile={self.__identity_file}"]
        return ssh_arguments

    def __location_str(self, path: str|None = None) -> str:
        dpath = "" if (path is None) else f":{path}"
        return f"{self.__username}@{self.__host}{dpath}"
