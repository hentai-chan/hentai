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

import errno
import functools
import html
import json
import logging
import os
import platform
import re
import shutil
import sqlite3
import sys
import tarfile
import time
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timezone
from enum import Enum, unique
from importlib.resources import path as resource_path
from pathlib import Path
from typing import List, Set, Tuple
from urllib.parse import urljoin, urlparse
from urllib.request import getproxies
from zipfile import ZipFile, ZIP_DEFLATED

import requests
from requests import HTTPError, Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from tqdm import tqdm
from urllib3.util.retry import Retry

__version__ = "3.2.9"
package_name = "hentai"
python_major = "3"
python_minor = "7"

try:
    assert sys.version_info >= (int(python_major), int(python_minor))
except AssertionError:
    raise RuntimeError(f"\033[31m{package_name!r} requires Python {python_major}.{python_minor}+ (You have Python {sys.version})\033[0m")

#region logging

def get_config_dir() -> Path:
    """
    Return a platform-specific root directory for user configuration settings.
    """
    return {
        'Windows': Path(os.path.expandvars('%LOCALAPPDATA%')),
        'Darwin': Path.home().joinpath('Library').joinpath('Application Support'),
        'Linux': Path.home().joinpath('.config')
    }[platform.system()].joinpath(package_name)


def get_logfile_path() -> Path:
    """
    Return a platform-specific log file path.
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    log_file = config_dir.joinpath("error.log")
    log_file.touch(exist_ok=True)
    return log_file

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(lineno)d::%(name)s::%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler(get_logfile_path())
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#endregion

def _build_ua_string() -> str:
    """
    Return a descriptive and truthful user agent string.
    """
    user_name = os.environ.get('USERNAME' if platform.system() == 'Windows' else 'USER', 'N/A')
    return f"{package_name}/{__version__} {platform.system()}/{platform.release()} CPython/{platform.python_version()} user_name/{user_name}"

def _progressbar_options(iterable, desc, unit, color="\033[32m", char='\u25CB', disable=False) -> dict:
    """
    Return custom optional arguments for `tqdm` progressbars.
    """
    return {
        'iterable': iterable,
        'bar_format': "{l_bar}%s{bar}%s{r_bar}" % (color, "\033[0m"),
        'ascii': char.rjust(9, ' '),
        'desc': desc,
        'unit': unit.rjust(1, ' '),
        'total': len(iterable),
        'disable': not disable
    }

def _query_db(db: str, sql: str, *args, local_: bool=False) -> List:
    """
    Apply a query to DBs that reside in the `hentai.data` namespace.
    """
    with resource_path('src.hentai.data' if local_ else 'hentai.data', db) as resource_handler:
        with closing(sqlite3.connect(resource_handler)) as connection:
            with closing(connection.cursor()) as cursor:
                return cursor.execute(sql, *args).fetchall()


@dataclass(frozen=True)
class Homepage:
    """
    The `Homepage` dataclass contains all doujins from the frontpage of
    <https://nhentai.net>, which is divided into two sub-sections: the
    `popular_now` section features 5 trending doujins, while `new_uploads`
    returns the 25 most recent additions to the DB.
    """
    popular_now: Set[Hentai]
    new_uploads: Set[Hentai]


@dataclass(frozen=True)
class User:
    """
    Provides public account information.
    """
    id: int
    username: str
    slug: str
    avatar_url: str
    is_superuser: bool
    is_staff: bool

    @property
    def url(self) -> str:
        return urljoin(Hentai.HOME, f"/users/{self.id}/{self.slug}")


@dataclass(frozen=True)
class Comment:
    """
    Defines comment object instances of doujin threads.
    """
    id: int
    gallery_id: int
    poster: User
    post_date: dt
    body: str


@dataclass(frozen=True)
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

    @classmethod
    def get(cls, tags: List[Tag], property_: str) -> str:
        """
        Return a list of tags as comma-separated string.

        Example
        -------
        ```
        from hentai import Hentai, Tag

        doujin = Hentai(177013)

        # english, translated
        print(Tag.get(doujin.language, 'name'))
        ```
        """
        if property_ not in Tag.__dict__.get('__dataclass_fields__').keys():
            raise ValueError(f"\033[31m{os.strerror(errno.EINVAL)}: {property_} not recognized as a property in {cls.__name__}\033[0m")
        return ', '.join([getattr(tag, property_) for tag in tags])

    @staticmethod
    def list(option: Option, local_: bool=False) -> List[Tag]:
        """
        Return a list of all tags where `option` is either

        `Option.Artist`
        `Option.Character`
        `Option.Group`
        `Option.Parody`
        `Option.Tag`
        `Option.Language`

        Example
        -------
        ```
        from hentai import Tag, Option

        # ['009-1', '07-ghost', '08th ms team', ...]
        print([tag.name for tag in Tag.list(Option.Group)])
        ```

        Note
        ----
        All tag count properties whose values exceed 999 are rounded to the nearest thousand.
        """
        if option not in [Option.Artist, Option.Character, Option.Group, Option.Parody, Option.Tag, Option.Language, Option.Category]:
            raise ValueError(f"\033[31m{os.strerror(errno.EINVAL)}: Invalid option ({option.name} is not an Tag object property)\033[0m")

        if option is Option.Category:
            raise NotImplementedError(f"\033[31mThis feature is not implemented yet\033[0m")

        tags = _query_db('tags.db', "SELECT * FROM Tag WHERE Type=:type_", {'type_': option.value}, local_=local_)
        number = lambda count: int(count) if str(count).isnumeric() else int(count.strip('K')) * 1_000
        return [Tag(int(tag[0]), tag[1], tag[2], urljoin(Hentai.HOME, tag[3]), number(tag[4])) for tag in tags]

    @staticmethod
    def search(option: Option, property_: str, value, local_: bool=False) -> Tag:
        """
        Return the first tag object of type `option` whose `property_` matches with `value`.

        Example
        -------
        ```
        from hentai import Tag

        # ID=3981
        print(f"ID={Tag.search(Option.Artist, 'name', 'shindol').id}")
        ```
        """
        return next(filter(lambda tag: getattr(tag, property_) == value, Tag.list(option, local_=local_)))


@dataclass(frozen=True)
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
        ```
        from hentai import Hentai

        doujin = Hentai(177013)

        # [WindowsPath('1.jpg'), WindowsPath('2.jpg'), ...]
        print([page.filename for page in doujin.pages])
        ```
        """
        num = Path(urlparse(self.url).path).name
        return Path(num).with_suffix(self.ext)

    def download(self, handler: RequestHandler, dest: Path=Path.cwd()) -> None:
        """
        Download an individual page to `dest`.

        Example
        -------
        ```
        from hentai import Hentai

        doujin = Hentai(177013)

        # download the last page to the CWD
        doujin.pages[-1].download(doujin.handler)
        ```
        """
        with open(dest.joinpath(self.filename), mode='wb') as file_handler:
            for chunk in handler.get(self.url, stream=True).iter_content(1024*1024):
                file_handler.write(chunk)


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
    Epos = 'epos'
    NumFavorites = 'num_favorites'
    Tag = 'tag'
    Group = 'group'
    Parody = 'parody'
    Character = 'character'
    Language = 'language'
    Artist = 'artist'
    Category = 'category'
    Cover = 'cover'
    Thumbnail = 'thumbnail'
    Images = 'image_urls'
    NumPages = 'num_pages'

    all: List[Option] = lambda: [option for option in Option if option.value != 'raw']


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
        ```
        from hentai import Extension

        # .jpg
        print(Extension.convert('j'))
        ```
        """
        return f".{cls(key).name.lower()}"


class RequestHandler(object):
    """
    RequestHandler
    ==============
    Defines a synchronous request handler class that provides methods and
    properties for working with REST APIs that is backed by the `requests`
    library.

    Example
    -------
    ```
    from hentai import Hentai, RequestHandler

    response = RequestHandler().get(url=Hentai.HOME)

    # True
    print(response.ok)
    ```
    """
    __slots__ = ['timeout', 'total', 'status_forcelist', 'backoff_factor']

    _timeout = (5, 5)
    _total = 5
    _status_forcelist = [413, 429, 500, 502, 503, 504]
    _backoff_factor = 1

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
        return Retry(total=self.total, status_forcelist=self.status_forcelist, backoff_factor=self.backoff_factor)

    @property
    def session(self) -> Session:
        """
        Creates a custom session object. A request session provides cookie
        persistence, connection-pooling, and further configuration options
        that are exposed in the RequestHandler methods in form of parameters
        and keyword arguments.
        """
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=self.retry_strategy))
        session.hooks['response'] = [lambda response, *args, **kwargs: response.raise_for_status()]
        session.headers.update({"User-Agent": _build_ua_string()})
        return session

    def get(self, url: str, **kwargs) -> Response:
        """
        Returns the GET request encoded in `utf-8`. Adds proxies to this session
        on the fly if urllib is able to pick up the system's proxy settings.
        """
        response = self.session.get(url, timeout=self.timeout, proxies=getproxies(), **kwargs)
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
    -----------
    ```
    from hentai import Hentai

    doujin = Hentai(177013)

    # [ShindoLA] METAMORPHOSIS (Complete) [English]
    print(doujin)
    ````

    Docs
    ----
    See full documentation at <https://www.hentai-chan.dev/projects/hentai>.
    """
    __slots__ = ['__id', '__handler', '__url', '__api', '__response', '__json']

    HOME = "https://nhentai.net/"
    _URL = urljoin(HOME, '/g/')
    _API = urljoin(HOME, '/api/gallery/')

    def __init__(self,
                 id_: int=0,
                 timeout: Tuple[float, float]=RequestHandler._timeout,
                 total: int=RequestHandler._total,
                 status_forcelist: List[int]=RequestHandler._status_forcelist,
                 backoff_factor: int=RequestHandler._backoff_factor,
                 json: dict=None):
        """
        Start a request session and parse meta data from <https://nhentai.net> for this `id`.
        """
        if id_ and not json:
            self.__id = id_
            super().__init__(timeout, total, status_forcelist, backoff_factor)
            self.__handler = RequestHandler(self.timeout, self.total, self.status_forcelist, self.backoff_factor)
            self.__url = urljoin(Hentai._URL, str(self.id))
            self.__api = urljoin(Hentai._API, str(self.id))
            self.__response = self.handler.get(self.api)
            self.__json = self.response.json()
        elif not id_ and json:
            self.__json = json
            self.__id = Hentai.__get_id(self.json)
            self.__handler = RequestHandler()
            self.__url = Hentai.__get_url(self.json)
            self.__api = Hentai.__get_api(self.json)
        else:
            raise TypeError(f"\033[31m{os.strerror(errno.EINVAL)}: Define either id or json as argument, but not both or none\033[0m")

    def __str__(self) -> str:
        return self.title()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ID={str(self.id).zfill(6)})"

    def __hash__(self) -> int:
        return hash(self.id)

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
    def id(self) -> int:
        """
        Return the ID of this `Hentai` object.
        """
        return self.__id

    @property
    def url(self) -> str:
        """
        Return the URL of this `Hentai` object.
        """
        return self.__url

    @property
    def api(self) -> str:
        """
        Return the API access point of this `Hentai` object.
        """
        return self.__api

    @property
    def json(self) -> dict:
        """
        Return the JSON content of this `Hentai` object.
        """
        return self.__json

    @property
    def handler(self) -> RequestHandler:
        """
        Return the `RequestHandler` of this `Hentai` object.
        """
        return self.__handler

    @property
    def response(self) -> Response:
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

    def title(self, format_: Format=Format.English) -> str:
        """
        Return the title of this `Hentai` object. The format of the title
        defaults to `English`, which is the verbose counterpart to `Pretty`.
        """
        return self.json['title'].get(format_.value)

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
    def thumbnail(self) -> str:
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
    def upload_date(self) -> dt:
        """
        Return the upload date of this `Hentai` object as timezone aware datetime object.
        """
        return dt.fromtimestamp(self.epos, tz=timezone.utc)

    def __tag(json_: dict, type_: str) -> List[Tag]:
        return [Tag(tag['id'], tag['type'], tag['name'], urljoin(Hentai.HOME, tag['url']), tag['count'])
            for tag in json_['tags']
                if tag['type'] == type_]

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
        """
        Return the number of times this `Hentai` object has been favorited. Because
        the API does not populate `num_favorites` of recently uploaded doujins,
        it will try to parse its HTML file as a fallback measure.
        """
        num_favorites = int(self.json['num_favorites'])

        if num_favorites == 0:
            try:
                html_ = html.unescape(self.handler.get(self.url).text)
                btn_content = re.findall(r'''<span class="nobold">(.*?)</span>''', html_, re.I)
                num_favorites = int(btn_content[0].strip('()'))
            except HTTPError:
                logger.error(f"An error occurred while trying to parse the HTML file for {repr(self)} (num_favorites={num_favorites})", exc_info=True)

        return num_favorites

    @property
    def pages(self) -> List[Page]:
        """
        Return a collection of pages detailing URL, file extension, width and
        height of this `Hentai` object.
        """
        pages = self.json['images']['pages']
        extension = lambda num: Extension.convert(pages[num]['t'])
        image_url = lambda num: f"https://i.nhentai.net/galleries/{self.media_id}/{num}{extension(num-1)}"
        return [Page(image_url(num + 1), Extension.convert(_['t']), _['w'], _['h']) for num, _ in enumerate(pages)]

    @property
    def image_urls(self) -> List[str]:
        """
        Return all image URLs of this `Hentai` object, excluding cover and thumbnail.
        """
        return [image.url for image in self.pages]

    @property
    def related(self) -> Set[Hentai]:
        """
        Return a set of five related doujins.
        """
        return {Hentai(json=raw_json) for raw_json in self.handler.get(urljoin(Hentai._API, f"{self.id}/related")).json()['result']}

    @property
    def thread(self) -> List[Comment]:
        """
        Return a list of comments of this `Hentai` object.
        """
        response = self.handler.get(urljoin(Hentai._API, f"{self.id}/comments")).json()
        user = lambda u: User(int(u['id']), u['username'], u['slug'], urljoin('i.nhentai.net/', u['avatar_url']), bool(u['is_superuser']), bool(u['is_staff']))
        comment = lambda c: Comment(int(c['id']), int(c['gallery_id']), user(c['poster']), dt.fromtimestamp(c['post_date'], tz=timezone.utc), c['body'])
        return [comment(data) for data in response]

    def download(self, dest: Path=None, folder: str=None, delay: float=0, zip_dir: bool=False, progressbar: bool=False) -> None:
        """
        Download all image URLs of this `Hentai` object to `dest`, excluding cover
        and thumbnail. By default, `folder` will be located in the CWD named after
        the doujin's `id`. Set a `delay` between each image download in seconds. If
        `zip_dir` is set to `True`, the download directory `folder` will be archived
        in `dest`. Enable `progressbar` for status feedback in terminal applications.
        """
        try:
            folder = str(self.id) if folder is None else folder
            dest = Path(folder) if dest is None else Path(dest).joinpath(folder)
            dest.mkdir(parents=True, exist_ok=True)
            for page in tqdm(**_progressbar_options(self.pages, f"Download #{str(self.id).zfill(6)}", 'page', disable=progressbar)):
                page.download(self.handler, dest)
                time.sleep(delay)
            if zip_dir:
                Utils.compress(dest)
                shutil.rmtree(dest, ignore_errors=True)
        except HTTPError as error:
            logger.error(f"Download failed for {repr(self)}", exc_info=True)
            if progressbar:
                print(f"#{str(id).zfill(6)}: {error}", file=sys.stderr)

    def export(self, filename: Path, options: List[Option]=None) -> None:
        """
        Store user-customized data about this `Hentai` object as a JSON file.
        Includes all available options by default.
        """
        Utils.export([self], filename, options)

    @staticmethod
    def exists(id_: int) -> bool:
        """
        Check whether or not an ID exists on <https://nhentai.net>.
        """
        try:
            return RequestHandler().get(urljoin(Hentai._URL, str(id_))).ok
        except HTTPError:
            return False

    def dictionary(self, options: List[Option]) -> dict:
        """
        Return a dictionary for this `Hentai` object whose key-value pairs
        are determined by the `options` list.
        """
        data = {}

        if Option.Raw in options:
            raise NotImplementedError(f"\033[31m{os.strerror(errno.EINVAL)}: Access self.json to retrieve this information\033[0m")

        for option in options:
            property_ = getattr(self, option.value)
            if isinstance(property_, list) and len(property_) != 0 and isinstance(property_[0], Tag):
                data[option.value] = [tag.name for tag in property_]
            elif option.value == 'title':
                data[option.value] = self.title(Format.Pretty)
            else:
                data[option.value] = property_
        return data


