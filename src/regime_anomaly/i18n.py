"""Small JSON-based translation layer for the Streamlit interface."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files

DEFAULT_LOCALE = "pt-BR"
SUPPORTED_LOCALES = ("pt-BR", "en")
LOCALE_LABELS = {"pt-BR": "Português (Brasil)", "en": "English"}


@lru_cache(maxsize=len(SUPPORTED_LOCALES))
def translations(locale: str) -> dict[str, str]:
    """Load a supported locale, falling back to Brazilian Portuguese."""
    selected_locale = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    resource = files("regime_anomaly").joinpath("locales", f"{selected_locale}.json")
    with resource.open(encoding="utf-8") as translation_file:
        return json.load(translation_file)


def translate(key: str, locale: str = DEFAULT_LOCALE, **values: object) -> str:
    """Translate a key and interpolate any named values."""
    messages = translations(locale)
    message = messages.get(key, translations(DEFAULT_LOCALE).get(key, key))
    return message.format(**values)
