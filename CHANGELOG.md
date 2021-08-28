# Changelog

## Version 3.2.8 (28 Aug 2021)

The log file path has been changed to a new, platform-specific location which is
accessible via code through the `get_logfile_path` method. Page objects now also
implement a download method which makes it possible to download individual pages:

```python
from hentai import Hentai
doujin = Hentai(177013)

# download the last page to the CWD
doujin.pages[-1].download(doujin.handler)
```

Another noticeably change took place in the download method of `Hentai` objects:
The `zip` option has been renamed to `zip_dir` to prevent conflicts with the built-in
`zip` method from the Python standard library. On top of all of that, its implementation
has also changed: archives created as a result of this operation use a `.zip` extension
on Windows platforms (as it already did previously), and `.tar.gz` on macOS and
Linux platforms (which is what's new). It also uses a more aggressive compression
configuration, which makes for smaller archives but also increases the overall
execution time.

Additionally, a bug related to the previous implementation has been fixed
by Shikanime Deva (<deva.shikanime@protonmail.com>) that was also caused by the
(former) `zip` option in which the download directory was not properly cleaned up
afterwards.

The `--verbose` option in the CLI is now turned on by default. You can revert this
change by using the `--no-verbose` flag to run this command in scripts silently.

Last but not least, the underlying `RequestHandler` class experienced a few minor
optimizations which also affects the `Hentai` class.

## Version 3.2.7 (29 June 2021)

Makes the `Hentai` class hashable and changes the return type of some methods from
`List[Hentai]` to `Set[Hentai]`. It also cuts down the total amount of external
dependencies to 2 (`requests` and `tqdm`). Another noticeable change took place
in the `RequestHandler` class: session objects now depict a descriptive and truthful
UA string. This makes it easier for server administrators to identify bot requests.

## Version 3.2.6 (15 May 2021)

Extends continuous integration scripts by running unit tests on all major platforms
and recent versions of python - the version matrix now also includes `3.10-beta.1`!

Note that this update also redefines the built-in CLI:

```bash
# now supports queued downloads! (turn on the progress bar with the verbose flag)
hentai --verbose download --id 1 2 3

# print title, genre, lang and num_pages (also supports multiple args)
hentai preview --id 177013
```

More importantly, this update also removes `requests_html` and `colorama` from the
list of required project dependencies, making this library more lightweight and
faster to install. Lastly, a security policy is now in place for disclosing
security vulnerabilities. Head over to this project's
[security policy](https://github.com/hentai-chan/hentai/blob/master/SECURITY.md)
to learn more about recommended security guidelines that you can follow while
developing your applications.

## Version 3.2.5 (26 February 2021)

Updates the documentation and moves the log file path on Linux back to `~/.hentai`,
but also improves the
[contributing notes](https://github.com/hentai-chan/hentai/blob/master/CONTRIBUTING.md)
for developers.

## Version 3.2.4 (09 February 2021)

Moves the log file path from the home directory to `/var/log` on Linux-like systems
and to `%LOCALAPPDATA%` on Windows. Also improves the GitHub issue templates and
implements a basic CLI:

```cli
# get help
hentai -h

# download doujin
hentai -id 177013

# check module version
hentai -version
```

## Version 3.2.3 (31 January 2021)

Adds log handler to the `hentai` module and implements a fallback mechanism to
the `num_favorites` property of Hentai objects for recently uploaded doujins. This
version also deprecates `setup.cfg` and made a few additional changes to the project
structure, none of which should have any effect on users of this library.

## Version 3.2.2 (17 January 2021)

Improves performance of `list` and `search` in `Tag` and changes the signature of
`search` to

- `search(option: Option, property_: str, value) -> Tag`

## Version 3.2.1 (31 December 2020)

Improves overall test coverage and implements

- `search(value, property_: str='name') -> Tag`

as a static method.

## Version 3.2.0 (27 December 2020)

In this version two new properties have been added to `Hentai` objects:

- `self.thread -> List[Comment]`
- `self.related -> List[Hentai]`

Additionally, datetime objects returned in any of this module's methods have been
made utc-timezone aware. URL properties in `Tag` objects now also return a fully
qualified path, e.g.

```python
from hentai import Hentai, Tag

doujin = Hentai(177013)

# old output:
# /language/english/, /language/translated/
# new output:
# https://nhentai.net/language/english/, https://nhentai.net/language/translated/
print(Tag.get(doujin.language, 'url'))
```

The `Tag` class now also features a static `Tag.list` method for the following
tag types:

- `Option.Artist`
- `Option.Character`
- `Option.Group`
- `Option.Parody`
- `Option.Tag`
- `Option.Language`

which returns all tags available related to the options above. This may be used
in combination with the

- `search_by_tag(id_: int, page: int=1, sort: Sort=Sort.Popular, handler=RequestHandler()) -> List[Hentai]`

method for browsing the nhentai catalogue by tag ID.

## Version 3.1.5 (09 December 2020)

After some reconsideration I came to the conclusion that it would be best when
none of the keyword arguments conflict with any of the built-in function from
python to further comply with PEP8 recommendations. Therefore, the following
arguments were renamed as followed:

- `property` becomes `property_`
- `id` becomes `id_`
- `format` becomes `format_`
- `type` becomes `type_`

The functions affected by this change were `Tag.get`, `Hentai.__init__`, `self.title`,
and `Hentai.exists`, respectively. In some instances, the previously missing return
type for some function signatures has been added back.

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
