<p align="center">
  <a href="https://hentaichan.pythonanywhere.com/projects/hentai" title="Project Logo">
    <img height="150" style="margin-top:15px" src="https://raw.githubusercontent.com/hentai-chan/hentai/master/docs/hentai.svg">
  </a>
</p>

<p align="center">
  <i>“De gustibus non est disputandum.”</i>
</p>

<p align="center">
    <a href="https://github.com/hentai-chan/hentai/actions?query=workflow%3ACI" title="Continuous Integration" target="_blank">
        <img src="https://github.com/hentai-chan/hentai/workflows/CI/badge.svg">
    </a>
    <a href="https://github.com/hentai-chan/hentai/actions?query=workflow%3ACodeQL" title="Code QL Analysis" target="_blank">
        <img src="https://github.com/hentai-chan/hentai/workflows/CodeQL/badge.svg">
    </a>
    <a href="https://github.com/hentai-chan/hentai/actions?query=workflow%3APyPI" title="PyPI Build" target="_blank">
        <img src="https://github.com/hentai-chan/hentai/workflows/PyPI/badge.svg">
    </a>
    <a href="https://pypi.org/project/hentai/" title="Release Version" target="_blank">
        <img src="https://img.shields.io/pypi/v/hentai?color=blue&label=Release">
    </a>
    <a href="https://www.codefactor.io/repository/github/hentai-chan/hentai" title="Code Factor" target="_blank">
        <img src="https://www.codefactor.io/repository/github/hentai-chan/hentai/badge">
    </a>
    <a href="https://codecov.io/gh/hentai-chan/hentai" title="Code Coverage" target="_blank">
        <img src="https://codecov.io/gh/hentai-chan/hentai/branch/master/graph/badge.svg?token=HOE2YZO4V6"/>
    </a>
    <a title="Supported Python Versions">
        <img src="https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9-blue">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" title="License Information" target="_blank">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
    <a title="Downloads per Month">
        <img src="https://img.shields.io/pypi/dm/hentai">
    </a>
    <a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/hentai-chan/hentai.git" title="Software Heritage Archive" target="_blank">
        <img src="https://archive.softwareheritage.org/badge/origin/https://github.com/hentai-chan/hentai.git/">
    </a>
</p>

# Python Hentai API Wrapper

This python package implements a wrapper class around nhentai's RESTful API.
Please be aware that this is not an official API, technical questions about
nhentai.net should be redirected to
[support@nhentai.com](mailto:support@nhentai.com).
Further note that the content of this module is generally considered NSFW. Finally,
I would like to comment at this point that you should under no circumstances use
this module to make an unreasonable amount of requests in a short period of time.

## Installation

Get the most recent stable release from PyPI:

```bash
pip install hentai
```

<details>
<summary>Dev Notes for Contributors</summary>

Alternatively, if you're looking to make a
[contribution](https://github.com/hentai-chan/hentai/blob/dev-hentai/CONTRIBUTING.md)
fork this repository and run

```bash
python -m venv venv/
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
# additionally install the following dependencies
pip install flake8 pytest wheel
# run all unit tests
pytest --verbose
# create wheel
python setup.py bdist_wheel --universal
```

Make sure to checkout `rec-hentai` so that your work is up-to-date with the next
release candidate. Don't implement any features that are incompatible with
version 3.7+ of python.

</details>

## Documentation

You can find the [documentation](https://hentaichan.pythonanywhere.com/projects/hentai)
online, or use the [wiki](https://github.com/hentai-chan/hentai/wiki) to learn more
about this module.

## Basic Usage

`Hentai` makes it very easy to browse through nhentai.net. It implements a flat
namespace for easy access of all their endpoints:

```python
from hentai import Hentai, Format

doujin = Hentai(177013)

# True
Hentai.exists(doujin.id)

# METAMORPHOSIS
print(doujin.title(Format.Pretty))

# [Tag(id=3981, type='artist', name='shindol', url='https://nhentai.net/artist/shindol/', count=279)]
print(doujin.artist)

# ['dark skin', 'group', ... ]
print([tag.name for tag in doujin.tag])

# 2016-10-18 12:28:49+00:00
print(doujin.upload_date)

# ['https://i.nhentai.net/galleries/987560/1.jpg', ... ]
print(doujin.image_urls)

# get the source
doujin.download(progressbar=True)
```

Apart from that, `hentai.Utils` also provides a handful of miscellaneous helper
methods:

```python
from hentai import Utils, Sort, Option, Tag
from pathlib import Path

print(Utils.get_random_id())

# recommend me something good!
print(Utils.get_random_hentai())

# advanced search with queries
for doujin in Utils.search_by_query('tag:loli', sort=Sort.PopularWeek):
    print(doujin.title(Format.Pretty))

# print all character names from all doujins
for character in Tag.list(Option.Character):
    print(character.name)

# store custom meta data as JSON file to disk
popular_loli = Utils.search_by_query('tag:loli', sort=Sort.PopularWeek)
custom = [Option.ID, Option.Title, Option.Epos]
Utils.export(popular_loli, filename=Path('popular_loli.json'), options=custom)
```

See also [https://nhentai.net/info/](https://nhentai.net/info/) for more information
on search queries.

## Command Line Interface

Starting with version 3.2.4, this module also provides a rudimentary CLI for downloading
doujins within the terminal:

```cli
# get help
hentai -h

# download this doujin to the CWD
hentai -id 177013

# check the module version
hentai -version
```

## Get In Touch

You can reach me at [dev.hentai-chan@outlook.com](mailto:dev.hentai-chan@outlook.com)
for private questions and inquires that don't belong to the issue tab.