class Utils(object):
    """
    Hentai Utility Library
    ======================
    This class provides a handful of miscellaneous static methods that extend the
    functionality of the `Hentai` class.

    Example 1
    ---------
    ```
    from hentai import Utils

    # 177013
    print(Utils.get_random_id())
    ```

    Example 2
    ---------
    ```
    from hentai import Hentai, Sort, Format, Utils

    lolis = Utils.search_by_query('tag:loli', sort=Sort.PopularWeek)
    ```
    """
    def exists(error_msg: bool=False):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except HTTPError as error:
                    logger.error(f"DNE (*args={','.join([arg for arg in args])})", exc_info=True)
                    if error_msg:
                        print(error, file=sys.stderr)
            return wrapper
        return decorator

    @staticmethod
    def get_random_id(handler: RequestHandler=RequestHandler()) -> int:
        """
        Return a random ID.
        """
        response = handler.get(urljoin(Hentai.HOME, 'random'))
        return int(urlparse(response.url).path.split('/')[-2])

    @staticmethod
    def get_random_hentai(handler: RequestHandler=RequestHandler()) -> Hentai:
        """
        Return a random `Hentai` object.
        """
        return Hentai(Utils.get_random_id(handler))

    @staticmethod
    def download(doujins: List[Hentai], delay: float=0, progressbar: bool=False, zip_dir: bool=False) -> None:
        """
        Download all image URLs for a sequence of `Hentai` object to the CWD,
        excluding cover and thumbnail. Set a `delay` between each image download
        in seconds. Enable `progressbar` for status feedback in terminal applications.
        """
        for doujin in doujins:
            doujin.download(delay=delay, progressbar=progressbar, zip_dir=zip_dir)

    @staticmethod
    def browse_homepage(start_page: int, end_page: int, handler: RequestHandler=RequestHandler(), progressbar: bool=False) -> Set[Hentai]:
        """
        Return a list of `Hentai` objects that are currently featured on the homepage
        in range of `[start_page, end_page]`. Each page contains as much as 25 results.
        Enable `progressbar` for status feedback in terminal applications.
        """
        if start_page > end_page:
            raise ValueError(f"\033[31m{os.strerror(errno.EINVAL)}: start_page={start_page} <= {end_page}=end_page is False\033[0m")
        data = set()
        for page in tqdm(**_progressbar_options(range(start_page, end_page+1), 'Browse', 'page', disable=progressbar)):
            with handler.get(urljoin(Hentai.HOME, 'api/galleries/all'), params={'page': page}) as response:
                for raw_json in response.json()['result']:
                    data.add(Hentai(json=raw_json))
        return data

    @staticmethod
    def get_homepage(handler: RequestHandler=RequestHandler()) -> Homepage:
        """
        Return an `Homepage` object, i.e. all doujins from the first page of the
        homepage.

        Example
        -------
        ```
        from hentai import Utils

        homepage = Utils.get_homepage()
        popular_now = homepage.popular_now
        new_uploads = homepage.new_uploads
        ```
        """
        try:
            html_ = html.unescape(handler.get(Hentai.HOME).text)
        except HTTPError as error:
            logger.error(f"Failed to establish a connection to {Hentai.HOME}", exc_info=True)
            print(error, file=sys.stderr)
        else:
            titles = re.findall(r'''<div class="caption">(.*?)</div>''', html_, re.I)[0:5]

            return Homepage(
                popular_now={doujin for doujin in Utils.search_by_query(query='*', sort=Sort.PopularToday, handler=handler) if str(doujin) in titles},
                new_uploads=Utils.browse_homepage(1, 1, handler)
            )

    @staticmethod
    def search_by_query(query: str, page: int=1, sort: Sort=Sort.Popular, handler: RequestHandler=RequestHandler()) -> Set[Hentai]:
        """
        Return a list of `Hentai` objects on page `page` that match this search
        `query` sorted by `sort`.
        """
        payload = {'query': query, 'page': page, 'sort': sort.value}
        with handler.get(urljoin(Hentai.HOME, 'api/galleries/search'), params=payload) as response:
            return {Hentai(json=raw_json) for raw_json in response.json()['result']}

    @staticmethod
    def search_by_tag(id_: int, page: int=1, sort: Sort=Sort.Popular, handler: RequestHandler=RequestHandler()) -> Set[Hentai]:
        """
        Return a list of `Hentai` objects on page `page` that match this tag
        `id_` sorted by `sort`.
        """
        payload = {'tag_id': id_, 'page': page, 'sort': sort.value}
        with handler.get(urljoin(Hentai.HOME, "api/galleries/tagged"), params=payload) as response:
            return {Hentai(json=raw_json) for raw_json in response.json()['result']}

    @staticmethod
    def search_all_by_query(query: str, sort: Sort=Sort.Popular, handler: RequestHandler=RequestHandler(), progressbar: bool=False) -> Set[Hentai]:
        """
        Return a list of all `Hentai` objects that match this search `query`
        sorted by `sort`. Enable `progressbar` for status feedback in terminal applications.

        Example
        -------
        ```
        from hentai import Utils, Sort, Format

        lolis = Utils.search_all_by_query('tag:loli', sort=Sort.PopularToday)
        ```
        """
        data = set()
        payload = {'query': query, 'page': 1, 'sort': sort.value}
        with handler.get(urljoin(Hentai.HOME, '/api/galleries/search'), params=payload) as response:
            for page in tqdm(**_progressbar_options(range(1, int(response.json()['num_pages'])+1), 'Search', 'page', disable=progressbar)):
                for doujin in Utils.search_by_query(query, page, sort, handler):
                    data.add(doujin)
        return data

    @staticmethod
    def export(iterable: List[Hentai], filename: Path, options: List[Option]=None) -> None:
        """
        Store user-customized data of `Hentai` objects as a JSON file.
        Includes all available options by default.

        Example
        -------
        ```
        from hentai import Utils, Sort, Option

        lolis = Utils.search_by_query('tag:loli', sort=Sort.PopularToday)
        Utils.export(popular_loli, Path('lolis.json'), options=[Option.ID, Option.Title])
        ```
        """
        if options is None:
            Utils.export(iterable, filename, options=Option.all())
        elif Option.Raw in options:
            with open(filename, mode='w', encoding='utf-8') as file_handler:
                json.dump([doujin.json for doujin in iterable], file_handler)
        else:
            with open(filename, mode='w', encoding='utf-8') as file_handler:
                json.dump([doujin.dictionary(options) for doujin in iterable], file_handler)

    @staticmethod
    def compress(folder: Path) -> None:
        """
        Archive `folder` as `ZipFile` (Windows) or `TarFile` (Linux and macOS)
        using the highest compression levels available.
        """
        if platform.system() == 'Windows':
            with ZipFile(f"{folder}.zip", mode='w', compression=ZIP_DEFLATED, compresslevel=9) as zip_handler:
                for file in Path(folder).glob('**/*'):
                    zip_handler.write(file)
        else:
            with tarfile.open(f"{folder}.tar.gz", mode='x:gz') as tar_handler:
                tar_handler.add(folder)
