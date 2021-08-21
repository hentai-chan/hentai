<p align="center">
  <a href="https://www.hentai-chan.dev/projects/hentai" title="Project Logo">
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
        <img src="https://img.shields.io/pypi/pyversions/hentai">
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

# Python Hentai API 包装类

[English](https://github.com/hentai-chan/hentai/blob/master/README.md) | 简体中文

这个Python封包围绕nhentai的RESTFUL API导入一个包装类。
请注意这不是官方的API，对hentai.net的技术性问题应转至[support@nhentai.com](mailto:support@nhentai.com)。
也请留意这个模组的内容整体来说是工作不宜(NSFW)的。
最后，在这里我想提醒阁下在任何情况下都不应利用此模组在短时间内作出过多的请求。

## 安装

从 PyPI 取得最新的稳定版本:

```bash
pip install hentai --only-binary all
```

<details>
<summary>给贡献者看的开发人员注脚</summary>

又或者你想
[贡献](https://github.com/hentai-chan/hentai/blob/dev-hentai/CONTRIBUTING.md)，
请对以下储存库进行分支并执行

```bash
python -m venv venv/
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
# 另请安装以下依赖类型
pip install flake8 pytest wheel
# 执行全部单元测试
pytest --verbose -s
# 创造 wheel
python setup.py bdist_wheel --universal
```

请查看 `rec-hentai` 以确认你的作品与最新的候选版本同步。
请勿导入python 3.7+不支援的功能。

</details>

## 记载

你可以从网上的[文件](https://www.hentai-chan.dev/projects/hentai),
或在[wiki](https://github.com/hentai-chan/hentai/wiki) 取得关于此模组的更多资讯.

## 基础用法

`Hentai`令浏览nhentai.net变得十分简单。它使用平面的命名空间使其端点变得容易存取：

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

# 取得来源
doujin.download(progressbar=True)
```

除此之外，`hentai.Utils`也提供多种样辅助方法：

```python
from hentai import Utils, Sort, Option, Tag
from pathlib import Path

print(Utils.get_random_id())

# 给我介绍些好东西吧！
print(Utils.get_random_hentai())

# 利用查询进行进阶搜寻
for doujin in Utils.search_by_query('tag:loli', sort=Sort.PopularWeek):
    print(doujin.title(Format.Pretty))

# 显示所有同人誌的所有角色名
for character in Tag.list(Option.Character):
    print(character.name)

# 以JSON储存后设资料至硬盘
popular_loli = Utils.search_by_query('tag:loli', sort=Sort.PopularWeek)
custom = [Option.ID, Option.Title, Option.Epos]
Utils.export(popular_loli, filename=Path('popular_loli.json'), options=custom)
```

如果想知道更多查询字眼的话，请另见[https://nhentai.net/info/](https://nhentai.net/info/)。

## 指令列介面

自版本3.2.4起，本模组也提供基本的指令列介面以从在终端里下载同人誌：

```cli
# 取得帮助
hentai --help

# 将此同人下载到CWD
hentai download --id 177013

# 查看模组版本
hentai --version
```

## 取得联系

你可以透过[dev.hentai-chan@outlook.com](mailto:dev.hentai-chan@outlook.com)向我询问私人问题和不能归类于issue的事项。
