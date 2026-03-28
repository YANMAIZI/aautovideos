import json
import locale
import os


def load_language_list(language):
    # Try both relative paths (for different working dirs)
    paths_to_try = [
        f"./i18n/locale/{language}.json",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "locale", f"{language}.json"),
    ]
    for path in paths_to_try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"Locale file not found for: {language}")


class I18nAuto:
    def __init__(self, language=None):
        # Priority: explicit arg > env var > system locale
        if language in ["Auto", None]:
            language = os.environ.get("VIRALCUTTER_LANG", None)
        if language in ["Auto", None]:
            try:
                language = locale.getdefaultlocale()[0]
            except Exception:
                language = None

        # Fallback chain: exact match -> language only (e.g. 'ru') -> ru_RU
        # Project default is Russian for a fully localized UX out of the box.
        candidate = language or "ru_RU"
        if not self._locale_exists(candidate):
            # Try just the language prefix: ru_RU -> ru (won't exist, but pattern)
            short = candidate.split("_")[0] if candidate else "en"
            # Try common mappings
            lang_map = {"ru": "ru_RU", "pt": "pt_BR", "en": "en_US"}
            candidate = lang_map.get(short, "ru_RU")
            if not self._locale_exists(candidate):
                candidate = "ru_RU"

        self.language = candidate
        self.language_map = load_language_list(candidate)

    def _locale_exists(self, lang):
        if not lang:
            return False
        paths = [
            f"./i18n/locale/{lang}.json",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "locale", f"{lang}.json"),
        ]
        return any(os.path.exists(p) for p in paths)

    def __call__(self, key):
        return self.language_map.get(key, key)

    def __repr__(self):
        return "Use Language: " + self.language
