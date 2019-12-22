# Chapter 2. Lists and Dictionaries

## Item 11: Know How to Slice Sequences

You can slice `list`, `str` and `bytes`. 
Slicing syntax:
```python
somelist[start:end]
```
Different variations:
```python
a = ["a", "b", "c", "d", "e", "f", "g", "h"]

a[:]     # ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
a[:5]    # ['a', 'b', 'c', 'd', 'e']
a[:-1]   # ['a', 'b', 'c', 'd', 'e', 'f', 'g']
a[4:]    #                     ['e', 'f', 'g', 'h']
a[-3:]   #                          ['f', 'g', 'h']
a[2:5]   #           ['c', 'd', 'e']
a[2:-1]  #           ['c', 'd', 'e', 'f', 'g']
a[-3:-1] #                          ['f', 'g']
```

Slicing do not depend on the actual length of the `list`, it can silently omit missing items. Use this behavior to establish max length:
```python
first_twenty_items = a[:20]
last_twenty_items = a[-20:]
```

**Note:** be careful with negative indexes, it might have surprising results: `somelist[-0:]` is equal to `somelist[:]`.

The result of slicing is a new `list`. Original `list` is unchanged:
```python
b = a[3:]
print("Before:  ", b)
b[1] = 99
print("After:   ", b)
print("No change:", a) 
```
    >>>
    Before:    ['d', 'e', 'f', 'g', 'h']
    After:     ['d', 99, 'f', 'g', 'h']
    No change: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

However, when in assignments, slice replaces the specific range in original `list`.
Also, the length dose not matter, it will shrink or got longer:

```python
print("Before:", a)
a[2:7] = [99, 00, 888]
print("After:", a)
```
    >>>
    Before: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    After: ['a', 'b', 99, 0, 888, 'h']

To copy the `list` you can use:
```python
b = a[:]
```

You can replace entire list using this assignment:
```python
b = a
print("Before a: ", a)
print("Before b: ", b)
a[:] = [101, 102, 103]
print("After a:", a)
print("After b:", b)
```
    >>>
    Before a:  ['a', 'b', 47, 11, 22, 14, 'h']
    Before b:  ['a', 'b', 47, 11, 22, 14, 'h']
    After a: [101, 102, 103]
    After b: [101, 102, 103]

## Item 12: Avoid Striding and Slicing in a Single Expression 

You can stride sequence using following logic: 
```python
somelist = [start:end:stride]
```

#### It can be used for:
* Odds and evens
```python
x = ["red", "orange", "yellow", "green", "blue", "purple"]
odds = x[::2]
evens = x[1::2]
print(odds)
print(evens)
```
    >>>
    ['red', 'yellow', 'blue']
    ['orange', 'green', 'purple']


* To reverse byte string you can use:
```python
x = b"mongoose"
y = x[::-1]
print(y)
```
    >>>
    b'esoognom'

* To reverse UTF-8 strings:
```python
x = "寿司"
y = x[::-1]
print(y)
```
    >>>
    司寿
    

**Note** It won't work with unicode byte string. 

* Other examples:
```python
x = ["a", "b", "c", "d", "e", "f", "g", "h"]

x[::2]      # ['a', 'c', 'e', 'g']
x[::-2]     # ['h', 'f', 'd', 'b']
x[2::2]     # ['c', 'e', 'g']
x[-2::-2]   # ['g', 'e', 'c', 'a']
x[-2:2:-2]  # ['g', 'e']
x[2:2:-2]   # []
```

### But, this is very confusing syntax and should be avoided. 
If You need to use `Striding` with `Slicing`, consider using striding separately from slicing:
```python
y = x[::2]    # ['a', 'c', 'e', 'g']
z = x[1:-1]  # ['c', 'e']
```

## Item 13: Prefer Catch-All Unpacking over Slicing
One of the limitation of basic Unpacking is that you need to know the length of the list in advance. 

* Consider using *stared expression* to catch-all values that didn't fit the unpacking pattern:
```python
car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
car_ages_descending = sorted(car_ages, reverse=True)

oldest, second_oldest, *others = car_ages_descending
print(oldest, second_oldest, others)
```
    >>>
    20 19 [15, 9, 8, 7, 6, 4, 1, 0]

