#!/usr/bin/env python3
"""
Settings for text loader.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict


@viewer
@dataclass
class TxtLoaderSettings:
    """
    Settings for text loader

    Attributes:
        filepath: Path to the file to load
        encoding: File encoding (utf-8 by default)
        read_kwargs: Additional arguments to pass to open/read
    """

    filepath: str
    encoding: str = "utf-8"
    read_kwargs: Dict = None

    def __post_init__(self):
        self.read_kwargs = self.read_kwargs or {}
