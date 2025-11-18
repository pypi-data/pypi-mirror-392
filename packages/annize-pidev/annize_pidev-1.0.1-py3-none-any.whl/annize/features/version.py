# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project versioning.
"""
import hallyd

import annize.data
import annize.flow.run_context


class Line:

    def __init__(self, *, version: annize.data.Version):
        self.__version = version

    @property
    def version(self) -> annize.data.Version:
        return self.__version


class Version(annize.data.Version):

    def __init__(self, *, text: str|None, pattern: annize.data.version.VersionPattern|None,
                 **segment_values):
        super().__init__(text=text, pattern=pattern or default_version_pattern(), **segment_values)


_CONTEXT__DEFAULT_VERSION_PATTERN = f"__{hallyd.lang.unique_id()}"


def default_version_pattern() -> annize.data.version.VersionPattern:
    return annize.flow.run_context.object_by_name(_CONTEXT__DEFAULT_VERSION_PATTERN) or CommonVersionPattern()


def project_versions() -> list[annize.data.Version]:
    return annize.flow.run_context.objects_by_type(annize.data.Version)


class NumericVersionPatternPart(annize.data.version.NumericVersionPatternPart):
    pass


class SeparatorVersionPatternPart(annize.data.version.SeparatorVersionPatternPart):
    pass


class OptionalVersionPatternPart(annize.data.version.OptionalVersionPatternPart):
    pass


class ConcatenatedVersionPatternPart(annize.data.version.ConcatenatedVersionPatternPart):
    pass


class VersionPattern(annize.data.version.VersionPattern):
    pass


class CommonVersionPattern(VersionPattern):

    def __init__(self):
        super().__init__(parts=(
            NumericVersionPatternPart(name="major"),
            SeparatorVersionPatternPart(text="."),
            NumericVersionPatternPart(name="minor"),
            OptionalVersionPatternPart(parts=(
                SeparatorVersionPatternPart(text="."),
                NumericVersionPatternPart(name="build")))))
