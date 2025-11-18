# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Keywords.
"""
import annize.flow.run_context


class Keywords:

    def __init__(self, *, from_string: str = "", split_by: str = " ", keywords: list[str] = ()):
        self.__from_string = from_string
        self.__split_by = split_by
        self.__keywords = keywords

    @property
    def keywords(self) -> list[str]:
        result = []
        for keyword in [*self.__keywords, *self.__from_string.split(self.__split_by)]:
            if keyword and (keyword not in result):
                result.append(keyword)
        return result


def project_keywords() -> Keywords:
    all_keywords = []
    for keywords in annize.flow.run_context.objects_by_type(Keywords):
        for keyword in keywords.keywords:
            if keyword not in all_keywords:
                all_keywords.append(keyword)
    return Keywords(keywords=all_keywords)
