#!/usr/bin/env python

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique
from typing import List, Tuple
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


@dataclass
class Tag:
    id: int
    type: str
    name: str
    url: str
    count: int

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
        return cls(key).name.lower()

class RequestHandler(object):
    TIMEOUT = (3.05, 1)
    # sleep time in-between failures = backoff_factor * (2 ** (total - 1))
    retry_strategy = Retry(
        total = 5, 
        status_forcelist = [413, 429, 500, 502, 503, 504], 
        backoff_factor = 1
    )

    assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries = retry_strategy))
    session.hooks['response'] = [assert_status_hook]
    session.headers.update({
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51"
    })

    @staticmethod
    def call_api(url: str, timeout: Tuple[float, float] = TIMEOUT, params: dict = {}) -> dict:
        response = RequestHandler.session.get(url, timeout = timeout, params = params)
        response.encoding = 'utf-8'
        return response.json()

class Hentai(RequestHandler):
    HOME = "https://nhentai.net/" 
    _URL = urljoin(HOME, '/g/')
    _API = urljoin(HOME, '/api/gallery/')

    def __init__(self, id: int, timeout: Tuple[float, float] = RequestHandler.TIMEOUT):
        self.id = id
        self.timeout = timeout
        self.url = urljoin(Hentai._URL, str(self.id))
        self.api = urljoin(Hentai._API, str(self.id))
        self.json = Hentai.call_api(self.api, self.timeout)
    
    @property
    def media_id(self) -> int:
        return self.json['media_id']

    def title(self, format: Format = Format.English) -> str:
        return self.json['title'].get(format.value)

    @property
    def cover(self) -> str:
        cover_ext = Extension.convert(self.json['images']['cover']['t'])
        return f"https://t.nhentai.net/galleries/{self.media_id}/cover.{cover_ext}"

    @property
    def thumbnail(self) -> str:
        thumb_ext = Extension.convert(self.json['images']['thumbnail']['t'])
        return f"https://t.nhentai.net/galleries/{self.media_id}/thumb.{thumb_ext}"

    @property
    def upload_date(self) -> datetime:
        return datetime.fromtimestamp(self.json['upload_date'])

    _tag = lambda self, type: [Tag(tag['id'], tag['type'], tag['name'], tag['url'], tag['count']) for tag in self.json['tags'] if tag['type'] == type]
    
    @property
    def tags(self) -> List[Tag]:
        return Hentai._tag(self, 'tag')

    @property
    def language(self) -> List[Tag]:
        return Hentai._tag(self, 'language')

    @property
    def artist(self) -> List[Tag]:
        return Hentai._tag(self, 'artist')

    @property
    def category(self) -> List[Tag]:
        return Hentai._tag(self, 'category')

    @property
    def num_pages(self) -> int:
        return self.json['num_pages']

    @property
    def num_favorites(self) -> int:
        return self.json['num_favorites']

    @property
    def image_urls(self) -> List[str]:
        extension = lambda num: Extension.convert(self.json['images']['pages'][num]['t'])
        image_url = lambda num: f"https://i.nhentai.net/galleries/{self.media_id}/{num}.{extension(num-1)}"
        return [image_url(num) for num in range(1, self.num_pages + 1)] 

    @staticmethod
    def get_random_id() -> int:
        response = Hentai.session.get(urljoin(Hentai.HOME, 'random'))
        return int(urlparse(response.url).path[3:-1])

    @staticmethod
    def get_homepage(page: int = 1, timeout: Tuple[float, float] = RequestHandler.TIMEOUT) -> List[dict]:
        response = Hentai.call_api(urljoin(Hentai.HOME, 'api/galleries/all'), timeout, params = { 'page' : page })
        return response['result']

    @staticmethod
    def search_by_query(query: str, timeout: Tuple[float, float] = RequestHandler.TIMEOUT) -> List[dict]:
        response = Hentai.call_api(urljoin(Hentai.HOME, '/api/galleries/search'), timeout, params = { 'query' : query })
        return response['result']
