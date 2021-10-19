# Contributing

Please note that this project assumes that you have python `v3.7+`
installed. Even though this project deals with NSFW content, we want
to keep all talk on GitHub topic related and appropriate for work with
software development.

## Getting Started

If you want to to work on a new feature or fix an existing one,
create a new topic branch denoted by `dev-*`. In case of the former
one it is recommended to create an new issue first. Make sure that
you pass all unit tests before making a pull requests, and write a
new test if your feature isn't already covered by one of the other
tests. Generally speaking, this project doesn't really need any
external dependencies other than the `requests` module, so if you want
to introduce new dependencies into your work discuss these changes
in your commit message so that it is clear why this would be necessary.
Henceforth, starting with `v1.0` all commit message shall start with one
these acronyms:

- **API:** an (incompatible) API change
- **BUG:** bug fix
- **DEP:** deprecate something, or remove a deprecated object
- **DEV:** development tool or utility
- **DOC:** documentation
- **ENH:** enhancement
- **MAINT:** maintenance commit (refactoring, typos, etc.)
- **REV:** revert an earlier commit
- **STY:** style fix (whitespace, PEP8)
- **TST:** addition or modification of tests

Commit messages that only change a few lines of code should be compressed
into one line (less than 72 characters in length), else try to be more descriptive
and outline the reasons that justify each modification.

## Style Guidelines

At the moment, there're no strict rules in place to enforce a particular style.
By and large I try to follow PEP8 with a few exceptions; for example, line lengths
can go up to 160 characters, although I don't encourage you to go out of your way
to write one-liner everywhere. Another thing you might notice is that enums use
`CamelCase` instead of `ALLCAPPS`. Client-facing methods and properties should contain
doc strings and examples where examples would make sense, the code itself however
should be self-explanatory. Use the discussion panel if you have any other questions
about this or reach out to me personally via mail which is my preferred method of
communication.

## Workflow

After forking this repository you can open a new `dev-*` branch. When working in
a team it's better to let all changes come together in a release branch (`rec-hentai`),
before they go on to `master` where they get build and deployed to PyPI. It is
important to respect this naming convention to trigger the CI scripts. Therefore,
PR that don't follow this convention cannot be merged into this project. Adding
unit tests is for the most part mandatory if you implement new functionality. Passing
all required checks is important to qualify for a code review. Despite all of that
don't shy away from asking questions if anything is unclear.

## Additional Sources

You may find it useful to browse through code of similar repositories.
[Documentation](https://www.hentai-chan.dev/projects/hentai) for this
code base is a work in progress and will be continuously improved over time.
