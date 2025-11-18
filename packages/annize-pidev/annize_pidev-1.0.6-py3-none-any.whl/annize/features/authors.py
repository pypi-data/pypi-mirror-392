# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project author information.
"""
import typing as t

import annize.features._pidev.i18n
import annize.flow.run_context
import annize.data
import annize.features.base
import annize.i18n


class Author:

    def __init__(self, *, full_name: annize.i18n.TrStr, email_address: str|None):
        self.__fullname = full_name
        self.__email_address = email_address

    @property
    def full_name(self) -> annize.i18n.TrStr:
        return self.__fullname

    @property
    def email_address(self) -> str|None:
        return self.__email_address


def project_authors() -> t.Sequence[Author]:
    return annize.flow.run_context.objects_by_type(Author)


def join_authors(authors: t.Iterable[Author]) -> Author:
    authors = tuple(authors)

    if len(authors) == 0:
        project_name = annize.features.base.pretty_project_name()
        return Author(full_name=annize.features._pidev.i18n.TrStr.tr("an_Aut_Generic").format(project_name=project_name),
                      email_address=None)

    elif len(authors) == 1:
        return authors[0]

    else:
        full_name = annize.i18n.friendly_join_string_list([author.full_name for author in authors])
        emails = [author.email_address for author in authors if author.email_address]
        email_address = emails[0] if (len(emails) > 0) else None
        return Author(full_name=full_name, email_address=email_address)
