#!/usr/bin/env python3

import argparse

from .hentai import *

__version__ = "3.2.4"
package_name = "hentai"
python_major = "3"
python_minor = "7"


def main():
    from hentai import Hentai
    parser = argparse.ArgumentParser(prog=package_name)
    parser.add_argument('--id', type=int, help="download this doujin in the current working directory")
    parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
    args = parser.parse_args()
    Hentai(args.id).download(progressbar=True)

if __name__ == '__main__':
    main()
