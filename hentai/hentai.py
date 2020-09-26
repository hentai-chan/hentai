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
    id: int
    type: str
    name: str
    url: str
    count: int

    @staticmethod
    def get_ids(tags: List[Tag]) -> List[int]:
        return [tag.id for tag in tags]

    @staticmethod
    def get_types(tags: List[Tag]) -> List[str]:
        return [tag.type for tag in tags]

    @staticmethod
    def get_names(tags: List[Tag]) -> List[str]:
        return [tag.name for tag in tags]

    @staticmethod
    def get_urls(tags: List[Tag]) -> List[str]:
        return [tag.url for tag in tags]

    @staticmethod
    def get_counts(tags: List[Tag]) -> List[int]:
        return [tag.count for tag in tags]


@dataclass
class Page:
    url: str
    ext: str
    width: int
    height: int

    @property
    def filename(self) -> Path:
        num = Path(urlparse(self.url).path).name
        return Path(num).with_suffix(self.ext)


@unique
class Sort(Enum):
    PopularYear = 'popular-year'
    PopularMonth = 'popular-month'
    PopularWeek = 'popular-week'
    PopularToday = 'popular-today'
    Popular = 'popular'
    Date = 'date'


@unique
class Format(Enum):
    English = 'english'
    Japanese = 'japanese'
    Pretty = 'pretty'


@unique
class Extension(Enum):
    JPG = 'j'
    PNG = 'p'
    GIF = 'g'

    @classmethod
    def convert(cls, key: str) -> str:
        return f".{cls(key).name.lower()}"


class RequestHandler(object):
    _timeout = (3.05, 1)
    _total = 5
    _status_forcelist = [413, 429, 500, 502, 503, 504]
    _backoff_factor = 1

    def __init__(self, 
                 timeout: Tuple[float, float]=_timeout, 
                 total: int=_total, 
                 status_forcelist: List[int]=_status_forcelist, 
                 backoff_factor: int=_backoff_factor):
        self.timeout = timeout
        self.total = total        
        self.status_forcelist = status_forcelist
        self.backoff_factor = backoff_factor

    @property
    def retry_strategy(self) -> Retry:
        return Retry(self.total, self.status_forcelist, self.backoff_factor)

    @property
    def session(self) -> Session:
        assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries = self.retry_strategy))
        session.hooks['response'] = [assert_status_hook]
        session.headers.update({
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51"
        })
        return session
    
    def call_api(self, url: str, params: dict={}, **kwargs) -> Response:
        response = self.session.get(url, timeout = self.timeout, params = params)
        response.encoding = 'utf-8'
        return response


