# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Changelogs.
"""
import datetime
import typing as t

import annize.data
import annize.features.version
import annize.features.version_control.common
import annize.flow.run_context
import annize.i18n


class Changelog:
    """
    A changelog.
    """

    def __init__(self, *, entries: t.Sequence["Entry"]):
        """
        :param entries: Entries.
        """
        self.__entries = tuple(entries)

    @property
    def entries(self) -> t.Sequence["Entry"]:
        """
        Entries.
        """
        return self.__entries


class Entry:
    """
    A changelog entry for a particular version, containing a list of items.
    """

    def __init__(self, *, version: annize.data.Version|None, time: datetime.datetime|None,
                 items: t.Sequence["annize.i18n.TrStr|Item"]):
        """
        :param version: The project version associated with this entry.
        :param time: The time associated with this entry.
        :param items: The items of this entry, representing the particular changes in this version.
        """
        self.__version = version
        self.__time = time
        self.__items = tuple(item if isinstance(item, Item) else Item(text=item) for item in items)

    @property
    def items(self) -> t.Sequence["Item"]:
        """
        The items of this entry.
        """
        return self.__items

    @property
    def time(self) -> datetime.datetime|None:
        """
        The time associated with this entry.
        """
        return self.__time

    @property
    def version(self) -> annize.data.Version|None:
        """
        The project version associated with this entry.
        """
        return self.__version


class Item:
    """
    An item, i.e. a short description for a particular change, of a changelog entry.
    """

    def __init__(self, *, text: annize.i18n.TrStr):
        """
        :param text: The text.
        """
        self.__text = text

    @property
    def text(self) -> annize.i18n.TrStr:
        """
        The text.
        """
        return self.__text


def default_changelog() -> Changelog|None:
    changelogs = annize.flow.run_context.objects_by_type(Changelog, toplevel_only=True)
    if len(changelogs) > 1:
        raise RuntimeError("there is more than one changelog defined in this project")
    if len(changelogs) == 1:
        return changelogs[0]
    return None
