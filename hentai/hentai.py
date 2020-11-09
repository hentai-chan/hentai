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

import csv
import json
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, unique
from importlib.resources import path as resource_path
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urljoin, urlparse
from urllib.request import getproxies

import requests
from faker import Faker
from requests import HTTPError, Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry

try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 7
except AssertionError:
    raise RuntimeError("Hentai requires Python 3.7+!") 


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
        
        ### Example:
        ```python
        >>> from hentai import Hentai, Tag
        >>> doujin = Hentai(177013)
        >>> Tag.get_ids(doujin.artist)
        3981
        ```
        """
        ids = [tag.id for tag in tags]
        return ids[0] if len(ids) == 1 else ids

    @staticmethod
    def get_types(tags: List[Tag]) -> str or List[str]:
        """
        Return a list of types corresponding to the passed Tag objects.

        ### Example:
        ```python
        >>> from hentai import Hentai, Tag
        >>> doujin = Hentai(177013)
        >>> Tag.get_types(doujin.artist)
        'artist'
        ```
        """
        types = [tag.type for tag in tags]
        return types[0] if len(types) == 1 else types 

    @staticmethod
    def get_names(tags: List[Tag]) -> str or List[str]:
        """
        Return a list of capitalized names corresponding to the passed Tag objects.

        ### Example:
        ```python
        >>> from hentai import Hentai, Tag
        >>> doujin = Hentai(177013)
        >>> Tag.get_names(doujin.artist)
        'Shindol'
        ```
        """
        capitalize_all = lambda sequence: ' '.join([word.capitalize() for word in sequence.split(' ')])
        artists = [capitalize_all(tag.name) for tag in tags]
        return artists[0] if len(artists) == 1 else artists

    @staticmethod
    def get_urls(tags: List[Tag]) -> str or List[str]:
        """
        Return a list of URLs corresponding to the passed Tag objects.
        
        ### Example:
        ```python
        >>> from hentai import Hentai, Tag
        >>> doujin = Hentai(177013)
        >>> Tag.get_urls(doujin.artist)
        '/artist/shindol/'
        ```
        """
        urls = [tag.url for tag in tags]
        return urls[0] if len(urls) == 1 else urls

    @staticmethod
    def get_counts(tags: List[Tag]) -> int or List[int]:
        """
        Return a list of counts (of occurrences) corresponding to the passed Tag objects.

        ### Example:
        ```python
        >>> from hentai import Hentai, Tag
        >>> doujin = Hentai(177013)
        >>> Tag.get_counts(doujin.artist)
        279
        ```
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

        ### Example:
        ```python
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
    Exposed endpoints used to sort queries. Defaults to `Popular`.
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
    Defines export options for the `Hentai` and `Utils` class.
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

        ### Example:
        ```python
        >>> from hentai import Extension
        >>> Extension.convert('j')
        '.jpg'
        ```
        """
        return f".{cls(key).name.lower()}"


class RequestHandler(object):
    """
    Defines a synchronous request handler class that provides methods and 
    properties for working with REST APIs.
    """
    _timeout = (3.05, 1)
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
        session.mount("https://", HTTPAdapter(max_retries = self.retry_strategy))
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
        response = self.session.get(url, timeout = self.timeout, params = params, proxies=getproxies(), **kwargs)
        response.encoding = 'utf-8'
        return response


class Hentai(RequestHandler):
    """
    # Python Hentai API Wrapper
    Implements a wrapper class around `nhentai`'s RESTful API that inherits from
    `RequestHandler`. Note that the content of this module is generally considered 
    NSFW.
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

        ## Basic Usage:
        ```python
        >>> from hentai import Hentai
        >>> doujin = Hentai(177013)
        >>> print(doujin)
        '[ShindoLA] METAMORPHOSIS (Complete) [English]'
        ```
        """
        if id and not json:
            self.id = id
            super().__init__(timeout, total, status_forcelist, backoff_factor)
            self.handler = RequestHandler(self.timeout, self.total, self.status_forcelist, self.backoff_factor)
            self.url = urljoin(Hentai._URL, str(self.id))
            self.api = urljoin(Hentai._API, str(self.id))
            self.response = self.handler.get(self.api)
            self.json = self.response.json()
        elif not id and json:
            self.json = json
            self.id = Hentai.__get_id(self.json)
            self.url = Hentai.__get_url(self.json)
            self.api = Hentai.__get_api(self.json)
        else:
            raise TypeError('Define either id or json argument, but not both or none')

    def __str__(self) -> str:
        return self.title()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ID={self.id})"
    
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
    def upload_date(self) -> datetime:
        """
        Return the upload date of this `Hentai` object.
        """
        return datetime.fromtimestamp(self.json['upload_date'])

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

    def download(self, dest: Path=Path.cwd(), delay: float=0) -> None:
        """
        Download all image URLs of this `Hentai` object to `dest` in a new folder,
        excluding cover and thumbnail. Set a `delay` between each image download 
        in seconds.
        """
        dest = dest.joinpath(self.title(Format.Pretty))
        dest.mkdir(parents=True, exist_ok=True)
        for image_url in self.image_urls:
            response = self.handler.get(image_url, stream=True)
            filename = dest.joinpath(dest.joinpath(image_url).name)
            with open(filename, mode='wb') as file_handler:
                for chunk in response.iter_content(1024):
                    file_handler.write(chunk)
                time.sleep(delay)

    def export(self, filename: Path, options: List[Option]=None) -> None:
        """
        Store user-customized data about this `Hentai` object as a JSON file.
        Includes all available options by default.
        """
        tmp = []
        tmp.append(self.json)
        Utils.export(tmp, filename, options)

    @staticmethod
    def exists(id: int, make_request: bool=True) -> bool:
        """
        Check whether or not the ID exists on `nhentai.net`. Set `make_request` 
        to `False` to search for validated IDs in an internal file.
        """
        if make_request:
            try:
                return RequestHandler().get(urljoin(Hentai._URL, str(id))).ok        
            except HTTPError:
                return False
        else:
            with resource_path('hentai.data', 'ids.csv') as data_path:
                with open(data_path, mode='r', encoding='utf-8') as file_handler:
                    reader = csv.reader(file_handler)
                    for row in reader:
                        if id == int(row[0]):
                            return True
            return False


class Utils(object):
    """
    # Hentai Utility Library

    This class provides a handful of miscellaneous static methods that extend the 
    functionality of the `Hentai` class.

    ### Example 1
    ```python
    >>> from hentai import Utils
    >>> print(Utils.get_random_id())
    177013
    ```

    ### Example 2
    ```python
    from hentai import Hentai, Sort, Format, Utils
    >>> # fetches 25 responses per query
    >>> for doujin in Utils.search_by_query('tag:loli', sort=Sort.PopularWeek):
    ...   print(doujin.title(Format.Pretty))
    ```
    """
    @staticmethod
    def get_random_id(make_request: bool=True, handler=RequestHandler()) -> int:
        """
        Return a random ID. Set `make_request` to `False` to randomly select an 
        already validated ID in an internal file.
        """
        if make_request:
            response = handler.session.get(urljoin(Hentai.HOME, 'random'))
            return int(urlparse(response.url).path[3:-1])
        else:
            with resource_path('hentai.data', 'ids.csv') as data_path:
                with open(data_path, mode='r', encoding='utf-8') as file_handler:
                    reader = csv.reader(file_handler)
                    return random.choice([int(row[0]) for row in reader])

    @staticmethod
    def get_random_hentai(make_request: bool=True, handler=RequestHandler()) -> Hentai:
        """
        Return a random `Hentai` object. Set `make_request` to `False` to randomly 
        select an already validated ID in an internal file.
        """
        return Hentai(Utils.get_random_id(make_request, handler))

    @staticmethod
    def download(ids: List[int], dest: Path=Path.cwd(), delay: float=0) -> None:
        """
        Download all image URLs for multiple magic numbers to `dest` in newly 
        created folders. Set a `delay` between each image download in seconds.
        """
        [Hentai(id).download(dest, delay) for id in ids]

    @staticmethod
    def browse_homepage(start_page: int, end_page: int, handler=RequestHandler()) -> List[Hentai]:
        """
        Return a list of `Hentai` objects that are currently featured on the homepage 
        in range of `[start_page, end_page]`. Each page contains as much as 25 results.
        """
        if start_page > end_page:
            raise ValueError("Invalid argument passed to function (requires start_page <= end_page).")
        data = []
        for page in range(start_page, end_page + 1):
            payload = { 'page' : page }
            response = handler.get(urljoin(Hentai.HOME, 'api/galleries/all'), params=payload).json()
            data.extend([Hentai(json=raw_json) for raw_json in response['result']])
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
    def search_all_by_query(query: str, sort: Sort=Sort.Popular, handler=RequestHandler()) -> List[Hentai]:
        """
        Return a list of all `Hentai` objects that match this search `query` 
        sorted by `sort`.

        ### Example:
        ```python
        >>> from hentai import Utils, Sort, Format
        >>> # fetches all responses that match this query
        >>> for doujin in Utils.search_all_by_query(query="tag:3d", sort=Sort.PopularWeek):
        ...   print(doujin)
        A Rebel's Journey:  Chang'e
        COMIC KURiBERON 2019-06 Vol. 80
        Mixed Wrestling Japan 2019
        ```
        """
        data = []
        payload = { 'query' : query, 'page' : 1, 'sort' : sort.value }
        response = handler.get(urljoin(Hentai.HOME, '/api/galleries/search'), params=payload).json()
        for page in range(1, int(response['num_pages']) + 1):
            data.extend(Utils.search_by_query(query, page, sort, handler))
        return data

    @staticmethod
    def export(iterable: List[Hentai], filename: Path, options: List[Option]=None) -> None:
        """
        Store user-customized data of `Hentai` objects as a JSON file.
        Includes all available options by default.

        ### Example:
        ```python
        >>> from hentai import Utils, Sort, Option
        >>> popular_loli = Utils.search_by_query('tag:loli', sort=Sort.PopularWeek)
        >>> # filter file content using options
        >>> custom = [Option.ID, Option.Title, Option.UploadDate]
        >>> Utils.export(popular_loli, Path('popular_loli.json'), options=custom)
        ```
        """
        if options is None:
            Utils.export(iterable, filename, options=[opt for opt in Option if opt.value != 'raw'])
        elif Option.Raw in options:
            with open(filename, mode='w', encoding='utf-8') as file_handler:
                json.dump(iterable, file_handler)
        else:
            content = { 'result' : [] }
            for index, raw_json in enumerate(iterable):
                data = {}
                doujin = Hentai(json=raw_json)
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
                    epos = doujin.upload_date.replace(tzinfo=timezone.utc).timestamp()
                    data['upload_date'] = round(epos)
                if Option.Favorites in options:
                    data['favorites'] = doujin.num_favorites
                if Option.Tag in options:
                    data['tag'] = Tag.get_names(doujin.tag)
                if Option.Group in options:
                    data['group'] = Tag.get_names(doujin.group)
                if Option.Parody in options:
                    data['parody'] = Tag.get_names(doujin.parody)
                if Option.Character in options:
                    data['character'] = Tag.get_names(doujin.character)
                if Option.Language in options:
                    data['language'] = Tag.get_names(doujin.language)
                if Option.Artist in options:
                    data['artist'] = Tag.get_names(doujin.artist)
                if Option.Category in options:
                    data['category'] = Tag.get_names(doujin.category)
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
