#!/usr/bin/env python3

import argparse
import errno
import sys
from pathlib import Path

from requests import HTTPError

from .hentai import *
from .hentai import __version__


def main():
    parser = argparse.ArgumentParser(prog=package_name)
    parser._positionals.title = 'Commands'
    parser._optionals.title = 'Arguments'

    parser.add_argument('-v', '--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('-V', '--verbose', default=True, action=argparse.BooleanOptionalAction, help="increase output verbosity")

    subparser = parser.add_subparsers(dest='command')

    download_parser = subparser.add_parser('download', help="download doujin (CWD by default)")
    download_parser.add_argument('--id', type=int, nargs='+', required=True, help="magic number")
    download_parser.add_argument('--dest', type=Path, default=Path.cwd(), help="download directory (CWD by default)")

    preview_parser = subparser.add_parser('preview', help="print doujin preview")
    preview_parser.add_argument('--id', type=int, nargs='+', required=True, help="magic number")

    args = parser.parse_args()

    if args.command == 'download':
        count = len(args.id)
        for id_ in args.id:
            try:
                doujin = Hentai(id_)
                doujin.download(dest=args.dest, progressbar=args.verbose)
            except HTTPError as error:
                print(f"\033[31mDownloadError:\033[0m {error}", file=sys.stderr)
                count -= 1
        if count:
            print(f"Stored {count} doujin{'s' if count > 1 else ''} in {str(args.dest)!r}")
    elif args.command == 'preview':
        for id_ in args.id:
            try:
                doujin = Hentai(id_)
                print(f"\033[32m{doujin.title(Format.Pretty)!r} by {Tag.get(doujin.artist, 'name')}\033[0m")
                print(f"genres:\t{Tag.get(doujin.tag, 'name')}")
                print(f"langs:\t{Tag.get(doujin.language, 'name')}")
                print(f"pages:\t{doujin.num_pages}", end='\n\n' if id_ != len(args.id) else '')
            except HTTPError as error:
                print(f"\033[31mPreviewError:\033[0m {error}", file=sys.stderr)
    else:
        parser.print_help(sys.stderr)
        sys.stderr(errno.EINVAL)

if __name__ == '__main__':
    main()