* The *stared expression* can be used at any position:
```python
oldest, *others, youngest = car_ages_descending
print(oldest, youngest, others)

*others, second_youngest, youngest = car_ages_descending
print(youngest, second_youngest, others)
```
    >>>
    20 0 [19, 15, 9, 8, 7, 6, 4, 1]
    0 1 [20, 19, 15, 9, 8, 7, 6, 4]

**Note** 
* However, you can't use *only* stared expression, you need to have at least one required part. 
```python 
*others = car_ages_descending
print(others)
```
    >>>
    File "<stdin>", line 1
SyntaxError: starred assignment target must be in a list or tuple

* You cant use 2 stared expressions:
```python
first, *middle, *second_middle, last = [1, 2, 3, 4] 
```
    >>>
    File "<stdin>", line 1
SyntaxError: two starred expressions in assignment

* Multiple catch-all unpacking can be used in multilevel structure, but better not be. 
```python
car_inventory = {
    "Downtown": ("Silver Shadow", "Pinto", "DMC"),
    "Airport": ("Skyline", "Viper", "Gremlin", "Nova")
}

((loc1, (best1, *rest1)),
 (loc2, (best2, *rest2))) = car_inventory.items()

print(f"Best at {loc1} is {best1}, {len(rest1)} others")
print(f"Best at {loc2} is {best2}, {len(rest2)} others")
```
    >>>
    Best at Downtown is Silver Shadow, 2 others
    Best at Airport is Skyline, 3 others

* The stared expressions always become `list`, and empty `list` if no leftover:
```python
short_list = [1, 2]
first, second, *rest = short_list
print(first, second, rest)
```
    >>>
    1 2 []

* Starred expressions can be used to display first row if iterator separately from iterator content:
```python
def generate_csv():
    yield ('Date', 'Make', 'Model', 'Year', 'Price')
    ...

it = generate_csv()
header, *rows = it
print("CSV Header:", header)
print("Row count:", len(rows))
```
    >>>
    CSV Header: ('Date', 'Make', 'Model', 'Year', 'Price')
    Row count: 200

**Note** Be careful to use stared expressions on long iterations, because it might eat all your memory. 


## Item 14: Sort by Complex Criteria Using `key` Parameter

* Use `sort()` method to sort built-in types which has a natural ordering to them:
```python
numbers = [93, 46, 75, 33, 0, 23, 33]
numbers.sort()
print(numbers)
```
    >>>
    [0, 23, 33, 33, 46, 75, 93]

* `sort()` do not work directly on objects. You need to use `key` parameter, which accepts function:
```python
class Tool():
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


tools = [
    Tool("level", 3.5),
    Tool("hammer", 1.25),
    Tool("screwdriver", 0.5),
    Tool("chisel", 0.25),
]

print("Unsorted:", repr(tools))
tools.sort(key=lambda x: x.name)
print("\nSorted:", tools)
```

    >>>
    Unsorted: [Tool('level', 3.5), Tool('hammer', 1.25), Tool('screwdriver', 0.5), Tool('chisel', 0.25)]
    
    Sorted: [Tool('chisel', 0.25), Tool('hammer', 1.25), Tool('level', 3.5), Tool('screwdriver', 0.5)]

* For `str` you may want to lower case each item in a list to ensure that they are in alphabetical order:
```python
places = ["home", "work", "New York", "Paris"]
places.sort()
print("Case sensitive:", places)
places.sort(key=lambda x: x.lower())
print("Case insensitive:", places)
```
    >>>
    Case sensitive: ['New York', 'Paris', 'home', 'work']
    Case insensitive: ['home', 'New York', 'Paris', 'work']

* for sorting with multiple criteria you may use `key` parameter returning `tuple` containing two attributes in required order:
```python
power_tools = [
    Tool('drill', 4),
    Tool('circular saw', 5),
    Tool('jackhammer', 40),
    Tool('sander', 4),
]

power_tools.sort(key=lambda x: (x.weight, x.name))
print(power_tools)
```
    >>>
    [Tool('drill', 4), Tool('sander', 4), Tool('circular saw', 5), Tool('jackhammer', 40)]

