#!/usr/bin/env python3

from __future__ import annotations

import argparse
import errno
import sys
from collections import namedtuple
from distutils.util import strtobool
from pathlib import Path
from typing import List

from requests import HTTPError

from .hentai import *
from .hentai import __version__


def __print_dict(dictionary: dict, indent=4) -> None:
    print("{\n%s\n}" % '\n'.join([f"{COLORS['blue']}{indent * ' '}{key}{COLORS['reset']}: {COLORS['green']}{value}{COLORS['reset']}," for key, value in dictionary.items()]))

def __from_file(path: Path) -> List[int]:
    with open(path, mode='r', encoding='utf-8') as file_handler:
        return [int(line.strip('#').rstrip()) for line in file_handler.readlines()]

def format_proxies(proxies: str) -> dict:
    return {prot: f"{prot}://{ip}" for (prot, ip) in [proxy.split('://') for proxy in proxies.split()]}

def main():
    formatter = lambda prog: argparse.HelpFormatter(prog,max_help_position=52)
    parser = argparse.ArgumentParser(prog=package_name, formatter_class=formatter, description="hentai command line interface.")
    parser._positionals.title = 'Commands'
    parser._optionals.title = 'Arguments'

    parser.add_argument('-v', '--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('-V', '--verbose', default=True, action='store_true', help="increase output verbosity (default: %(default)s)")
    parser.add_argument('--no-verbose', dest='verbose', action='store_false', help="run commands silently")
    parser.add_argument('-a', '--user-agent', type=str, default=None, help="configure custom User-Agent (optional)")
    parser.add_argument('-p', '--proxies', type=str, default=None, help="configure HTTP and/or HTTPS proxies (optional)")

    subparser = parser.add_subparsers(dest='command')

    download_help_msg = "download a doujin from https://nhentai.net/ to your local harddrive"
    download_parser = subparser.add_parser('download', description=download_help_msg, help=download_help_msg)
    download_parser.add_argument('--id', type=int, nargs='*', help="doujin ID")
    download_parser.add_argument('--dest', type=Path, metavar='PATH', default=Path.cwd(), help="download directory (default: %(default)s)")
    download_parser.add_argument('-c', '--check', default=True, action='store_true', help="check for duplicates (default: %(default)s)")
    download_parser.add_argument('--no-check', dest='check', action='store_false', help="disable checking for duplicates")
    download_parser.add_argument('--batch-file', type=Path, metavar='PATH', nargs='?', help="file containing IDs to download, one ID per line")

    preview_help_msg = "print doujin meta data"
    preview_parser = subparser.add_parser('preview', description=preview_help_msg, help=preview_help_msg)
    preview_parser.add_argument('--id', type=int, nargs='+', required=True, help="doujin ID")

    log_help_msg = "access the CLI logger"
    log_parser = subparser.add_parser('log', description=log_help_msg, help=log_help_msg)
    log_parser.add_argument('--reset', action='store_true', help="reset all log file entries")
    log_parser.add_argument('--path', action='store_true', help="return the log file path")
    log_parser.add_argument('--list', action='store_true', help='read the log file')

    args = parser.parse_args()

    try:
        if args.command == 'download':
            for id_ in (args.id or __from_file(args.batch_file)):
                doujin = Hentai(id_)
                if args.check and Path(args.dest).joinpath(str(doujin.id)).exists():
                    print(f"{COLORS['yellow']}WARNING:{COLORS['reset']} A file with the same name already exists in {str(args.dest)!r}.")
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
        elif args.command == 'log':
            if args.reset:
                open(get_logfile_path(), mode='w', encoding='utf-8').close()
            if args.path:
                print(get_logfile_path())
            if args.list:
                with open(get_logfile_path(), mode='r', encoding='utf-8') as file_handler:
                    log = file_handler.readlines()

                    if not log:
                        print(f"{COLORS['yellow']}INFO:{COLORS['reset']} there is nothing to read because the log file is empty")
                        return

                    parse = lambda line: line.strip('\n').split('::')
                    Entry = namedtuple('Entry', 'timestamp levelname lineno name message')

                    tabulate = "{:<7} {:<8} {:<30} {:<30}".format

                    print(COLORS['green'] + tabulate('Line', 'Level', 'File Name', 'Message') + COLORS['reset'])

                    for line in log:
                        entry = Entry(parse(line)[0], parse(line)[1], parse(line)[2], parse(line)[3], parse(line)[4])
                        print(tabulate(entry.lineno.zfill(4), entry.levelname, entry.name, entry.message))
        else:
            parser.print_help(sys.stderr)
            sys.stderr(errno.EINVAL)
    except HTTPError as error:
        print(f"{COLORS['red']}ERROR:{COLORS['reset']} {error}", file=sys.stderr)
        logger.error("CLI caught an HTTP error (network down?): %s" % str(error))
    except Exception as error:
        print(f"{COLORS['red']}ERROR:{COLORS['reset']} {error}", file=sys.stderr)
        logger.error("CLI caught an error: %s" % str(error))

if __name__ == '__main__':
    main()
