# Changelog

## Version 2.0.1 (06 Nov 2020)

Fixes a bug that occurred every time the `make_request` parameter was used outside
the library's root directory. Additionally, this patch also comes with a few new
features:

- Adds the `scanlator` property to the `Hentai` class
- Overloads the constructor with the `json` option

## Version 2.0 (11 Oct 2020)

Warning: This version breaks backwards compatibility. In particular, the methods

- `search_by_query` moved from `Hentai` to `Utils`
- `search_all_by_query` moved from `Hentai` to `Utils`
- `get_homepage` moved from `Hentai` to `Utils`
- `browse_homepage` moved from `Hentai` to `Utils`
- `download_queue` moved from `Hentai` to `Utils`
- `get_random_id` moved from `Hentai` to `Utils`
- `call_api` was renamed to `get` in `RequestHandler`

now reside in a newly created `Utils` class. Note that the return type from
`browse_homepage` changes from an iterator of lists of dictionaries to a list of
dictionaries, so that you know get all results in a single list which should make
it easier to work with. This change also affects the `get_homepage` and
`search_all_by_query` functions.

On top of that, the following functions now take an additional optional
`make_request` parameter:

- `Hentai.exists(id: int, make_request: bool=True) -> bool`
- `Utils.get_random_id(make_request: bool=True, handler=RequestHandler()) -> int`
- `Utils.get_random_hentai(make_request: bool=True) -> Hentai`

Additionally, this version implements the following new features:

- `Hentai.get_url(json: dict) -> str`
- `Hentai.get_api(json: dict) -> str`
- `Hentai.export(self, filename: Path, options: List[Option]=None) -> None`
- `Utils.static_export(iterable, filename: Path, options: List[Option]=None) -> None:`
- `Option` enum for specifying export options in `export` and `static_export`
- Most functions attained descriptive doc strings and sometimes even small code snippets

Moreover, the `download` function now writes in chunks which should be a little
faster for bigger images. The `RequestHandler` sessions now looks for proxies if
urllib is able to pick up the system's proxy settings. The user agent for each
request will be provided by the `faker.providers.user_agent` sub-package powered
by `faker` (<https://github.com/joke2k/faker>).

Finally, this version also includes an utility script for collaborators.

## Version 1.2 (26 Sep 2020)

- Makes this module compatible with python version 3.7
- Adds the following Tag helper method:
  - `get_ids(tags: List[Tag])`
  - `get_types(tags: List[Tag])`
  - `get_names(tags: List[Tag])`
  - `get_count(tags: List[Tag])`
- Extends sort enum by
  - `PopularYear`
  - `PopularMonth`
  - `Date`
- Adds Page as a new data class featuring
  - `url`
  - Extension `ext`
  - Image `width`
  - Image `height`
  - Image `filename`
- Changes the signature from `get_tags(json: dict)` to `get_tag(json: dict)`
- Renames the property `tags` to `tag` in `Hentai`
