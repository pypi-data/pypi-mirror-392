# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Generator for some source parts of Sphinx-based reStructuredText documentations.
"""
import annize.i18n


def heading(text: annize.i18n.TrStrOrStr, *, level: int, anchor: str|None = None, special: bool = False) -> str:
    """
    Generates documentation source for a section heading.

    :param text: The heading text.
    :param level: The heading level. Level 0 is the title and higher numbers are deeper levels of text structure. You
                  should not use levels higher than 5.
    :param anchor: The anchor name for references.
    :param special: Whether to use special characters instead of the default ones. Useful for generating outer document
                    sources with other document sources embedded (which would otherwise lead to conflicting levels).
    """
    text = str(text)
    characters = '''#*=-^"~'''

    if special:
        line_char, with_overline = {0: (characters[2], True),
                                    1: (characters[3], True),
                                    2: (characters[4], True),
                                    3: (characters[6], True)}.get(level, (characters[6], False))

    else:
        # https://lpn-doc-sphinx-primer.readthedocs.io/en/stable/concepts/heading.html
        line_char, with_overline = {0: (characters[0], True),
                                    1: (characters[1], True),
                                    2: (characters[0], False),
                                    3: (characters[1], False),
                                    4: (characters[2], False),
                                    5: (characters[3], False),
                                    6: (characters[4], False),
                                    7: (characters[5], False)}.get(level, (characters[5], True))

    header_decoration_str = (line_char * len(text))
    sub_header_decoration_str = f"{header_decoration_str}\n" if with_overline else ""
    anchor_str = f".. _{anchor}:\n\n" if anchor else ""

    return f"\n\n{anchor_str}{sub_header_decoration_str}{text}\n{header_decoration_str}\n\n"
