# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based Python documentation.
"""
import os
import subprocess

import annize.features.documentation.sphinx.common
import annize.features.documentation.sphinx.rst
import annize.fs


class Python3ApiReferenceLanguage(annize.features.documentation.sphinx.common.ApiReferenceLanguage):
    """
    Python 3 language support for API references.
    """

    def __init__(self, *, show_undocumented_members: bool = True, show_protected_members: bool = True):
        self.__show_undocumented_members = show_undocumented_members
        self.__show_protected_members = show_protected_members

    def generate_sources(self, info):
        info.config_values["autodoc_default_options"] = {"member-order": "bysource"}
        self.__patch_property_types_in_docstrings(info.source)

        sphinx_apidoc_options = ["members", "show-inheritance"]
        if self.__show_undocumented_members:
            sphinx_apidoc_options += ["undoc-members"]

        cmd = ["sphinx-apidoc", "--no-toc", "--implicit-namespaces", "--module-first"]
        if self.__show_protected_members:
            cmd += ["--private"]
        cmd += ["-o", info.document_source_dir, info.source]
        subprocess.check_call(cmd, env={**os.environb, "SPHINX_APIDOC_OPTIONS": ",".join(sphinx_apidoc_options)},
                              cwd=info.source)

        info.document_source_dir("index.rst").write_text(
            f"{annize.features.documentation.sphinx.rst.heading(info.heading, level=0)}\n"
            f".. toctree::\n"
            f"    :glob:\n"
            f"\n"
            f"    {info.source.name}\n")

        return "index"

    def __patch_property_types_in_docstrings(self, source: annize.fs.Path) -> None:  # TODO# remove this when Sphinx can do it better
        for python_code_file in source.rglob("/**/*.py"):
            if python_code_file.is_relative_to(source):
                python_code = python_code_file.read_text()
                property_idx = None
                while True:
                    property_idx = python_code.rfind("@property", 0, property_idx)
                    if property_idx == -1:
                        break
                    python_code = self.__patch_property_types_in_docstrings__patch_property(python_code, property_idx)
                python_code_file.write_text(python_code)

    def __patch_property_types_in_docstrings__patch_property(self, python_code: str, property_idx: int) -> str:
        i_brace = python_code.find("(", property_idx)
        if i_brace != -1:
            i_def = python_code.find("def", property_idx, i_brace)
            if i_def != -1:
                property_name = python_code[i_def + 3:i_brace].strip()

                open_braces_count = 1
                while (open_braces_count > 0) and i_brace < len(python_code):
                    i_brace += 1
                    if python_code[i_brace] == "(":
                        open_braces_count += 1
                    elif python_code[i_brace] == ")":
                        open_braces_count -= 1

                i_colon = python_code.find(":", i_brace)
                if i_colon != -1:
                    return_type_str = python_code[i_brace + 1:i_colon].strip()
                    if return_type_str.startswith("->"):
                        return_type_name = return_type_str[2:].strip()
                        if return_type_name[0] in ('"', "'"):
                            return_type_name = return_type_name[1:-1]

                        i_next_line = python_code.find("\n", i_colon) + 1
                        if i_next_line != 0:
                            indent_by = len(python_code[i_next_line:]) - len(python_code[i_next_line:].lstrip())
                            body_begin_chunk = python_code[i_next_line:].strip()[:3]
                            for body_begin_chunk_ in ("'''", '"""'):
                                if body_begin_chunk == body_begin_chunk_:
                                    python_code = self.__patch_property_types_in_docstrings__patch_docstring(
                                        property_name, python_code, i_next_line, indent_by, return_type_name,
                                        body_begin_chunk)
                                    break
                            else:
                                python_code = self.__patch_property_types_in_docstrings__add_docstring(
                                    property_name, python_code, i_next_line, indent_by, return_type_name)

        return python_code

    def __patch_property_types_in_docstrings__patch_docstring(
            self, property_name: str, python_code: str, i_next_line: int, indent_by: int, return_type_name: str,
            body_begin_chunk: str) -> str:
        i_docstring_closer = python_code.find(body_begin_chunk, python_code.find(body_begin_chunk, i_next_line) + 1)
        i_docstring_split = python_code.rfind("\n", 0, i_docstring_closer) + 1 + indent_by
        is_settable = f"@{property_name}.setter" in python_code
        new_line = "\n" + (" " * indent_by)
        return (python_code[:i_docstring_split] + new_line + f":rtype: {return_type_name}"
                + (f"\n{new_line}This property is also settable." if is_settable else "")
                + new_line + python_code[i_docstring_split:])

    def __patch_property_types_in_docstrings__add_docstring(
            self, property_name: str, python_code: str, i_next_line: int, indent_by: int, return_type_name: str) -> str:
        i_split = i_next_line + indent_by
        return self.__patch_property_types_in_docstrings__patch_docstring(
            property_name,
            python_code[:i_split] + 2 * ("'''\n" + (" " * indent_by)) + python_code[i_split:],
            i_next_line, indent_by, return_type_name, "'''")
