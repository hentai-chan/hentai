#!/usr/bin/env python3

import ctypes
import locale
import platform

from .hentai import *

MSG = {
    'en_GB': 'You discovered a function that is still not implemented yet!',
    'en_US': 'You discovered a function that is still not implemented yet!',
    'ja_JP': 'まだ実装されていない機能が見つかりました！',
    'es_ES': 'Has descubierto una función que aún no se ha implementado!'
}

def main():
    if platform.system() == 'Windows':
        windll = ctypes.windll.kernel32
        lang = locale.windows_locale[windll.GetUserDefaultUILanguage()]
        err_msg = MSG.get(lang, 'en_US')
    else:
        lang = locale.getdefaultlocale()[0]
        err_msg = MSG.get(lang, 'en_US')

    raise NotImplementedError(f"{Fore.RED}{err_msg}")

if __name__ == '__main__':
    main()
