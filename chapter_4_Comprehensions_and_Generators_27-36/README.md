# Chapter 4. Comprehensions and Generators.

Many programs are build to manipulate lists, dictionary key/value pairs, sets. For this kind of situations Python provides special syntax, called `comprehensions`, for succinctly iterating through these types of data and creating derivative data structures. Comprehensions can significantly improve the readability and provide with other benefits. 

This style of processing data is extended to the functions called *generators*. This functions incrementally return values from iterative data types. Generators improve performance, memory usage and readability  

## Item 27: Use Comprehensions Instead of `map` and `filter`
Python provide syntax for deriving a list from another iterable data structure. it is called *list comprehension*. 

* Here we will have a list of square of each number from other list using `for` loop:
```python
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares = []
for x in a:
    squares.append(x**2)

print(squares)
```
    >>>
    [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

* The same output can be output can be achieved by using list comprehension:
```python
squares = [x**2 for x in a] # List Comprehension
print(squares)
```
    >>>
    [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

* Unless you are applying a single-argument function, list comprehensions are also clearer that the `map` built-in function, which requires creation of the lambda function for computation:
```python 
alt = map(lambda x: x ** 2, a)
```

Unlike `map`, list comprehensions can easily filter input values. Here we will show square values only for even numbers:
```python
even_squares = [x**2 for x in a if x % 2 == 0]

print(even_squares)
```
    >>>
    [4, 16, 36, 64, 100]

The `filter` and `map` built-in can be used to achieve the same outcome, but it is much harder to read:
```python
alt = map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, a))
assert list(alt) == even_squares
```

* Dictionaries and sets have their own comprehensions, called *dictionary comprehension* and *set comprehension* respectively. This make it easy to create a derivative data structures when working with algorithms: 
```python
even_square_dict = {x: x**2 for x in a if x % 2 == 0}
thees_cubed_set = {x**3 for x in a if x % 3 == 0}
print(even_square_dict)
print(thees_cubed_set)
```
    >>>
    {2: 4, 4: 16, 6: 36, 8: 64, 10: 100}
    {216, 729, 27}

* Using `map` and `filter` is even noisier:
```python
alt_dict = dict(map(lambda x: (x, x**2), 
                filter(lambda x: x % 2 == 0, a)))
alt_set = set(map(lambda x: x **3, 
            filter(lambda x: x % 3 == 0, a)))
```

## Item 28: Avoid More Than Two Control Subexpressions in Comprehensions
Beyond simple usage, comprehensions allow using multiple level of lopping. 

* For example, we want to flatten a matrix in to a list:
```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [x for row in matrix for x in row]
print(flat)
```
    >>>
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
This example is readable and straightforward. The usage of comprehension is reasonable. 

* Another reasonable usage of list-comprehension would be replacing two-level-dip replacement of the input list. Like in the example of the squared values of two dimensional matrix. This list-comprehension is little more noisier, but still relatively easy to read:
```python
squared = [[x**2 for x in row] for row in matrix]
print(squared)
```
    >>>
    [[1, 4, 9], [16, 25, 36], [49, 64, 81]]

* However, if this comprehension were with more loops it would become al long as the regular `for loop` construction and harder to read, even. 
```python
my_list = [[1, 2, 4], [4, 5, 6],]
    ...

flat = [x for sublist_1 in my_list
        for sublist_2 in sublist_1
        for x in sublist_2]
```
Here, is the regular `for loop` statement producing same result:
```python
flat = []
for sublist_1 in my_list:
    for sublist_2 in sublist_1:
        flat.extend(sublist_2)
```

* Comprehensions support multiple `if` conditions. Basically, there could be an `if`, `or`, `and` condition after each `for` subexpression. Following comprehensions are examples of overloaded list-comprehensions and should be avoided, difficulty of reading and comprehending:
```python
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
b = [x for x in a if x > 4 if x % 2 == 0]
c = [x for x in a if x > 4 and x % 2 == 0] # It is equivalent to the b code

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
filtered = [[x for x in row if x % 3 == 0]
                for row in matrix if sum(row) >= 10]
print(filtered)
```
    >>>
    [[6], [9]]

* general rule of thumb is not to use more than two control subexpressions in comprehensions. It could be two `for` loops, one `for` loop and one `if` statement, or two `if` statements. Beyond that, it is better to switch to the normal `if`and `for` statements and writing a helper functions.

## Item 29: Avoid Repeated Work in Comprehensions by Using Assignment Expressions
A common pattern of using all type of comprehension is the need to reference them in multiple places. 

* for example, we need to write a program for order handling. When a new order comes we need to tell if you can fullfil the order. We need to verify if we have enough of stock and it is above of the minimal threshold for shipment(8):
```python

stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

order = ["screws", "wingnuts", "clips"]

def get_batches(count, size):
    return count // size

result = {}

for name in order:
    count = stock.get(name, 0)
    batches = get_batches(count, 8)
    if batches:
        result[name] = batches

print(result)
```
    >>>
    {'screws': 4, 'wingnuts': 1}

* We can rewrite `for` statement using dict-comprehension following way:
```python
found = {name: get_batches(stock.get(name, 0), 8)
        for name in order
        if get_batches(stock.get(name, 0), 8)}
print(found)
```
    >>>
    {'screws': 4, 'wingnuts': 1}

Although, this is more compact, the `get_batches(stock.get(name, 0), 8)` is repeated. This hurts readability and technically unnecessary. Moreover, it is bug prone, if we letter decided to change the batch size to 4 and make change only in one place of the code, we will end up with different results:
```python
has_bug = {name: get_batches(stock.get(name, 0), 4)
            for name in order
            if get_batches(stock.get(name, 0), 8)}  

print("Expected:", found)
print("Found:", has_bug)
```
    >>>
    Expected: {'screws': 4, 'wingnuts': 1}
    Found: {'screws': 8, 'wingnuts': 2}

An easy solution to this is use `walrus` assignment, to make assignment as a part of the comprehension:
```python
found = {name: batches for name in order
        if (batches := get_batches(stock.get(name, 0), 8))}
```

Assignment expression `batches := get_batches(...)` allows me to get values for each `order` key in the stock dictionary a single time, call `get_batches` only once, and store its corresponding value in the batches variable. I can then reference this variable else where in the comprehension to construct a `dict`s content, without calling `get_batches` a second time. Eliminating unnecessary calls to `get` and `get_batches` may also improve performance. 

It's a valid syntax to define a assignment expression in the value expression of the comprehension. However, if you try to reference the variable in other parts og the comprehension we might get a exception, do to the order in which comprehensions are evaluated:
```python
result = {name: (tenth := count // 10)
            for name, count in stock.items() if tenth > 0}
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 2, in <dictcomp>
    NameError: name 'tenth' is not defined

This error can be fixed by moving the assignment expression in the condition and then referencing variable name its defined in the comprehension's value expression:
```python
result = {name: tenth for name, count in stock.items()
            if (tenth := count // 10) > 0}
```
    >>>
    {'nails': 12, 'screws': 3, 'washers': 2}

If comprehension uses the walrus operator in the value part of the comprehension and doesn't have a condition, it'll leak the loop variable in to the containing scope. 
```python
half = [(last := count // 2) for count in stock.values()]
print(f"Last item of {half} is {last}")
```
    >>>
    Last item of [62, 17, 4, 12] is 12

This leakage of the loop variable is similar to what happens in regular `for` loop statements:
```python
for count in stock.values(): # Leaks loop variable
    pass

print(f"Last item of {list(stock.values())} is {count}")
```
    >>>
    Last item of [125, 35, 8, 24] is 24

However, the for loop variable of the comprehension does not leak:
```python
half = [count // 2 for count in stock.values()]
print(half) # Works
print(count) # Exception because loop variable doesn't leak
```
    >>>
    [62, 17, 4, 12]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    NameError: name 'count' is not defined

It is better **not to leak** loop variables, so it is recommended to use assignment expressions only in the condition part of a comprehensions. 

Assignment expressions works in similar way in the generator expressions:
```python
found = ((name, batches) for name in order
            if (batches := get_batches(stock.get(name, 0), 8)))
print(next(found))
print(next(found))
```
    >>>
    ('screws', 4)
    ('wingnuts', 1)

## Item 30: Consider Generators Instead of Returning List
The simplest choice for a function that produces sequence of results is to return a list of items. For example, we want to have an index of every word in the string. Here we accumulate avery index in a `list` using `append` and return it at the end of the function:
```python
def index_words(text):
    result = []
    if text:
        result.append(0)
    for index, letter in enumerate(text):
        if letter == " ":
            result.append(index + 1)
    return 
    
```
This works as expected for small simple cases:
```python
address = 'Four score and seven years ago...'
result = index_words(address)
print(result[:10])
```
    >>>
    [0, 5, 11, 15, 21, 27, 31, 35, 43, 51]

There is two problems with `index_words` function:
1. This code is noisy, and bulky. 

using generator it can be done more succinctly:
```python
def index_words_iter(text):
    if text:
        yield 0
    for index, letter in enumerate(text):
        if letter == " ":
            yield index + 1

it = index_words_iter(text)
print(next(it))
print(next(it))
```
    >>>
    0
    5

We can convert results of the generator to the `list` easily:
```python
result = list(index_words_iter(text))
print(result[:10])
```
    >>>
    [0, 5, 11, 15, 21, 27, 31, 35, 43, 51]

2. If big text is passed to the `index_words` function is passed, it will eat all the memory available and probably crush, because of the results needs to be stored in the `list` and returned only after it finishes all the computations. 

Where in generator it only requires memory for a single loop instance. Thus it can iterate through very big files. Following version of the generator is adapted to work with one line from a file:
```python
import itertools


def index_file(handle):
    offset = 0
    for line in handle:
        if line:
            yield offset
        for letter in line:
            offset += 1
            if letter == ' ':
                yield offset


with open("address.txt", "r") as f:
    it = index_file(f)
    results = itertools.islice(it, 0, 10)
    print(list(results))
```
    >>>
    [0, 5, 11, 15, 21, 27, 31, 35, 43, 51]

The only gotcha with generators is that returned values are stateful and cannot be reused.

## Item 31: Be Defensive When Iterating Over Arguments
When function takes a `list` of objects as a parameter, it is often important to iterate over it multiple times. For example, we want to analyse the number of tourist visited US Texas. Dataset is the number of tourist visited each city. We need to find percentage for this number. 

Do do this we need normalization function that sums the input to determine the total number of visits and then divided it by each city's tourist number:
```python
def normalize(numbers):
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result
```
This function work as expected when given a list of numbers:
```python
visits = [15, 35, 80]
percentages = normalize(visits)
print(percentages)
assert sum(percentages) == 100
```
    >>>
    [11.538461538461538, 26.923076923076923, 61.53846153846154]

To scale it up, we define a generator, to read data from a file that contains information about all the cities in Texas. 
```python
def read_visits(data_path):
    with open(data_path, "r") as f:
        for line in f:
            yield int(line)
```
Surprisingly, calling `normalize` over `read_visits` gives no results:
```python
it = read_visits("my_numbers.txt")
percentages = normalize(it)
print(percentages) 
```
    >>>
    []

This happens because a generator yields values only once. If a generator already risen `StopIteration` exception, it won't produce any results any more:
```python
it = read_visits("my_numbers.txt")
print(list(it))
print(list(it)) # Already exhausted!
```
    >>>
    [15, 35, 80]
    []

Confusingly, it won't raise and exception when iterating over already exhausted iterator. Functions in Python can't tell the difference between iterators that has no output and iterators that had an output but been exhausted.

To solve this problem, we can copy the entire output of the generator to the `list` and then iterate over `list` version of our data. 
```python
def normalize_copy(numbers):
    numbers_copy = list(numbers) # Copy the iterator
    total = sum(numbers_copy)
    result = []
    for value in numbers_copy:
        percent = 100 * value / total
        result.append(percent)
    return result

Now, the code will work correctly:
```python
it = read_visits('my_numbers.txt')
percentages = normalize_copy(it)
print(percentages)
assert sum(percentages) == 100.0
```
But, the content of the iterator may by extremely large, this is actually defeating the idea of writing the generator in the first place. The other way around is to return new iterator each call:
```python
def normalize_func(get_iter):
    total = sum(get_iter()) # New iterator
    result =[]
    for value in get_iter(): # New iterator
        percent = 100 * value / total
        result.append(percent)
    return result
```
To use `normalize_func` we can use a `lambda` function that calls a generator and produces a new generator each time:
```python
path = 'my_numbers.txt'
percentages = normalize_func(lambda: read_visits(path))
print(percentages)
assert sum(percentages) == 100.0
```
    >>>
    [11.538461538461538, 26.923076923076923, 61.53846153846154]
Although it works, it doesn't look very good. To make it better we can make a container class with implemented *iterator protocol* 

THe iterator protocol is how Python `for` loops and related expressions traverse content of a container type. When python sees the statement like `for x in foo`, it actually calls `iter(foo)`. The `iter()` built-in function calls `foo.__iter__` special method in turn. The `__iter__` method must return an iterator object (which itself implements `__next__` special method). Then, the `for` loop repeatedly called `next` built-in function on the iterator object until its exhausted (indicated by raising *StopIteration* exception).

It sounds complicated, but it is in fact easy to implement in classes with `__iter__` method as a generator. Here, we define a container class which reads content of the file:
```python
class ReadVisits:
    def __init__(self, data_path):
        self.data_path = data_path
    def __iter__(self):
        with open(self.data_path) as f:
            for line in f:
                yield int(line)
```
Now, this work with the original function:
```python
visits = ReadVisits(path)
percentages = normalize(visits)
print(percentages)
assert sum(percentages) == 100.0
```
    >>>
    [11.538461538461538, 26.923076923076923, 61.53846153846154]
This works because `sum` and `for` loop calls `ReadVisits.__iter__` method each independently and ensures that each of them gets full iterator to process. The only downside is that it reads the input data multiple times. 

To go further, we can test if the input can be iterated over and, if its not, to raise and exception:
```python
def normalize_defensive(numbers):
    if iter(numbers) is numbers: # An iterator -- bad!
        raise TypeError("Must supply a container")
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result
```
Alternatively, the `collections.abc` built-in module provides `Iterator` class that can be used in `isinstance` test to recognize a potential problem:
```python
from collections.abc import Iterator


def normalize_defensive(numbers):
    if isinstance(numbers, Iterator): # Another way to check
        raise TypeError("Must supply a container")
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result
```
This approach is ideal if you don't want to copy full iterator, but need to access it multiple times. This function works well with `list` and `ReadVisits` inputs because they are iterable containers:
```python
visits = [15, 25, 80]
percentages = normalize_defensive(visits)
assert sum(percentages) == 100.0

visits = ReadVisits(path)
percentages = normalize_defensive(visits)
assert sum(percentages) == 100.0
```
The function will raise an error if iterator is supplied:
```python
visits = [15, 25, 80]
it = iter(visits)
normalize_defensive(it)
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 3, in normalize_defensive
    TypeError: Must supply a container
This approach is also works for asynchronous iterators.

# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
