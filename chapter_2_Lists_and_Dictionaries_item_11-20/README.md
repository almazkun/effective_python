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