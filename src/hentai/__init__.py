#!/usr/bin/env python3

import argparse

from .hentai import *
from .hentai import __version__

def main():
    parser = argparse.ArgumentParser(prog=package_name)
    parser.add_argument('-id', type=int, help="download this doujin in the current working directory")
    parser.add_argument('-version', action='version', version=f"%(prog)s {__version__}")
    args = parser.parse_args()
    Hentai(args.id).download(progressbar=True)

if __name__ == '__main__':
    main()
