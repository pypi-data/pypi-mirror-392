# src/ipsumheroes/__init__.py
"""
ipsumheroes —  Utility functions and package initialization

*Where lorem ipsum meets the legends of history.*

A playful **lorem ipsum generator** that sprinkles placeholder text with
the names and quotes of **history’s luminaries and heroes**. Ideal for
developers, designers, and writers who want their filler text to be more
inspiring.

Supports multiple languages (EN, NL, DE, FR, ES) and highly customizable
text generation.

Features
--------
- Generate lorem ipsum with optional luminary enrichment
- Adjustable number of sentences, paragraphs, and sections
- Configurable punctuation, indentation, tags (XML/HTML), and wrapping
- Lightweight and easy to integrate

Full manual and detailed usage examples:
https://github.com/rikroos/ipsumheroes/blob/master/docs/manual.md
"""

from importlib.metadata import version, PackageNotFoundError
from typing import cast

from konvigius import Config
from .topic import get_available_topics, add_topic
from .resources.config_schema import SCHEMA
from .generator import paragraphs, paragraphs_text, sentences, sentences_text


__all__ = [
    "add_topic",
    "changelog",
    "get_available_topics",
    "get_config",
    "paragraphs",
    "paragraphs_text",
    "sentences",
    "sentences_text",
]

__VERSION__ = None
_cfg = None  # reference to the default configuration setup


def changelog() -> str:
    """Return the contents of the package-distributed CHANGELOG.md"""
    from importlib.resources import files

    pkg = cast(str, __package__)  # satisfy pyright
    return (files(pkg) / "CHANGELOG.md").read_text(encoding="utf-8")


def get_config(new: bool = False) -> Config:
    """Lazily retrieves the configuration object or a new configuration object.

    If the configuration has not been set up, a new instance of
    `konvigius.Config` will be created automatically.

    If the parameter ``new`` is True, then a new configuration object is
    returned. This will not overwrite the existing configuration object.
    """
    global _cfg
    if new:
        _cfg = Config.config_factory(SCHEMA)
    else:
        if _cfg is None:
            _cfg = Config.config_factory(SCHEMA)
    return _cfg


def main():
    global __VERSION__
    try:
        __VERSION__ = version("ipsumheroes")
    except PackageNotFoundError:
        __VERSION__ = "0.0.0"  # fallback for development


# --- calling main: -----------------------------------------------------------

main()


# === END ===
