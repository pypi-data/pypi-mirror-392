# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
GPG support.
"""
import abc


class Key(abc.ABC):

    @property
    @abc.abstractmethod
    def public_key_ascii(self) -> str:
        pass
