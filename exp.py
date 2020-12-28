from __future__ import annotations

import functools
import heapq
from dataclasses import dataclass, fields
from itertools import islice
from time import timezone
from typing import List

# import pretty_errors
import requests
from colorama import Fore, Style, init
from requests.exceptions import HTTPError
from requests_html import HTMLSession

from hentai import *

init(autoreset=True)

# pretty_errors.configure()

@dataclass
class Homepage:
    popular_now: List[Hentai]
    new_uploads: List[Hentai]

def get_homepage(handler=RequestHandler()) -> Homepage:
    try:
        response = HTMLSession().get(Hentai.HOME)
    except HTTPError as error:
        print(f"{Fore.RED}{error}")
    else:
        titles = response.html.find("div.index-popular", first=True).text

        return Homepage(
            popular_now=[doujin for doujin in Utils.search_by_query(query='*', sort=Sort.PopularToday) if str(doujin) in titles],
            new_uploads=Utils.browse_homepage(1, 1, handler)
        )

def dictionary(doujin: Hentai, options: List[Option]) -> dict:
    data = {}
    for option in options:
        property = getattr(doujin, option.value)
        if isinstance(property, list) and len(property) != 0 and isinstance(property[0], Tag):
            data[option.value] = [tag.name for tag in property]
        elif option.value == 'title':
            data[option.value] = doujin.title(Format.Pretty)
        else:
            data[option.value] = property
    return data

if __name__ == '__main__':
    # doujin = Hentai(177013).title(Format.Pretty)

    # related = doujin.related
    # for r in related:
    #     print(f"{r.id}\t{r.title(Format.Pretty)}")

    print(Tag.search('shindol'))

    # last = doujin.thread[-1]
    
    # print(last.post_date)
    # print(Utils.get_random_hentai().response.ok)
    