* Negation on `int`'s may be used to sort in different directions:
```python
power_tools.sort(key=lambda x: (-x.weight, x.name))
print(power_tools)
```
    >>>
    [Tool('jackhammer', 40), Tool('circular saw', 5), Tool('drill', 4), Tool('sander', 4)]

* To combine mane sorting criteria and different directions combine `sort` function calls following way and use `reverse` for changing direction:
```python
power_tools.sort(key=lambda x: x.name)
power_tools.sort(key=lambda x: x.weight, reverse=True)
print(power_tools)
```
    >>>
    [Tool('jackhammer', 40), Tool('circular saw', 5), Tool('drill', 4), Tool('sander', 4)]

## Item 15: Be Cautious When Relying on `dict` Insertion Ordering
Before Python 3.5 `key` orders `dict` are not in order they were inserted. From Python 3.6 `dict` items will be in order of insertion. 

`OrderedDict` is `dict` like type with preserving order of items. But it has different performance characteristics. 

* However, you should not rely on the fact that the are ordered in order of insertion, because it might cause unforeseen behavior:
```python
votes = {
    "otter": 1281,
    "polar bear": 587,
    "fox": 863,
}

def populate_ranks(votes, ranks):
    names = list(votes.keys())
    names.sort(key=votes.get, reverse=True)
        for i, name enumerate(names, 1):
            ranks[name] = i


def get_winner(ranks):
    return next(iter(ranks))


ranks = {}
populate_ranks(votes, ranks)
print(ranks)
winner = get_winner(ranks)
print(winner)
```
    >>>
    {'otter': 1, 'bear': 2, 'fox': 3}
    otter

It is all good, but if later the requirements have changes and now you need to show results in alphabetical order. To do so, you might use `collections.abc` built-in method, to make your own `dict`-like class which will iterate its contents in alphabetical order:
```python
from collections.abc import MutableMapping


class SortedDict(MutableMapping):
    def __init__(self):
        self.date = {}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __delitem__(self, key)
        del self.date[key]

    def __iter__(self):
        keys = list(self.data.keys())
        keys.sort()
        for key in keys:
            yield key

    def __len__(self):
        return len(self.data)


sorted_ranks = SortedDict()
populate_ranks(votes, sorted_ranks)
print(sorted_ranks.data)
winner = get_winner(sorted_ranks)
print(winner)
```
    >>>
    {'otter': 1, 'bear': 2, 'fox': 3}
    fox

The problem here os that `get_winner()` assumes that `dict`s content sorted in insertion order. Whish is no longer try in custom `dict` class. To avoid this bug, you have 3 options:

* To make `get_winner` check for the rank. This is most conservative and robust solution:
```python
def get_winner(ranks):
    for name, rank in ranks.items():
        if rank == 1:
            return name

winner = get_winner(sorted_ranks):
print(winner)
```
    >>>
    otter

* Also, you can check if a correct type were supplied and raise exception if not. This solution most probably have better runtime performance:
```python
def get_winner(ranks):
    if not ranks isinstance(ranks, dict):
        raise TypeError("must provide a dict instance")
    return next(iter(ranks))

get_winner(sorted_ranks)
```
    >>>
    Traceback ...
    TypeError: must provide a dict instance

* Third solution is to use type annotations to ensure that `dict` is passed:
```python
from typing import Dict, MutableMapping


def populate_ranks(votes: Dict[str, int],
                   ranks: Dict[str, int]) -> None
    names = list(votes.keys())
    names.sort(key=votes.get, reverse=True)
    for i, name in enumerate(names, 1):
        ranks[name] = i


def get_winner(ranks: Dict[str, int]) -> None
    return next(iter(ranks))


class SortedDict(MutableMapping[str, int]):
...

sorted_ranks = SortedDict()
populate_ranks(votes, sorted_ranks)
print(sorted_ranks.data)
winner = get_winner(sorted_ranks)
print(winner)
```
    >>>
    $ python3 -m mypy --strict example.py
    .../example.py:48: error: Argument 2 to "populate_ranks" has
    ➥incompatible type "SortedDict"; expected "Dict[str, int]"
    .../example.py:50: error: Argument 1 to "get_winner" has
    ➥incompatible type "SortedDict"; expected "Dict[str, int]"


# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)