# Contributing

Please note that this project assumes that you have python `v3.8+`
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
into one line, else try to be more descriptive and outline the reasons
that justify each modification.

## Additional Sources

You may find it useful to browse through code of similar repositories.
Documentation for this code base is also on my bucket list and will be added
soon.
