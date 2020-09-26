# Changelog

## Version 1.2

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
  - `filename()`
- Changes the signature from `get_tags(json: dict)` to `get_tag(json: dict)`
- Renames the property `tags` to `tag` in `Hentai`
