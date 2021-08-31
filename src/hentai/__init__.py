#!/usr/bin/env python3

from __future__ import annotations

import argparse
import errno
import sys
from distutils.util import strtobool
from pathlib import Path
from typing import List

from requests import HTTPError

from .hentai import *
from .hentai import __version__


def __print_dict(dictionary: dict, indent=4) -> None:
    print("{\n%s\n}" % '\n'.join([f"\033[36m{indent*' '}{key}\033[0m: \033[32m{value}\033[0m" for key, value in dictionary.items()]))

def __from_file(path: Path) -> List[int]:
    with open(path, mode='r', encoding='utf-8') as file_handler:
        return [int(line.strip('#').rstrip()) for line in file_handler.readlines()]

def main():
    parser = argparse.ArgumentParser(prog=package_name)
    parser._positionals.title = 'Commands'
    parser._optionals.title = 'Arguments'

    parser.add_argument('-v', '--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('-V', '--verbose', default=True, action=argparse.BooleanOptionalAction, help="increase output verbosity")

    subparser = parser.add_subparsers(dest='command')

    download_parser = subparser.add_parser('download', help="download doujin (CWD by default)")
    download_parser.add_argument('--id', type=int, nargs='*', help="magic number")
    download_parser.add_argument('--dest', type=Path, default=Path.cwd(), help="download directory (CWD by default)")
    download_parser.add_argument('-c', '--check', default=True, action=argparse.BooleanOptionalAction, help="check for duplicates")
    download_parser.add_argument('--batch-file', type=Path, nargs='?', help="file containing IDs to download, one ID per line")

    preview_parser = subparser.add_parser('preview', help="print doujin preview")
    preview_parser.add_argument('--id', type=int, nargs='+', required=True, help="magic number")

    args = parser.parse_args()

    try:
        if args.command == 'download':
            for id_ in (args.id or __from_file(args.batch_file)):
                doujin = Hentai(id_)
                if args.check and Path(args.dest).joinpath(str(doujin.id)).exists():
                    print(f"\033[33mWarning:\033[0m A file with the same name already exists in {str(args.dest)!r}.")
                    choice = input("Proceed with download? [Y/n] ")
                    if choice == '' or strtobool(choice):
                        doujin.download(dest=args.dest, progressbar=args.verbose)
                else:
                    doujin.download(dest=args.dest, progressbar=args.verbose)
        elif args.command == 'preview':
            for id_ in args.id:
                doujin = Hentai(id_)
                values = [doujin.title(Format.Pretty), doujin.artist[0].name, doujin.num_pages, doujin.num_favorites, doujin.url]
                if args.verbose:
                    __print_dict(dict(zip(['Title', 'Artist', 'NumPages', 'NumFavorites', 'URL'], values)))
                else:
                    print(','.join(map(str, values)))
        else:
            parser.print_help(sys.stderr)
            sys.stderr(errno.EINVAL)
    except HTTPError as error:
        print(f"\033[31mError:\033[0m {error}", file=sys.stderr)

if __name__ == '__main__':
    main()
