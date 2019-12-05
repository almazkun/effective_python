# Chapter 1. Pythonic Thinking

## Item 1: Know Which Version of Python You’re Using

Use Python 3

> ``python --version``

```python
    import sys


    print(sys.version_info)
    print(sys.version)
```

## Item 2: Follow the PEP 8 Style Guide

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

Use *Unicode sandwich*, always decode string to "utf-8" as soon as possible. Always work with `b'ytes'` and `b'ytes'` or `str` and `str`, never `b'ytes'` and `str`. 

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
    """Turns str into bytes, or return bytes"""
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode("utf-8")
    else:
        value = bytes_or_str
    return value
```


#### Reading and writing bytes from/to files 

Use `"rb"` and `"wb"`

## Prefer Interpolated F-String Over C-style Format Strings and `str.format`

#### Don't use C-style formating
```python
"%(do_not) use C-style string" % (formating)
```

#### Don't use Built-in `str.format`
```python
"{do_not} use this one".format("too")
```

#### Use new Interpolated Format Strings - `f_strings` 
```python
f_string = f'{Use} {this} format'
```

Perks: 
* Can put Python expressions into braces:
    ```python 
    pantry = [
        ('avocados', 1.25),
        ('bananas', 2.5),
        ('cherries', 15),
    ]

    for i, (item, count) in enumerate(pantry):
        f_string = f"#{i+1}: {item.title():<10s} = {round(count)}"
        print(f_string)
    ```
    > \>>>
    >1: Avocados   = 1
    >2: Bananas    = 2
    >3: Cherries   = 15
    > \>>>

* Can split over multiple lines:
    ```python
    for i, (item, count) in enumerate(pantry):
        print(f"#{i+1}: "
            
                f"{item.title():<10s} = "
                f"{round(count)}")

    ```

* Can put variables into braces:
    ```python
    places = 3
    number = 1.23456
    print(f"My number is {number:.{places}f}")

    ```
    > \>>>
    > My number is 1.235
    > \>>>

## Item 5: Write Helper Functions Instead of Complex Expressions

Use helper functions for some repetitive task, even if you need to repeat it only couple of times. 

```python
from urllib.parse import parse_qs


my_values = parse_qs('red=5&blue=0&green=',
                        keep_blank_values=True)

print(repr(my_values))

```

> \>>>
>{'red': ['5'], 'blue': ['0'], 'green': ['']}
> \>>>

```python
my_values = {'red': ['5'], 'blue': ['0'], 'green': ['']}


def get_first_int(values, key, default=0):
    found = values.get(key, [""])

    if found[0]:
        return int(found[0])
    return default


red = get_first_int(my_values, "red")
blue = get_first_int(my_values, "blue")
green = get_first_int(my_values, "green")

print(red, blue, green)

```
> \>>>
5 0 0
> \>>>

## Item 6: Prefer Multiple Assignments Unpacking Over Indexing

`tuple` type is a immutable, ordered sequence of values.

```python
snack_calories = {
    "chips": 140,
    "popcorn": 80,
    "nuts": 190,
}
items = tuple(snack_calories.items())
print(items)

```
> \>>>
(('chips', 140), ('popcorn', 80), ('nuts', 190))
> \>>>

Unpacking:

```python
item = ("Peanut butter", "Jelly")
first, second = item #Unpacking
print(f"{first} and {second}")

```
> \>>>
Peanut butter and Jelly
> \>>>

* Use unpacking to swap in single line:
    ```python
    def bubble_sort(a):
        for _ in range(len(a)):
            for i in range(1, len(a)):
                if a[i] < a[i-1]:
                    print(a, a[i], a[i-1])
                    a[i-1], a[i] = a[i], a[i-1] # Swap

    names = ["pretzels", "carrots", "arugula", "bacon"]
    bubble_sort(names)
    print(names)

    ```

    > \>>>
    ['arugula', 'bacon', 'carrots', 'pretzels']
    > \>>>


* Use unpacking with `for` and `enumerate()`:
    ```python 
    snacks = [("bacon", 350), ("donut", 240), ("muffin", 190)]
    for rank, (name, calories) in enumerate(snacks, 1):
        print(f"#{rank}: {name} has {calories} calories")
    
    ```
    > \>>>
    #1: bacon has 350 calories
    #2: donut has 240 calories
    #3: muffin has 190 calories
    > \>>>
