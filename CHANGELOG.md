# Changelog

## Version 3.1.4 (01 December 2020)

Improves error message feedback for raised exceptions and deprecates all static
`Tag` methods in favor of

- `Tag.get(cls, tags: List[Tag], property: str) -> str:`

Besides, the `self.download` method in `Hentai` replaces the `dest` keyword argument
with `folder`, i.e. the name of the folder where the images are to be stored. The
new default name for this folder corresponds to the `id` of this doujin. A previous
internal method is also now exposed in the pubic interface:

- `self.dictionary(options: List[Option]=None) -> dict`

This method returns a flattened dictionary whose key-value pairs are determined
by the list of options passed as argument to this method. Also note that the

- `Utils.get_homepage(handler=RequestHandler()) -> Homepage`

method lost its `page: int=1` keyword argument.

## Version 3.1.3 (21 November 2020)

This version improves the general quality of the code and adds a missing feature
to the `get_homepage` function. It now returns an object that gives access to the
`popular_now` and `new_uploads` section as a list of hentai objects. In previous
versions, `new_uploads` was returned implicitly.

Furthermore, the `Utils.download` function now takes `doujins: List[Hentai]` instead
of `ids: List[int]` as main parameter to reduce the total number of calls made to
the API.

Also notice that the following export options have been renamed:

- `Option.Favorites` now is `Option.NumFavorites`
- `Option.UploadDate` now is `Option.Epos`
- `Option.PageCount` now is `Option.NumPages`

## Version 3.1.2 (16 November 2020)

Fixes an error in `RequestHandler` where `retry_strategy` passed its arguments
in the wrong order to `Retry` which caused the session to halt at times, courtesy
of @kiranajij <kiranajij216@gmail.com>.

On top of that, this patch also adds an `exists` decorator to the `Utils` class
for better error handling.

## Version 3.1.1 (14 November 2020)

Deprecates the `make_request` parameter everywhere and adds proper error handling
to both download functions. Changes doc strings to the restructured text format
because of the better linting support. Lastly, this patch removes old artifacts
which considerably reduces the file size of this module.

## Version 3.1.0 (12 November 2020)

This version adds a `progressbar` option (disabled by default) to the following
functions:

- `self.download` in `Hentai`
- `Utils.download`
- `Utils.browse_homepage`
- `Utils.search_all_by_query`

Another new feature allows a direct comparison between `Hentai` objects based on
their ID:

- `__gt__` (`>`)
- `__ge__` (`>=`)
- `__eq__` (`==`)
- `__le__` (`<`)
- `__lt__` (`<=`)
- `__ne__` (`!=`)

Additionally, you can now also access the `epos` value directly in `Hentai`
by property instead of going back and forth between conversions. Lastly, the
following fields are now readonly:

- `self.id`
- `self.json`
- `self.url`
- `self.api`
- `self.handler`
- `self.response`

This upgrade also fixes an error that previously occurred when you used the `Option.Raw`
option in `Utils.export`. Last but not least, the `RequestHandler._timeout` value
has been relaxed to `(5,5)`.

## Version 3.0.0 (09 November 2020)

This will be the last major update to this library as work on this project slowly
comes to an end. In this version,

- Virtually all static methods in the `Hentai` have been removed - use their
  corresponding properties instead. This change drastically reduces the number of
  lines of code in the main class
- The following functions have been renamed:
  - `Utils.static_export` now is `Utils.export`
  - `Utils.download_queue` now is `Utils.download`
- Adds `List[Hentai]` as type hint to `Utils.export`
- Additionally, three more properties have been added to the `Hentai` object:
  - `self.group`
  - `self.parody`
  - `self.character`
- Adds export of all new options mentioned above
- The magic method `__repr__` changes its output to `Hentai(ID={self.id})`
- Updates & improves doc strings

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
