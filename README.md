<div align="center">
  <img height="150" style="margin-top:15px" src="https://raw.githubusercontent.com/hentai-chan/hentai/master/docs/hentai.svg">
</div>

<h1 align="center">Python Hentai API Wrapper</h1>

<p align="center">
    <a href="https://github.com/hentai-chan/hentai/actions?query=workflow%3ACI">
        <img src="https://github.com/hentai-chan/hentai/workflows/CI/badge.svg">
    </a>
    <a href="https://pypi.org/project/hentai/">
        <img src="https://github.com/hentai-chan/hentai/workflows/PyPI/badge.svg">
    </a>
    <img src="https://img.shields.io/pypi/v/hentai?color=blue&label=Release">
    <img src="https://img.shields.io/badge/Python-3.7%20%7C%203.8-blue">
    <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
</p>

<p align="center">
This python package implements a wrapper class around <code>nhentai</code>'s
RESTful API. Note that the content of this module is generally considered NSFW.
</p>

## Installation

Get the most recent stable release from PyPI:

```bash
pip install hentai
```

## Basic Usage

`Hentai` makes it very easy to browse through [https://nhentai.net](https://nhentai.net/).
It implements a flat namespace for easy access of all their endpoints:

```python
from hentai import Hentai, Format

doujin = Hentai(177013)

# METAMORPHOSIS
print(doujin.title(Format.Pretty))

# [Tag(id=3981, type='artist', name='shindol', url='/artist/shindol/', count=279)]
print(doujin.artist)

# ['dark skin', 'group', ... ]
print([tag.name for tag in doujin.tag])

# 2016-10-18 14:28:49
print(doujin.upload_date)

# ['https://i.nhentai.net/galleries/987560/1.jpg', ... ]
print(doujin.image_urls)
```

Apart from that, `Hentai` also provides a handful of miscellaneous static methods:

```python
from hentai import Sort

# recommend me something good!
random_id = Hentai.get_random_id()

# format defaults to 'English'
print(Hentai(random_id).title())

# advanced search with queries
for doujin in Hentai.search_by_query('tag:loli', sort=Sort.PopularWeek):
    print(Hentai.get_title(doujin))
```

See also [https://nhentai.net/info/](https://nhentai.net/info/) for more information
on search queries.

## Documentation

I know this is important. I will be working on automating this in a timely manner.
Stay tuned! In the mean time, use the [wiki](https://github.com/hentai-chan/hentai/wiki)
as a first point of reference.

## Get In Touch

You can reach me at [dev.hentai-chan@outlook.com](mailto:dev.hentai-chan@outlook.com)
for private questions and inquires that don't belong to the issue tab.
