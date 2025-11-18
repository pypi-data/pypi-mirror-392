# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import annize.features._pidev.common
import annize.i18n


annize.i18n.add_translation_provider(annize.i18n.GettextTranslationProvider(
    annize.features._pidev.common.data_dir("mo")), priority=50_000)


tr = annize.i18n.tr
TrStr = annize.i18n.TrStr
