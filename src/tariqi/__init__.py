"""Tariqi Legal AI core package."""

from .answerer import TariqiAssistant
from .calculator import FineCalculator
from .config import AppConfig
from .pipeline import build_index

__all__ = [
    "AppConfig",
    "FineCalculator",
    "TariqiAssistant",
    "build_index",
]