class Hentai(RequestHandler):
    HOME = "https://nhentai.net/" 
    _URL = urljoin(HOME, '/g/')
    _API = urljoin(HOME, '/api/gallery/')

    def __init__(self, 
                 id: int, 
                 timeout: Tuple[float, float]=RequestHandler._timeout, 
                 total: int=RequestHandler._total, 
                 status_forcelist: List[int]=RequestHandler._status_forcelist, 
                 backoff_factor: int=RequestHandler._backoff_factor):
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
        return int(json['id'])

    @staticmethod
    def get_media_id(json: dict) -> int:
        return int(json['media_id'])

    @property
    def media_id(self) -> int:
        return Hentai.get_media_id(self.json)   

    @staticmethod
    def get_title(json: dict, format: Format=Format.English) -> str:
        return json['title'].get(format.value)

    def title(self, format: Format=Format.English) -> str:
        return Hentai.get_title(self.json, format)

    @staticmethod
    def get_cover(json: dict) -> str:
        cover_ext = Extension.convert(json['images']['cover']['t'])
        return f"https://t.nhentai.net/galleries/{Hentai.get_media_id(json)}/cover{cover_ext}"

    @property
    def cover(self) -> str:
        return Hentai.get_cover(self.json)

    @staticmethod
    def get_thumbnail(json: dict) -> str:
        thumb_ext = Extension.convert(json['images']['thumbnail']['t'])
        return f"https://t.nhentai.net/galleries/{Hentai.get_media_id(json)}/thumb{thumb_ext}"

    @property
    def thumbnail(self):
        return Hentai.get_thumbnail(self.json)

    @staticmethod
    def get_upload_date(json: dict) -> datetime:
        return datetime.fromtimestamp(json['upload_date'])

    @property
    def upload_date(self) -> datetime:
        return Hentai.get_upload_date(self.json)

    _tag = lambda json, type: [Tag(tag['id'], tag['type'], tag['name'], tag['url'], tag['count']) for tag in json['tags'] if tag['type'] == type]
    
    @staticmethod
    def get_tag(json: dict) -> List[Tag]:
        return Hentai._tag(json, 'tag')

    @property
    def tag(self) -> List[Tag]:
        return Hentai.get_tag(self.json)

    @staticmethod
    def get_language(json: dict) -> List[Tag]:
        return Hentai._tag(json, 'language')

    @property
    def language(self) -> List[Tag]:
        return Hentai.get_language(self.json)

    @staticmethod
    def get_artist(json: dict) -> List[Tag]:
        return Hentai._tag(json, 'artist')

    @property
    def artist(self) -> List[Tag]:
        return Hentai.get_artist(self.json)

    @staticmethod
    def get_category(json: dict) -> List[Tag]:
        return Hentai._tag(json, 'category')

    @property
    def category(self) -> List[Tag]:
        return Hentai.get_category(self.json)

    @staticmethod
    def get_num_pages(json: dict) -> int:
        return int(json['num_pages'])

    @property
    def num_pages(self) -> int:
        return Hentai.get_num_pages(self.json)

    @staticmethod
    def get_num_favorites(json: dict) -> int:
        return int(json['num_favorites'])

    @property
    def num_favorites(self) -> int:
        return Hentai.get_num_favorites(self.json)

    @staticmethod
    def get_pages(json: dict) -> List[Page]:
        pages = json['images']['pages']
        extension = lambda num: Extension.convert(pages[num]['t'])
        image_url = lambda num: f"https://i.nhentai.net/galleries/{Hentai.get_media_id(json)}/{num}{extension(num - 1)}"
        return [Page(image_url(num + 1), Extension.convert(_['t']), _['w'], _['h']) for num, _ in enumerate(pages)]

    @property
    def pages(self) -> List[Page]:
        return Hentai.get_pages(self.json)

    @staticmethod
    def get_image_urls(json: dict) -> List[str]:
        return [image.url for image in Hentai.get_pages(json)]

    @property
    def image_urls(self) -> List[str]:
        return Hentai.get_image_urls(self.json)

    def download(self, dest: Path=Path(os.path.expanduser("~\\Desktop"))) -> None:
        dest = dest.joinpath(self.title(Format.Pretty))
        dest.mkdir(parents=True, exist_ok=True)
        for image_url in self.image_urls:
            response = self.handler.call_api(image_url, stream=True)
            filename = dest.joinpath(dest.joinpath(image_url).name)
            with open(filename, mode='wb') as file_handler:
                file_handler.write(response.content)

    @staticmethod
    def download_queue(ids: List[int], dest=os.path.expanduser("~\\Desktop")) -> None:
        [Hentai(id).download(dest) for id in ids]

    @staticmethod
    def exists(id: int) -> bool:
        try:
            return RequestHandler().call_api(urljoin(Hentai._URL, str(id))).ok        
        except HTTPError:
            return False

    @staticmethod
    def get_random_id(handler=RequestHandler()) -> int:
        response = handler.session.get(urljoin(Hentai.HOME, 'random'))
        return int(urlparse(response.url).path[3:-1])

    @staticmethod
    def browse_homepage(start_page: int, end_page: int, handler=RequestHandler()) -> Iterator[List[dict]]:
        for page in range(start_page, end_page + 1):
            payload = { 'page' : page }
            response = handler.call_api(urljoin(Hentai.HOME, 'api/galleries/all'), params=payload).json()
            yield response['result']

    @staticmethod
    def get_homepage(page: int=1, handler=RequestHandler()) -> List[dict]:
        return next(Hentai.browse_homepage(page, page, handler))

    @staticmethod
    def search_by_query(query: str, page: int=1, sort: Sort=Sort.Popular, handler=RequestHandler()) -> List[dict]:
        payload = { 'query' : query, 'page' : page, 'sort' : sort.value }
        response = handler.call_api(urljoin(Hentai.HOME, '/api/galleries/search'), params=payload).json()
        return response['result']

    @staticmethod
    def search_all_by_query(query: str, sort: Sort=Sort.Popular, handler=RequestHandler()) -> Iterator[List[dict]]:
        payload = { 'query' : query, 'page' : 1 }
        response = handler.call_api(urljoin(Hentai.HOME, '/api/galleries/search'), params=payload).json()
        for page in range(1, int(response['num_pages']) + 1):
            yield Hentai.search_by_query(query, page, sort, handler)
