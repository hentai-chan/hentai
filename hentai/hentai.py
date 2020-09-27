#!/usr/bin/env python

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique
from pathlib import Path
from typing import Iterator, List, Tuple
from urllib.parse import urljoin, urlparse

import requests
from requests import HTTPError, Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from requests.packages.urllib3.util.retry import Retry


try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 7
except AssertionError:
    raise RuntimeError("Hentai requires Python 3.7+!") 


@dataclass
class Tag:
    """
    A data class that bundles related `Tag` properties.
    """
    id: int
    type: str
    name: str
    url: str
    count: int

    @staticmethod
    def get_ids(tags: List[Tag]) -> List[int]:
        """
        Return all IDs of a list of `Tag` objects.
        """
        return [tag.id for tag in tags]

    @staticmethod
    def get_types(tags: List[Tag]) -> List[str]:
        """
        Return all types of a list of `Tag` objects.
        """
        return [tag.type for tag in tags]

    @staticmethod
    def get_names(tags: List[Tag]) -> List[str]:
        """
        Return all names of a list of `Tag` objects.
        """
        return [tag.name for tag in tags]

    @staticmethod
    def get_urls(tags: List[Tag]) -> List[str]:
        """
        Return all URLs of a list of `Tag` objects.
        """
        return [tag.url for tag in tags]

    @staticmethod
    def get_counts(tags: List[Tag]) -> List[int]:
        """
        Return all counts (of occurrences on `nhentai.net`) of a list of `Tag` objects.
        """
        return [tag.count for tag in tags]


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
        Return the file name for this `Page`.
        """
        num = Path(urlparse(self.url).path).name
        return Path(num).with_suffix(self.ext)


@unique
class Sort(Enum):
    """
    Exposed endpoints used to sort queries. Defaults to `Popular`.
    """
    PopularYear = 'popular-year'
    PopularMonth = 'popular-month'
    PopularWeek = 'popular-week'
    PopularToday = 'popular-today'
    Popular = 'popular'
    Date = 'date'


@unique
class Format(Enum):
    """
    Title format. In some instances, `Format.Japanese` or `Format.Pretty` return
    `None`.
    """
    English = 'english'
    Japanese = 'japanese'
    Pretty = 'pretty'


@unique
class Extension(Enum):
    """
    Extensions used by `nhentai` images.
    """
    JPG = 'j'
    PNG = 'p'
    GIF = 'g'

    @classmethod
    def convert(cls, key: str) -> str:
        """
        Convert Extension enum to its string representation.

        Example:
        ```python
        >>> from hentai import Extension
        >>> Extension.convert('j')
        .jpg
        ```
        """
        return f".{cls(key).name.lower()}"


class RequestHandler(object):
    """
    Defines a synchronous request handler class.
    """
    _timeout = (3.05, 1)
    _total = 5
    _status_forcelist = [413, 429, 500, 502, 503, 504]
    # sleep between fails = backoff_factor * (2 ** (total - 1))
    _backoff_factor = 1

    def __init__(self, 
                 timeout: Tuple[float, float]=_timeout, 
                 total: int=_total, 
                 status_forcelist: List[int]=_status_forcelist, 
                 backoff_factor: int=_backoff_factor):
        """
        Instantiates a new session and uses sane default params that can be modified
        later on to change the way `Hentai` object make their requests.
        """
        self.timeout = timeout
        self.total = total        
        self.status_forcelist = status_forcelist
        self.backoff_factor = backoff_factor

    @property
    def retry_strategy(self) -> Retry:
        """
        Return a retry strategy for this session. 
        """
        return Retry(self.total, self.status_forcelist, self.backoff_factor)

    @property
    def session(self) -> Session:
        """
        Return this session object used for making GET and POST requests.
        """
        assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries = self.retry_strategy))
        session.hooks['response'] = [assert_status_hook]
        session.headers.update({
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51"
        })
        return session
    
    def call_api(self, url: str, params: dict={}, **kwargs) -> Response:
        """
        Returns the GET request encoded in `utf-8`.
        """
        response = self.session.get(url, timeout = self.timeout, params = params)
        response.encoding = 'utf-8'
        return response


class Hentai(RequestHandler):
    """
    Implements a wrapper class around `nhentai`'s RESTful API that inherits from
    `RequestHandler`.
    """
    HOME = "https://nhentai.net/" 
    _URL = urljoin(HOME, '/g/')
    _API = urljoin(HOME, '/api/gallery/')

    def __init__(self, 
                 id: int, 
                 timeout: Tuple[float, float]=RequestHandler._timeout, 
                 total: int=RequestHandler._total, 
                 status_forcelist: List[int]=RequestHandler._status_forcelist, 
                 backoff_factor: int=RequestHandler._backoff_factor):
        """
        Start a request session and parse meta data from `nhentai.net` for this `id`.

        Basic Usage:
        ```python
        >>> from hentai import Hentai
        >>> doujin = Hentai(177013)
        >>> print(doujin)
        [ShindoLA] METAMORPHOSIS (Complete) [English]
        ```
        """
        self.id = id
        super().__init__(timeout, total, status_forcelist, backoff_factor)
        self.handler = RequestHandler(self.timeout, self.total, self.status_forcelist, self.backoff_factor)
        self.url = urljoin(Hentai._URL, str(self.id))
        self.api = urljoin(Hentai._API, str(self.id))
        self.response = self.handler.call_api(self.api)
        self.json = self.response.json()

    def __str__(self) -> str:
        return self.title()

    def __repr__(self) -> str:
        return f"ID({self.id})"
    
    @staticmethod
    def get_id(json: dict) -> int:
        """
        Return the id of an nhentai response object.
        """
        return int(json['id'])

    @staticmethod
    def get_media_id(json: dict) -> int:
        """
        Return the media id of an nhentai response object.
        """
        return int(json['media_id'])

    @property
    def media_id(self) -> int:
        """
        Return the media id of this `Hentai` object.
        """
        return Hentai.get_media_id(self.json)   

    @staticmethod
    def get_title(json: dict, format: Format=Format.English) -> str:
        """
        Return the title of an nhentai response object.
        """
        return json['title'].get(format.value)

    def title(self, format: Format=Format.English) -> str:
        """
        Return the title of this `Hentai` object.
        """
        return Hentai.get_title(self.json, format)

    @staticmethod
    def get_cover(json: dict) -> str:
        """
        Return the cover URL of an nhentai response object.
        """
        cover_ext = Extension.convert(json['images']['cover']['t'])
        return f"https://t.nhentai.net/galleries/{Hentai.get_media_id(json)}/cover{cover_ext}"

    @property
    def cover(self) -> str:
        """
        Return the cover URL of this `Hentai` object.
        """
        return Hentai.get_cover(self.json)

    @staticmethod
    def get_thumbnail(json: dict) -> str:
        """
        Return the thumbnail URL of an nhentai response object.
        """
        thumb_ext = Extension.convert(json['images']['thumbnail']['t'])
        return f"https://t.nhentai.net/galleries/{Hentai.get_media_id(json)}/thumb{thumb_ext}"

    @property
    def thumbnail(self):
        """
        Return the thumbnail URL of this `Hentai` object.
        """
        return Hentai.get_thumbnail(self.json)

    @staticmethod
    def get_upload_date(json: dict) -> datetime:
        """
        Return the upload date of an nhentai response object.
        """
        return datetime.fromtimestamp(json['upload_date'])

    @property
    def upload_date(self) -> datetime:
        """
        Return the upload date of this `Hentai` object.
        """
        return Hentai.get_upload_date(self.json)

    _tag = lambda json, type: [Tag(tag['id'], tag['type'], tag['name'], tag['url'], tag['count']) for tag in json['tags'] if tag['type'] == type]
    
    @staticmethod
    def get_tag(json: dict) -> List[Tag]:
        """
        Return all tags of type tag of an nhentai response object.
        """
        return Hentai._tag(json, 'tag')

    @property
    def tag(self) -> List[Tag]:
        """
        Return all tags of type tag of this `Hentai` object.
        """
        return Hentai.get_tag(self.json)

    @staticmethod
    def get_language(json: dict) -> List[Tag]:
        """
        Return all tags of type language of an nhentai response object.
        """
        return Hentai._tag(json, 'language')

    @property
    def language(self) -> List[Tag]:
        """
        Return all tags of type language of this `Hentai` object.
        """
        return Hentai.get_language(self.json)

    @staticmethod
    def get_artist(json: dict) -> List[Tag]:
        """
        Return all tags of type artist of an nhentai response object.
        """
        return Hentai._tag(json, 'artist')

    @property
    def artist(self) -> List[Tag]:
        """
        Return all tags of type artist of this `Hentai` object.
        """
        return Hentai.get_artist(self.json)

    @staticmethod
    def get_category(json: dict) -> List[Tag]:
        """
        Return all tags of type category of this `Hentai` object.
        """
        return Hentai._tag(json, 'category')

    @property
    def category(self) -> List[Tag]:
        """
        Return all tags of type category of this `Hentai` object.
        """
        return Hentai.get_category(self.json)

    @staticmethod
    def get_num_pages(json: dict) -> int:
        """
        Return the total number of pages of an nhentai response object.
        """
        return int(json['num_pages'])

    @property
    def num_pages(self) -> int:
        """
        Return the total number of pages of this `Hentai` object.
        """
        return Hentai.get_num_pages(self.json)

    @staticmethod
    def get_num_favorites(json: dict) -> int:
        """
        Return the number of times the nhentai response object has been favorited.
        """
        return int(json['num_favorites'])

    @property
    def num_favorites(self) -> int:
        """Return the number of times this `Hentai` object has been favorited."""
        return Hentai.get_num_favorites(self.json)

    @staticmethod
    def get_pages(json: dict) -> List[Page]:
        """
        Return a collection of pages detailing URL, file extension, width an 
        height of an nhentai response object.
        """
        pages = json['images']['pages']
        extension = lambda num: Extension.convert(pages[num]['t'])
        image_url = lambda num: f"https://i.nhentai.net/galleries/{Hentai.get_media_id(json)}/{num}{extension(num - 1)}"
        return [Page(image_url(num + 1), Extension.convert(_['t']), _['w'], _['h']) for num, _ in enumerate(pages)]

    @property
    def pages(self) -> List[Page]:
        """
        Return a collection of pages detailing URL, file extension, width an 
        height of this `Hentai` object.
        """
        return Hentai.get_pages(self.json)

    @staticmethod
    def get_image_urls(json: dict) -> List[str]:
        """
        Return all image URLs of an nhentai response object.
        """
        return [image.url for image in Hentai.get_pages(json)]

    @property
    def image_urls(self) -> List[str]:
        """
        Return all image URLs of this `Hentai` object.
        """
        return Hentai.get_image_urls(self.json)

    def download(self, dest: Path=Path(os.path.expanduser("~\\Desktop"))) -> None:
        """
        Download all image URLs of this `Hentai` object to `dest` in a new folder.
        """
        dest = dest.joinpath(self.title(Format.Pretty))
        dest.mkdir(parents=True, exist_ok=True)
        for image_url in self.image_urls:
            response = self.handler.call_api(image_url, stream=True)
            filename = dest.joinpath(dest.joinpath(image_url).name)
            with open(filename, mode='wb') as file_handler:
                file_handler.write(response.content)

    @staticmethod
    def download_queue(ids: List[int], dest=os.path.expanduser("~\\Desktop")) -> None:
        """
        Download all image URLs for multiple magic numbers to `dest` in newly 
        created folders.
        """
        [Hentai(id).download(dest) for id in ids]

    @staticmethod
    def exists(id: int) -> bool:
        """
        Check whether the magic number exists on `nhentai.net`.
        """
        try:
            return RequestHandler().call_api(urljoin(Hentai._URL, str(id))).ok        
        except HTTPError:
            return False

    @staticmethod
    def get_random_id(handler=RequestHandler()) -> int:
        """
        Return a valid random magic number.
        """
        response = handler.session.get(urljoin(Hentai.HOME, 'random'))
        return int(urlparse(response.url).path[3:-1])

    @staticmethod
    def browse_homepage(start_page: int, end_page: int, handler=RequestHandler()) -> Iterator[List[dict]]:
        """
        Return an iterated list of nhentai response objects that are currently 
        featured on the homepage in range of `[start_page, end_page]`.
        """
        for page in range(start_page, end_page + 1):
            payload = { 'page' : page }
            response = handler.call_api(urljoin(Hentai.HOME, 'api/galleries/all'), params=payload).json()
            yield response['result']

    @staticmethod
    def get_homepage(page: int=1, handler=RequestHandler()) -> List[dict]:
        """
        Return an iterated list of nhentai response objects that are currently 
        featured on the homepage.
        """
        return next(Hentai.browse_homepage(page, page, handler))

    @staticmethod
    def search_by_query(query: str, page: int=1, sort: Sort=Sort.Popular, handler=RequestHandler()) -> List[dict]:
        """
        Return a list of nhentai response objects on page=`page` matching this 
        search `query` sorted by `sort`.
        """
        payload = { 'query' : query, 'page' : page, 'sort' : sort.value }
        response = handler.call_api(urljoin(Hentai.HOME, '/api/galleries/search'), params=payload).json()
        return response['result']

    @staticmethod
    def search_all_by_query(query: str, sort: Sort=Sort.Popular, handler=RequestHandler()) -> Iterator[List[dict]]:
        """
        Return an iterated list of all nhentai response objects matching this 
        search `query` sorted by `sort`.
        """
        payload = { 'query' : query, 'page' : 1 }
        response = handler.call_api(urljoin(Hentai.HOME, '/api/galleries/search'), params=payload).json()
        for page in range(1, int(response['num_pages']) + 1):
            yield Hentai.search_by_query(query, page, sort, handler)
