#!/usr/bin/env python3
"""
Text Loader.
"""

from pypassist.mixin.cachable import Cachable

from ...base import Loader
from .settings import TxtLoaderSettings


class TxtLoader(Loader, register_name="txt"):
    """
    Loader for text files.
    """

    SETTINGS_DATACLASS = TxtLoaderSettings

    @Cachable.caching_method()
    def _load_impl(self, settings):
        """
        Load data from a text file.

        Args:
            settings: Settings for the txt loader.

        Returns:
            str: The loaded file content.
        """
        with open(
            settings.filepath,
            "r",
            encoding=settings.encoding,
            **settings.read_kwargs,
        ) as f:
            return f.read()
