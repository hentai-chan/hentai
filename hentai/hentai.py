#!/usr/bin/env python3

"""
Implements a wrapper class around nhentai's RESTful API.
Copyright (C) 2020  hentai-chan (dev.hentai-chan@outlook.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urljoin, urlparse
from urllib.request import getproxies

import requests
from colorama import init, Fore
from faker import Faker
from requests import HTTPError, Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from tqdm import tqdm
from urllib3.util.retry import Retry

try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 7
except AssertionError:
    raise RuntimeError("Hentai requires Python 3.7+!") 

init(autoreset=True)

def _progressbar_options(iterable, desc, unit, color=Fore.GREEN, char='\u25CB', disable=False): 
    """
    Return options arguments for `tqdm` progressbars.
    """
    return {
        'iterable': iterable,
        'bar_format': "{l_bar}%s{bar}%s{r_bar}" % (color, Fore.RESET),
        'ascii': char.rjust(9, ' '), 
        'desc': desc, 
        'unit': unit.rjust(1, ' '), 
        'total': len(iterable), 
        'disable': not disable
    }

@dataclass
class Tag:
    """
    A data class that bundles related `Tag` properties and useful helper methods
    for interacting with tags.
    """
    id: int
    type: str
    name: str
    url: str
    count: int

    @staticmethod
    def get_ids(tags: List[Tag]) -> int or List[int]:
        """
        Return a list of IDs corresponding to the passed Tag objects.
        
        Example
        -------
            >>> from hentai import Hentai, Tag
            >>> doujin = Hentai(177013)
            >>> Tag.get_ids(doujin.artist)
            3981
        
        """
        ids = [tag.id for tag in tags]
        return ids[0] if len(ids) == 1 else ids

    @staticmethod
    def get_types(tags: List[Tag]) -> str or List[str]:
        """
        Return a list of types corresponding to the passed Tag objects.

        Example
        -------
            >>> from hentai import Hentai, Tag
            >>> doujin = Hentai(177013)
            >>> Tag.get_types(doujin.artist)
            'artist'
        """
        types = [tag.type for tag in tags]
        return types[0] if len(types) == 1 else types 

    @staticmethod
    def get_names(tags: List[Tag]) -> str or List[str]:
        """
        Return a list of capitalized names corresponding to the passed Tag objects.

        Example
        -------
            >>> from hentai import Hentai, Tag
            >>> doujin = Hentai(177013)
            >>> Tag.get_names(doujin.artist)
            'Shindol'
        """
        capitalize_all = lambda sequence: ' '.join([word.capitalize() for word in sequence.split(' ')])
        artists = [capitalize_all(tag.name) for tag in tags]
        return artists[0] if len(artists) == 1 else artists

    @staticmethod
    def get_urls(tags: List[Tag]) -> str or List[str]:
        """
        Return a list of URLs corresponding to the passed Tag objects.
        
        Example
        -------
            >>> from hentai import Hentai, Tag
            >>> doujin = Hentai(177013)
            >>> Tag.get_urls(doujin.artist)
            '/artist/shindol/'
        """
        urls = [tag.url for tag in tags]
        return urls[0] if len(urls) == 1 else urls

    @staticmethod
    def get_counts(tags: List[Tag]) -> int or List[int]:
        """
        Return a list of counts (of occurrences) corresponding to the passed Tag objects.

        Example
        -------
            >>> from hentai import Hentai, Tag
            >>> doujin = Hentai(177013)
            >>> Tag.get_counts(doujin.artist)
            279
        """
        counts = [tag.count for tag in tags]
        return counts[0] if len(counts) == 1 else counts


@dataclass
class Page:
    """
    A data class that bundles related `Page` properties.
    """
    url: str
    ext: str
    width: int
    height: int

    @property
    def filename(self) -> Path:
        """
        Return the file name for this `Page` as Path object.

        Example
        -------
            >>> from hentai import Hentai
            >>> doujin = Hentai(177013)
            >>> [page.filename for page in doujin.pages]
            [WindowsPath('1.jpg'), WindowsPath('2.jpg'), ...]
        """
        num = Path(urlparse(self.url).path).name
        return Path(num).with_suffix(self.ext)


@unique
class Sort(Enum):
    """
    Expose endpoints used to sort queries. Defaults to `Popular`.
    """
    Popular = 'popular'
    PopularYear = 'popular-year'
    PopularMonth = 'popular-month'
    PopularWeek = 'popular-week'
    PopularToday = 'popular-today'
    Date = 'date'


@unique
class Option(Enum):
    """
    Define export options for the `Hentai` and `Utils` class.
    """
    Raw = 'raw'
    ID = 'id'
    Title = 'title'
    Scanlator = 'scanlator'
    URL = 'url'
    API = 'api'
    MediaID = 'media_id'
    UploadDate = 'upload_date'
    Favorites = 'favorites'
    Tag = 'tag'
    Group = 'group'
    Parody = 'parody'
    Character = 'character'
    Language = 'language'
    Artist = 'artist'
    Category = 'category'
    Cover = 'cover'
    Thumbnail = 'thumbnail'
    Images = 'images'
    PageCount = 'pages'


@unique
class Format(Enum):
    """
    The title format. In some instances, `Format.Japanese` or `Format.Pretty` 
    return an empty string.
    """
    English = 'english'
    Japanese = 'japanese'
    Pretty = 'pretty'


@unique
class Extension(Enum):
    """
    Known file extensions used by `nhentai` images.
    """
    JPG = 'j'
    PNG = 'p'
    GIF = 'g'

    @classmethod
    def convert(cls, key: str) -> str:
        """
        Convert Extension enum to its string representation.

        Example
        -------
            >>> from hentai import Extension
            >>> Extension.convert('j')
            '.jpg'
        """
        return f".{cls(key).name.lower()}"


class RequestHandler(object):
    """
    Defines a synchronous request handler class that provides methods and 
    properties for working with REST APIs.
    """
    _timeout = (5, 5)
    _total = 5
    _status_forcelist = [413, 429, 500, 502, 503, 504]
    _backoff_factor = 1
    _fake = Faker()

    def __init__(self, 
                 timeout: Tuple[float, float]=_timeout, 
                 total: int=_total, 
                 status_forcelist: List[int]=_status_forcelist, 
                 backoff_factor: int=_backoff_factor):
        """
        Instantiates a new request handler object.
        """
        self.timeout = timeout
        self.total = total        
        self.status_forcelist = status_forcelist
        self.backoff_factor = backoff_factor

    @property
    def retry_strategy(self) -> Retry:
        """
        The retry strategy returns the retry configuration made up of the
        number of total retries, the status forcelist as well as the backoff
        factor. It is used in the session property where these values are 
        passed to the HTTPAdapter. 
        """
        return Retry(self.total, self.status_forcelist, self.backoff_factor)

    @property
    def session(self) -> Session:
        """
        Creates a custom session object. A request session provides cookie
        persistence, connection-pooling, and further configuration options
        that are exposed in the RequestHandler methods in form of parameters 
        and keyword arguments.
        """
        assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=self.retry_strategy))
        session.hooks['response'] = [assert_status_hook]
        session.headers.update({
            "User-Agent" : RequestHandler._fake.chrome(version_from=80, version_to=86, build_from=4100, build_to=4200)
        })
        return session
    
    def get(self, url: str, params: dict=None, **kwargs) -> Response:
        """
        Returns the GET request encoded in `utf-8`. Adds proxies to this session 
        on the fly if urllib is able to pick up the system's proxy settings.
        """
        response = self.session.get(url, timeout=self.timeout, params=params, proxies=getproxies(), **kwargs)
        response.encoding = 'utf-8'
        return response


class Hentai(RequestHandler):
    """
    Python Hentai API Wrapper
    =========================
    Implements a wrapper class around `nhentai`'s RESTful API that inherits from
    `RequestHandler`. Note that the content of this module is generally considered 
    NSFW.

    Basic Usage
    ------------
        >>> from hentai import Hentai
        >>> doujin = Hentai(177013)
        >>> print(doujin)
        '[ShindoLA] METAMORPHOSIS (Complete) [English]'

    Docs
    ----
    See full documentation is at <http://localhost:8080/projects/hentai>.
    """
    HOME = "https://nhentai.net/" 
    _URL = urljoin(HOME, '/g/')
    _API = urljoin(HOME, '/api/gallery/')

    def __init__(self, 
                 id: int=0, 
                 timeout: Tuple[float, float]=RequestHandler._timeout, 
                 total: int=RequestHandler._total, 
                 status_forcelist: List[int]=RequestHandler._status_forcelist, 
                 backoff_factor: int=RequestHandler._backoff_factor,
                 json: dict=None):
        """
        Start a request session and parse meta data from `nhentai.net` for this `id`.
        """
        if id and not json:
            self.__id = id
            super().__init__(timeout, total, status_forcelist, backoff_factor)
            self.__handler = RequestHandler(self.timeout, self.total, self.status_forcelist, self.backoff_factor)
            self.__url = urljoin(Hentai._URL, str(self.id))
            self.__api = urljoin(Hentai._API, str(self.id))
            self.__response = self.handler.get(self.api)
            self.__json = self.response.json()
        elif not id and json:
            self.__json = json
            self.__id = Hentai.__get_id(self.json)
            self.__url = Hentai.__get_url(self.json)
            self.__api = Hentai.__get_api(self.json)
        else:
            raise TypeError('Define either id or json argument, but not both or none')

    def __str__(self) -> str:
        return self.title()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ID={str(self.id).zfill(6)})"

    #region operators

    def __gt__(self, other) -> bool:
        return self.id > other.id

    def __ge__(self, other) -> bool:
        return self.id >= other.id

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __le__(self, other) -> bool:
        return self.id <= other.id

    def __lt__(self, other) -> bool:
        return self.id < other.id

    def __ne__(self, other) -> bool:
        return self.id != other.id

    #endregion
    
    @staticmethod
    def __get_id(json: dict) -> int:
        """
        Return the ID of an raw nhentai response object.
        """
        return int(json['id'])

    @staticmethod
    def __get_url(json: dict) -> str:
        """
        Return the URL of an raw nhentai response object.
        """
        return urljoin(Hentai._URL, str(Hentai.__get_id(json)))

    @staticmethod
    def __get_api(json: dict) -> str:
        """
        Return the API access point of an raw nhentai response object.
        """
        return urljoin(Hentai._API, str(Hentai.__get_id(json)))        

    @property
    def id(self):
        """
        Return the ID of this `Hentai` object.
        """
        return self.__id

    @property
    def url(self):
        """
        Return the URL of this `Hentai` object.
        """
        return self.__url

    @property
    def api(self):
        """
        Return the API access point of this `Hentai` object.
        """
        return self.__api

    @property
    def json(self):
        """
        Return the JSON content of this `Hentai` object.
        """
        return self.__json

    @property
    def handler(self):
        """
        Return the `RequestHandler` of this `Hentai` object.
        """
        return self.__handler

    @property
    def response(self):
        """
        Return the GET request response of this `Hentai` object.
        """
        return self.__response

    @property
    def media_id(self) -> int:
        """
        Return the media ID of this `Hentai` object.
        """
        return int(self.json['media_id'])        

    def title(self, format: Format=Format.English) -> str:
        """
        Return the title of this `Hentai` object. The format of the title
        defaults to `English`, which is the verbose counterpart to `Pretty`.
        """
        return self.json['title'].get(format.value)

    @property
    def scanlator(self) -> str:
        """
        Return the scanlator of this `Hentai` object. This information is often 
        not specified by the provider.
        """
        return self.json['scanlator']

    @property
    def cover(self) -> str:
        """
        Return the cover URL of this `Hentai` object.
        """
        cover_ext = Extension.convert(self.json['images']['cover']['t'])
        return f"https://t.nhentai.net/galleries/{self.media_id}/cover{cover_ext}"

    @property
    def thumbnail(self):
        """
        Return the thumbnail URL of this `Hentai` object.
        """
        thumb_ext = Extension.convert(self.json['images']['thumbnail']['t'])
        return f"https://t.nhentai.net/galleries/{self.media_id}/thumb{thumb_ext}"

    @property
    def epos(self) -> int:
        """
        Return the epos of this `Hentai` object.
        """
        return self.json['upload_date']

    @property
    def upload_date(self) -> datetime:
        """
        Return the upload date of this `Hentai` object.
        """
        return datetime.fromtimestamp(self.epos)

    __tag = lambda json, type: [Tag(tag['id'], tag['type'], tag['name'], tag['url'], tag['count']) for tag in json['tags'] if tag['type'] == type]

    @property
    def tag(self) -> List[Tag]:
        """
        Return all tags of type tag of this `Hentai` object.
        """
        return Hentai.__tag(self.json, 'tag')

    @property
    def group(self) -> List[Tag]:
        """
        Return all tags of type group of this `Hentai` object. This tag is sometimes 
        not specified by the provider.
        """
        return Hentai.__tag(self.json, 'group')

    @property
    def parody(self) -> List[Tag]:
        """
        Return all tags of type parody of this `Hentai` object. This tag is sometimes 
        not specified by the provider.
        """
        return Hentai.__tag(self.json, 'parody')

    @property
    def character(self) -> List[Tag]:
        """
        Return all tags of type character of this `Hentai` object. This tag is sometimes 
        not specified by the provider.
        """
        return Hentai.__tag(self.json, 'character')

    @property
    def language(self) -> List[Tag]:
        """
        Return all tags of type language of this `Hentai` object.
        """
        return Hentai.__tag(self.json, 'language')

    @property
    def artist(self) -> List[Tag]:
        """
        Return all tags of type artist of this `Hentai` object.
        """
        return Hentai.__tag(self.json, 'artist')

    @property
    def category(self) -> List[Tag]:
        """
        Return all tags of type category of this `Hentai` object.
        """
        return Hentai.__tag(self.json, 'category')        

    @property
    def num_pages(self) -> int:
        """
        Return the total number of pages of this `Hentai` object.
        """
        return int(self.json['num_pages'])

    @property
    def num_favorites(self) -> int:
        """Return the number of times this `Hentai` object has been favorited."""
        return int(self.json['num_favorites'])

    @property
    def pages(self) -> List[Page]:
        """
        Return a collection of pages detailing URL, file extension, width and 
        height of this `Hentai` object.
        """
        pages = self.json['images']['pages']
        extension = lambda num: Extension.convert(pages[num]['t'])
        image_url = lambda num: f"https://i.nhentai.net/galleries/{self.media_id}/{num}{extension(num - 1)}"
        return [Page(image_url(num + 1), Extension.convert(_['t']), _['w'], _['h']) for num, _ in enumerate(pages)]

    @property
    def image_urls(self) -> List[str]:
        """
        Return all image URLs of this `Hentai` object, excluding cover and thumbnail.
        """
        return [image.url for image in self.pages]

    def download(self, dest: Path=Path.cwd(), delay: float=0, progressbar: bool=False) -> None:
        """
        Download all image URLs of this `Hentai` object to `dest` in a new folder,
        excluding cover and thumbnail. Set a `delay` between each image download 
        in seconds.
        """
        Utils.download([self.id], dest, delay, progressbar)

    def export(self, filename: Path, options: List[Option]=None) -> None:
        """
        Store user-customized data about this `Hentai` object as a JSON file.
        Includes all available options by default.
        """
        Utils.export([self], filename, options)

    @staticmethod
    def exists(id: int) -> bool:
        """
        Check whether or not an ID exists on `nhentai.net`.
        """
        try:
            return RequestHandler().get(urljoin(Hentai._URL, str(id))).ok        
        except HTTPError:
            return False

class Utils(object):
    """
    Hentai Utility Library
    ======================

    This class provides a handful of miscellaneous static methods that extend the 
    functionality of the `Hentai` class.

    Example 1
    ---------
        >>> from hentai import Utils
        >>> print(Utils.get_random_id())
        177013

    Example 2
    ---------
        >>> from hentai import Hentai, Sort, Format, Utils
        >>> lolis = Utils.search_by_query('tag:loli', sort=Sort.PopularWeek)
    """
    @staticmethod
    def get_random_id(handler=RequestHandler()) -> int:
        """
        Return a random ID.
        """
        response = handler.get(urljoin(Hentai.HOME, 'random'))
        return int(urlparse(response.url).path.split('/')[-2])

    @staticmethod
    def get_random_hentai(handler=RequestHandler()) -> Hentai:
        """
        Return a random `Hentai` object.
        """
        return Hentai(Utils.get_random_id(handler))

    @staticmethod
    def download(ids: List[int], dest: Path=Path.cwd(), delay: float=0, progressbar: bool=False) -> None:
        """
        Download all image URLs for multiple IDs to `dest` in separate folders. 
        Set a `delay` between each image download in seconds. Enable `progressbar` 
        for status feedback in terminal applications.
        """
        for id in ids:
            try:
                doujin = Hentai(id)
                dest = dest.joinpath(doujin.title(Format.Pretty))
                dest.mkdir(parents=True, exist_ok=True)
                for page in tqdm(**_progressbar_options(doujin.pages, f"Download #{str(doujin.id).zfill(6)}", 'page', disable=progressbar)):
                    response = doujin.handler.get(page.url, stream=True)
                    with open(dest.joinpath(page.filename), mode='wb') as file_handler:
                        for chunk in response.iter_content(1024):
                            file_handler.write(chunk)
                        time.sleep(delay)
            except HTTPError as error:
                if progressbar:
                    print(f"{Fore.RED}#{str(id).zfill(6)}: {error}")

    @staticmethod
    def browse_homepage(start_page: int, end_page: int, handler=RequestHandler(), progressbar: bool=False) -> List[Hentai]:
        """
        Return a list of `Hentai` objects that are currently featured on the homepage 
        in range of `[start_page, end_page]`. Each page contains as much as 25 results.
        Enable `progressbar` for status feedback in terminal applications.
        """
        if start_page > end_page:
            raise ValueError("Invalid argument passed to function (requires start_page <= end_page).")
        data = []
        for page in tqdm(**_progressbar_options(range(start_page, end_page + 1), 'Browse', 'page', disable=progressbar)):
            response = handler.get(urljoin(Hentai.HOME, 'api/galleries/all'), params={ 'page' : page })
            data.extend([Hentai(json=raw_json) for raw_json in response.json()['result']])
        return data

    @staticmethod
    def get_homepage(page: int=1, handler=RequestHandler()) -> List[Hentai]:
        """
        Return a list of `Hentai` objects that are currently featured on the homepage.
        Each page contains as much as 25 results.
        """
        return Utils.browse_homepage(page, page, handler)

    @staticmethod
    def search_by_query(query: str, page: int=1, sort: Sort=Sort.Popular, handler=RequestHandler()) -> List[Hentai]:
        """
        Return a list of `Hentai` objects on page `page` that match this search 
        `query` sorted by `sort`.
        """
        payload = { 'query' : query, 'page' : page, 'sort' : sort.value }
        response = handler.get(urljoin(Hentai.HOME, 'api/galleries/search'), params=payload).json()
        return [Hentai(json=raw_json) for raw_json in response['result']]

    @staticmethod
    def search_all_by_query(query: str, sort: Sort=Sort.Popular, handler=RequestHandler(), progressbar: bool=False) -> List[Hentai]:
        """
        Return a list of all `Hentai` objects that match this search `query` 
        sorted by `sort`. Enable `progressbar` for status feedback in terminal applications.

        Example
        -------
            >>> from hentai import Utils, Sort, Format
            >>> lolis = Utils.search_all_by_query('tag:loli', sort=Sort.PopularToday)
        """
        data = []
        payload = { 'query' : query, 'page' : 1, 'sort' : sort.value }
        response = handler.get(urljoin(Hentai.HOME, '/api/galleries/search'), params=payload).json()
        for page in tqdm(**_progressbar_options(range(1, int(response['num_pages']) + 1), 'Search', 'page', disable=progressbar)):
            data.extend(Utils.search_by_query(query, page, sort, handler))
        return data

    @staticmethod
    def export(iterable: List[Hentai], filename: Path, options: List[Option]=None) -> None:
        """
        Store user-customized data of `Hentai` objects as a JSON file.
        Includes all available options by default.

        Example
        -------
            >>> from hentai import Utils, Sort, Option
            >>> lolis = Utils.search_by_query('tag:loli', sort=Sort.PopularToday)
            >>> Utils.export(popular_loli, Path('lolis.json'), options=[Option.ID, Option.Title])
        """
        if options is None:
            Utils.export(iterable, filename, options=[opt for opt in Option if opt.value != 'raw'])
        elif Option.Raw in options:
            with open(filename, mode='w', encoding='utf-8') as file_handler:
                json.dump([doujin.json for doujin in iterable], file_handler)
        else:
            content = { 'result' : [] }
            for index, doujin in enumerate(iterable):
                data = {}
                if Option.ID in options:
                    data['id'] = doujin.id
                if Option.Title in options:
                    data['title'] = doujin.title(format=Format.Pretty)
                if Option.Scanlator in options:
                    data['scanlator'] = doujin.scanlator
                if Option.URL in options:
                    data['url'] = doujin.url
                if Option.API in options:
                    data['api'] = doujin.api
                if Option.MediaID in options:
                    data['media_id'] = doujin.media_id
                if Option.UploadDate in options:
                    data['upload_date'] = doujin.json['upload_date']
                if Option.Favorites in options:
                    data['favorites'] = doujin.num_favorites
                if Option.Tag in options:
                    data['tag'] = [tag.name for tag in doujin.tag]
                if Option.Group in options:
                    data['group'] = [tag.name for tag in doujin.group]
                if Option.Parody in options:
                    data['parody'] = [tag.name for tag in doujin.parody]
                if Option.Character in options:
                    data['character'] = [tag.name for tag in doujin.character]
                if Option.Language in options:
                    data['language'] = [tag.name for tag in doujin.language]
                if Option.Artist in options:
                    data['artist'] = [tag.name for tag in doujin.artist]
                if Option.Category in options:
                    data['category'] = [tag.name for tag in doujin.category]
                if Option.Cover in options:
                    data['cover'] = doujin.cover
                if Option.Thumbnail in options:
                    data['thumbnail'] = doujin.thumbnail
                if Option.Images in options:
                    data['images'] = doujin.image_urls
                if Option.PageCount in options:
                    data['pages'] = doujin.num_pages
                content['result'].insert(index, data)
            with open(filename, mode='w', encoding='utf-8') as file_handler:
                json.dump(content, file_handler)
