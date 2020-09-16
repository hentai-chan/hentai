# Python Hentai API Wrapper

![CI](https://github.com/hentai-chan/hentai/workflows/CI/badge.svg)
![PyPI](https://github.com/hentai-chan/hentai/workflows/PyPI/badge.svg)
![Version](https://img.shields.io/pypi/v/hentai?color=blue&label=Release)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This python package implements a wrapper class around `nhentai.net`'s RESTful API.

## Basic Usage

This package makes it very easy to browse through [https://nhentai.net](https://nhentai.net/).
It implements a flat namespace for easy access of the most common endpoints:

```python
from hentai import Hentai, Format

doujin = Hentai(177013)

# METAMORPHOSIS
print(doujin.title(Format.Pretty))

# [Tag(id=3981, type='artist', name='shindol', url='/artist/shindol/', count=279)]
print(doujin.artist)

# ['dark skin', 'group', 'mmf threesome', 'story arc', 'ahegao', 'anal', ... ]
print([tag.name for tag in doujin.tags])

# 2016-10-18 14:28:49
print(doujin.upload_date)

# ['https://i.nhentai.net/galleries/987560/1.jpg', 'https://i.nhentai.net/galleries/987560/2.jpg', ... ]
print(doujin.image_urls)
```

Aside from that, this package also provides a handful of miscellaneous static method:

```python
# recommend me something good!
random_id = Hentai.get_random_id()

# format defaults to 'English'
print(Hentai(random_id).title())

# advanced search with queries
print(Hentai.search_by_query('tag:loli'))
```

See also [https://nhentai.net/info/](https://nhentai.net/info/) for more information
on search queries.
