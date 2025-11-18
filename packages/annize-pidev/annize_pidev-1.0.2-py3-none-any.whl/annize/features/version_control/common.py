# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Version control.
"""
import abc
import datetime
import typing as t

import annize.flow.run_context
import annize.data


class VersionControlSystem(abc.ABC):

    @abc.abstractmethod
    def current_revision(self) -> str:
        pass

    @abc.abstractmethod
    def revision_list(self) -> t.Sequence[str]:
        pass

    @abc.abstractmethod
    def commit_message(self, revision: str) -> str:
        pass

    @abc.abstractmethod
    def commit_time(self, revision: str) -> datetime.datetime:
        pass

    @abc.abstractmethod
    def revision_number(self, revision: str) -> int:
        pass


class BuildVersion(annize.data.Version):

    def __init__(self, *, base_version: annize.data.Version, vcs: VersionControlSystem):
        super().__init__(pattern=base_version.pattern)
        self.__base_version = base_version
        self.__vcs = vcs

    def __full_version(self):
        segment_values = {k: v for k, v in self.__base_version.segments_tuples}
        segment_values["build"] = self.__vcs.revision_number(self.__vcs.current_revision())
        return annize.data.Version(pattern=self.__base_version.pattern, **segment_values)

    @property
    def segments_tuples(self):
        return self.__full_version().segments_tuples

    @property
    def text(self):
        return self.__full_version().text
