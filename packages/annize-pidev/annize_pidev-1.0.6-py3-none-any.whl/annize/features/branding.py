# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Branding.
"""
import annize.flow.run_context
import annize.data


class BrandColor(annize.data.Color):
    pass


def brand_color(*, none_on_undefined: bool = False) -> annize.data.Color:
    for obj in annize.flow.run_context.objects_by_type(BrandColor):
        return obj
    return None if none_on_undefined else annize.data.Color(red=0.3, green=0.3, blue=0.3)
