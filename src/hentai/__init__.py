#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from requests import HTTPError

from .hentai import *
from .hentai import __version__


def main():
    parser = argparse.ArgumentParser(prog=package_name)
    subparser = parser.add_subparsers(dest='command')

    parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('--verbose', action='store_true', help="increase output verbosity")

    download_parser = subparser.add_parser('download', help="download doujin (CWD by default)")
    download_parser.add_argument('--id', type=int, nargs='+', help="magic number")
    download_parser.add_argument('--dest', type=Path, default=Path.cwd(), help="download directory (CWD by default)")

    preview_parser = subparser.add_parser('preview', help="print doujin preview")
    preview_parser.add_argument('--id', type=int, nargs='+', help="magic number")

    args = parser.parse_args()
    
    if args.command == 'download':
        count = len(args.id)
        for id_ in args.id:
            try:
                doujin = Hentai(id_)
                doujin.download(dest=args.dest, progressbar=args.verbose)
            except HTTPError as error:
                print(f"Download #{str(id_).zfill(6)}: {error}", file=sys.stderr)
                count -= 1
        if count: print(f"Stored {count} doujin{'s' if count > 1 else ''} in {str(args.dest)!r}")

    if args.command == 'preview':
        for id_ in args.id:
            try:
                doujin = Hentai(id_)
                print(doujin.title(Format.Pretty))
                print(f"Genres: {Tag.get(doujin.tag, 'name')}\n")
            except HTTPError:
                print(f"Error: #{str(id_).zfill(6)} does not exist")

if __name__ == '__main__':
    main()
