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

x = ["red", "orange", "yellow", "green", "blue", "purple"]
odds = x[::2]
evens = x[1::2]
print(odds)
print(evens)
```
    >>>
    ['red', 'yellow', 'blue']
    ['orange', 'green', 'purple']