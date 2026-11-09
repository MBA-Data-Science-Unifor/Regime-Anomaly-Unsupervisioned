from regime_anomaly.i18n import (
    DEFAULT_LOCALE,
    SUPPORTED_LOCALES,
    translate,
    translations,
)


def test_brazilian_portuguese_is_the_default_locale() -> None:
    assert DEFAULT_LOCALE == "pt-BR"
    assert translate("nav.overview") == "Visão geral"


def test_supported_locales_have_the_same_translation_keys() -> None:
    default_keys = translations(DEFAULT_LOCALE).keys()

    for locale in SUPPORTED_LOCALES:
        assert translations(locale).keys() == default_keys


def test_english_remains_available() -> None:
    assert translate("nav.overview", "en") == "Overview"
