# Chapter 1. Pythonic Thinking

## Item 1: Know Which Version of Python You’re Using

Use Python 3

> ``python --version``

```python
    import sys
    print(sys.version_info)
    print(sys.version)
```

## item 2: Follow the PEP 8 Style Guide

#### Whitespace matters
* Use 4 [spaces]
* no more than 79 lines in 
* nest line of long line should be 4 [spaces] indented
* ``class`` and ``def`` should be separated by 2 empty lines (top, bottom)
* in ``class``, methods should be separated by 1 empty line
* ``{key: value,}`` no space before colon
* ``var = something`` spaces before and after colon
* ``def some(name: str):`` no space before colon in type annotations

#### Naming
* ``lowercase_underscore`` for functions, variables and attributes
* ``_leading_underscore`` for protected instance attributes
* ``__double_leading_underscore`` for private instance attributes
* ``class CapitalizedWord``
* ``ALL_CAPS`` for module-level constants
* ``def some(self,):`` for name of first parameter for instance methods in classes
* ``def some(cls,)`` for name of first parameter of a class method

#### Expressions and Statements

Find the one, and/or only one obvious way to do it.

* ``if a is not``
* ``if not some_list`` to check if empty
* ``if some_list`` to check if not empty
* no single-line ``if``,``for``,``while``, ``except``. 

#### Imports
* All ``import`` are always on the top
* ``from bar import foo`` always use absolute names
* ``from . import foo`` for relative import
* Section imports in the following order:
    1. standard library
    2. modules
    3. 3rd-party modules
    4. your own modules

## Item 3: Know the Differences Between ``bytes`` and ``str``

Use *Unicode sandwich*, always decode string possible to "utf-8" as soon as possible.

Use helper functions to turn bytes to strings:
```python
def to_str(bytes_or_str):
    """Turns bytes into string, or return string"""
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode("utf=8")
    else:
        value = bytes_or_str
    return value

```

To turn string to bytes:
```python
def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode("utf-8")
    else:
        value = bytes_or_str
    return value

```


