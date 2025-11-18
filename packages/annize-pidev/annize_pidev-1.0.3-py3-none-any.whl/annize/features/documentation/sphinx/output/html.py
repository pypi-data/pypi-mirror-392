# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based HTML documentation output.
"""
import html
import json

import annize.asset
import annize.features._pidev.common
import annize.features.base
import annize.features.documentation.common
import annize.features.documentation.sphinx.output.common
import annize.fs
import annize.i18n


class HtmlOutputSpec(annize.features.documentation.common.HtmlOutputSpec):
    """
    Sphinx HTML documentation output. This extends the superclass by some optional, Sphinx-specific arguments.
    """

    def __init__(self, *, is_homepage: bool = False,
                 theme: str|None = None,
                 masterlink: str|None = None,
                 logo_image: annize.fs.TFilesystemContent|None = None,
                 background_image: annize.fs.TFilesystemContent|None = None):
        """
        :param theme: The Sphinx html theme name.
        :param masterlink: Url that overrides the target of the main heading (which is also a link).
        """
        super().__init__(is_homepage=is_homepage)
        self.__theme = theme
        self.__masterlink = masterlink
        self.__logo_image = logo_image
        self.__background_image = background_image

    @property
    def theme(self) -> str|None:
        return self.__theme

    @property
    def masterlink(self) -> str|None:
        return self.__masterlink

    @property
    def logo_image(self) -> annize.fs.FilesystemContent|None:
        return self.__logo_image

    @property
    def background_image(self) -> annize.fs.FilesystemContent|None:
        return self.__background_image


@annize.features.documentation.sphinx.output.common.register_output_generator
class HtmlOutputGenerator(annize.features.documentation.sphinx.output.common.OutputGenerator):
    """
    HTML documentation output generator.
    """

    @classmethod
    def is_compatible_for(cls, output_spec):
        return isinstance(output_spec, annize.features.documentation.common.HtmlOutputSpec)

    def format_name(self):
        return "html"

    def prepare_generate(self, info):
        info.entry_path = f"{info.config_values["master_doc"]}.html"
        title = annize.i18n.translate(info.document.title)
        short_title = annize.i18n.translate(info.document.short_title)
        title_tagline = annize.i18n.translate(info.document.title_tagline or "")
        is_homepage = self.output_spec.is_homepage

        if isinstance(self.output_spec, HtmlOutputSpec):
            masterlink = self.output_spec.masterlink
            theme = self.output_spec.theme
            logo_image = self.output_spec.logo_image.path() if self.output_spec.logo_image else None
            background_image = self.output_spec.background_image.path() if self.output_spec.background_image else None

        else:
            masterlink = None
            short_title = None
            theme = None
            logo_image = None
            background_image = None

        theme = theme or "pimpinella_anisum"

        info.config_values["html_theme"] = theme
        info.config_values["html_theme_path"] = [str(_) for _ in (
            *info.config_values.get("html_theme_path", ()),
            annize.features._pidev.common.data_dir)]
        info.config_values["html_static_path"] = html_static_paths = [str(_) for _
                                                                      in info.config_values.get("html_static_path", ())]

        if short_title or title:
            info.config_values["html_short_title"] = short_title or title
        if title:
            info.config_values["html_title"] = title

        html_theme_options_override = dict(sidebartreesmall=not is_homepage, menusectionindicator=not is_homepage,
                                           shortdesc=title_tagline)

        if masterlink:
            html_theme_options_override["masterlink"] = masterlink

        if theme == "pimpinella_anisum":
            info.config_values["html_css_files"] = []
            base_color = annize.features.base.brand_color()

            # TODO  hacks
            background_image = annize.features.base.project_directory()("media/background.png")
            if not background_image.exists():
                background_image = background_image.parent("background.jpg")
            for logo_image in annize.features.base.project_directory()("media/logo").children():
                if logo_image.name.endswith(".64.png"):
                    break

            if background_image:
                bgimagename = f"_annize_bgimage.{background_image.name}"
                bgimagecssdirfs = info.document_source_dir(bgimagename)
                background_image.copy_to(bgimagecssdirfs(bgimagename))
                html_static_paths.append(str(bgimagecssdirfs))
                html_theme_options_override["bgimage"] = bgimagename
            for bcaa in range(10):
                for bcab in range(10):
                    for bcac in range(20):
                        sbcac = "abcdefghijklmnopqrst"[bcac]
                        ncolor = base_color.with_modified(lightness=(bcab+1)/10)
                        ncolor = ncolor.with_modified(saturation=ncolor.saturation * (bcac+1)/10)
                        html_theme_options_override[f"brandingcolor_{sbcac}{bcaa}{bcab}"] = (
                            f"rgb({ncolor.red * 255},{ncolor.green * 255},{ncolor.blue * 255},"
                            f"{(bcaa + 1) / 10})")

        if is_homepage:
            html_theme_options_override.update(sidebarhidelvl1=True, headhidelvl1=True, sidebarhidelvl3up=True,
                                               shorthtmltitle=True)

        html_theme_options = info.config_values["html_theme_options"] = info.config_values.get("html_theme_options", {})
        html_theme_options.update(html_theme_options_override)

        html_static_paths.append(str(annize.features._pidev.common.data_dir("icons/docrender")))

        if logo_image:
            logo_image_destination_name = f"_annize_logo_image.{logo_image.name}"
            logo_image.copy_to(info.document_config_dir(logo_image_destination_name))
            info.config_values["html_logo"] = logo_image_destination_name

    def multi_language_frame(self, document):
        result = super().multi_language_frame(document)
        links_html = ""
        for language in result.culture_names:
            links_html += (f"<a href='{html.escape(result.entry_path_for_language(language))}'>"
                           f"{html.escape(annize.i18n.culture_by_spec(language).english_lang_name)}"
                           f"</a><br/>")
        language_entry_points = {language: result.entry_path_for_language(language)
                                 for language in result.culture_names}

        title = annize.i18n.translate(document.title, culture="en")  # TODO noh  hardcoded en
        title_html = f"<title>{html.escape(title)}</title>" if title else ""
        result.file.path()("index.html").write_file(
            f"<!DOCTYPE html>"
            f"<html>"
            f"<head>"
            f"<meta charset='utf-8'>{title_html}"
            f"<script>"
            f"var myLanguage = navigator.language;"
            f"var languageEntryPoints = {json.dumps(language_entry_points)};"
            f"function trylang(c) {{"
            f"    var entrypoint = languageEntryPoints[c];"
            f"    if (entrypoint) {{"
            f"        document.location.href = entrypoint;"
            f"        return true;"
            f"    }}"
            f"}};"
            f"trylang(myLanguage) || trylang(myLanguage.substring(0,2)) || trylang('en') || trylang('?');"
            f"</script>"
            f"</head>"
            f"<body>"
            f"<h1>🗣 🌐 ❓</h1>"
            f"{links_html}"
            f"</body>"
            f"</html>")  # TODO what with language = "?" ?!

        result._set_entry_path("index.html")
        return result
