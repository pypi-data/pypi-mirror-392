# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Git-based version control.
"""
import datetime
import subprocess
import typing as t

import annize.features.base
import annize.features.files.common
import annize.features.version_control.common
import annize.fs


class VersionControlSystem(annize.features.version_control.common.VersionControlSystem):

    def __init__(self, *, path: str|None):
        super().__init__()
        self.__path = path or ""

    @property
    def path(self) -> annize.fs.Path:
        return annize.features.base.project_directory()(self.__path)

    def current_revision(self):
        return self.__call_git(("log", "-1", "--pretty=format:%H")).strip()

    def revision_list(self):
        return list(reversed([line for line in [line.strip() for line in self.__call_git(
            ("rev-list", "HEAD")).split("\n")] if line]))

    def commit_message(self, revision):
        return self.__call_git(("log", revision, "-n1", "--format=format:%B"))

    def commit_time(self, revision):
        return datetime.datetime.fromtimestamp(float(self.__call_git(("log", revision, "-n1", "--format=format:%ct"))))

    def revision_number(self, revision):
        for i_revision_, revision_ in enumerate(self.revision_list()):
            if revision_.startswith(revision):
                return i_revision_ + 1
        raise ValueError(f"revision not found: {revision}")

    def __call_git(self, cmdline: t.Iterable[str]) -> str:
        return subprocess.check_output(("git", *cmdline), cwd=self.path).decode()


class ExcludeByGitIgnores(annize.features.files.common.Exclude):

    def __init__(self):
        super().__init__(by_path_pattern=None, by_path=None, by_name_pattern=None, by_name=None)

    def does_exclude(self, relative_path, source, destination):
        if source.name == ".git":  # TODO move to files.common.UsualExcludes ?!
            return True

        try:
            return subprocess.check_output(("git", "ls-files", source.name), cwd=source.parent).strip() == b""
        except subprocess.CalledProcessError:
            return False
