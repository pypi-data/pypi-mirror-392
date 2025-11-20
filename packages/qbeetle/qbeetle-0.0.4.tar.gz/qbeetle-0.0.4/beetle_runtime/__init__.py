import locale
import os
import gettext
from babel import Locale

APP_NAME = "beetle_runtime"
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")


def get_translator():
    _ = gettext.gettext

    try:
        loc = locale.getdefaultlocale()
        language_locale = Locale.parse(loc[0])
        if language_locale.language == "zh":
            l10n = gettext.translation(APP_NAME, localedir=LOCALE_DIR, languages=["zh"])
        else:
            l10n = gettext.translation(APP_NAME, localedir=LOCALE_DIR, languages=["en"])
        l10n.install()
        _ = l10n.gettext
    except Exception as e:
        print(e, "\nUsing defalt language - English")
    return _


_ = get_translator()


class BeetleError(Exception):
    pass
