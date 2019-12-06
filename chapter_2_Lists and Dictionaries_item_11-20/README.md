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

