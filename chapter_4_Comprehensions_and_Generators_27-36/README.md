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

## Item 32: Consider Generator Expressions for Large List Comprehensions
Problem with list comprehensions is they are creating a `list` with a single value for each value of the input sequence. This is fine for small input, but a large input will consume all the memory and crash a program.

For example, we want to read a file and return the number of characters of each line. Here is a list comprehension which require to hold length of every line in memory:
```python
value = [len(x) for x in open("my_numbers.txt")]
print(value)
```
    >>>
    [100, 57, 15, 1, 12, 75, 5, 86, 89, 11]

To solve this issue, Python has generator expressions, which are generalizations of list comprehensions and generators. As a normal generators, they don't hold the whole input in the memory, but yield one item at the time. 

To make a generator expression we need to put list comprehension in `()`. The previous syntax made generator, but with the generator object as a output:
```python
it = (len(x) for x in open("my_numbers.txt"))
print(it)
```
    >>>
    <generator object <genexpr> at 0x000002603BC56248>
```python
print(next(it))
print(next(it))
```
    >>>
    100
    57

Another powerful outcome of the generator is that they can be composed together. One generator is taken as a input for another generator:
```python
roots = ((x, x**0.5) for x in it)
print(next(roots))
```
    >>>
    (15, 3.872983346207417)
THe calling last generator will trigger previous iterator and they will together move through the sequence. 
However, it is sample, they can work with large inputs efficiently, this outputs are stateful, be aware of using them multiple times. 


## Item 33: Compose Multiple Generators with `yield from`
Using generators has variety of benefits and solutions to common problems. Generators are so useful that many programs seems like layers of generators strung together.

For example, we need a program to display movements on the screen. TO make an animation we need 2 functions, one for movement and one to stop:
```python
def move(period, speed):
    for _ in range(0, period):
        yield speed


def pause(delay):
    for _ in range(0, delay):
        yield 0
```

To create tje animation, we need to combine `move` and `pause` together to produce single sequence of on screen deltas. We will do this by calling a generator for each step of the animation, iterating over each generator in turn, and then yielding the deltas from all of them in sequence:
```python
def animate():
    for delta in move(4, 5.0):
        yield delta
    for delta in pause(10):
        yield delta
    for delta in move(2, 3.0):
        yield delta
```
ANd now, we need render those deltas on screen as they are produced by single `animation` generator:
```python
def render(delta):
    print(f"Delta: {delta:.1f}")
    # Move the image onscreen
    ...

def run(func):
    for delta in func():
        render(delta)

run(animate)
```
    >>>
    Delta: 5.0
    Delta: 5.0
    Delta: 5.0
    Delta: 5.0
    Delta: 0.0
    Delta: 0.0
    Delta: 0.0
    Delta: 3.0
    Delta: 3.0

The problem with this code is the repetitive nature of the `animate` function. Redundancy of `for` statements and `yield` expressions for each generator adds noise and hurts readability. This example has only three nested generators, but it is already hard to read. Example with more complex movements will be much harder to follow.

The solution to this problem is to use `yield from` expression. This advance generator feature allows you to yield all the values from the nested generator before returning control to the parent generator. Here, is the `animate` function written using `yield from`:
```python
def animate_composed():
    yield from move(4, 5.0)
    yield from pause(3)
    yield from move(2, 3.0)

run(animate_composed)
```
    >>>
    Delta: 5.0
    Delta: 5.0
    Delta: 5.0
    Delta: 5.0
    Delta: 0.0
    Delta: 0.0
    Delta: 0.0
    Delta: 3.0
    Delta: 3.0

The result is the same, but function is clearer and makes python take care of `for` and `yield` expressions using `yield from`. It is, also, has better performance:
```python
import timeit

def child():
    for i in range(1_000_000):
        yield i

def slow():
    for i in child():
        yield i

def fast():
    yield from child()


baseline = timeit.timeit(
    stmt="for _ in slow(): pass",
    globals=globals(),
    number=50)
print(f"Manual nesting {baseline:.2f}s")

comparison = timeit.timeit(
    stmt="for _ in fast(): pass",
    globals=globals(),
    number=50
)
print(f"Composed nesting {comparison:.2f}s")

reduction = (baseline - comparison) / baseline
print(f"{reduction:.1%} less time")
```
    >>>
    Manual nesting 9.50s
    Composed nesting 8.63s
    9.2% less time

Item 34: Avoid Injecting Data Into Generator Using `send`

`yield` provides generators with a handy way to produce an iterable series of output values.But it is unidirectional. There is now immediately obvious way to simultaneously stream in and out of generator as it runs. Having such a bidirectional communication with a generator could be valuable in variety of ways.

For example, we need to write a program to transmit a signal using software-defined radio. Here, is a function to generate an approximation of a sine wave with a given numbers of points:
```python
import math


def wave(amplitude, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        yield output
```
Now, I can transmit the wave signal at a single specified amplitude by iterating over `wave` generator:
```python
def transmit(output):
    if output is None:
        print(f"Output is None")
    else:
        print(f"Output:{output:>5.1f}")

def run(it):
    for output in it:
        transmit(output)

run(wave(3.0, 8))
```
    >>>
    Output:  0.0
    Output:  2.1
    Output:  3.0
    Output:  2.1
    Output:  0.0
    Output: -2.1
    Output: -3.0
    Output: -2.1
This works fine for producing a basic waveforms, but it can't be used to constantly vary the amplitude of the wave based on separate input (i.e., as required to broadcast a AM radio signals). We need a way to modulate a the amplitude for each iteration of a generator.

Python generators support `send` method, which upgrades `yield` expressions into two-way channel. The `send` method can be used to provide a streaming input to the generator at the same time it's yielding outputs. Normally, when iterating a generator, the value of the `yield` expression is `None`:
```python
def my_generator():
    received = yield 1
    print(f"received = {received}")

it = iter(my_generator())
output = next(it)           # Get first generator output
print(f"output = {output}")
try:
    next(it)                # Runs generator until it exists
except StopIteration:
    pass
```
    >>>
    output = 1
    received = None
When we call `send` method instead iterating the generator with `for` loop or `next` built-in function, the supplied parameter becomes value of the `yield` expression the the generator is resumed.
However, when a generator first start, a `yield` expression is has not been encountered yet, so the only valid value for calling `send` is `None` (any other argument would raise an exception at runtime):
```python
it = iter(my_generator())
output = it.send(None)      # Get generator output
print(f"output = {output}")

try:
    it.send("hello!")       # Send value into the generator
except StopIteration:
    pass
```
    >>>
    output = 1
    received = hello!
To use `send` method we need to change our wave generator.
```python
def wave_modulating(steps):
    step_size = 2 * math.pi / steps
    amplitude = yield                   # Receive initial amplitude
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        amplitude = yield output        # Receive next amplitude
```
Also, we need to change the `run()` function. 
```python
def run_modulating(it):
    amplitudes = [
        None, 7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10,]
    for amplitude in amplitudes:
        output = it.send(amplitude)
        transmit(output)

run_modulating(wave_modulating(12))
```
    >>>
    Output is None
    Output:  0.0
    Output:  3.5
    Output:  6.1
    Output:  2.0
    Output:  1.7
    Output:  1.0
    Output:  0.0
    Output: -5.0
    Output: -8.7
    Output:-10.0
    Output: -8.7
This works. But it has problems. First, it is difficult for a new reader to understand: using yield on the right side is not intuitive and it is hard to understand the link between `yield` and `send` without knowing advanced generator feature. 

Now, imagine program requirements are changed. We need to use more complex waveform consisting of multiple signals in sequence. One way to implement this is by composing multiple generators using `yield from` expression:
```python
def complex_wave():
    yield from wave(7.0, 3)
    yield from wave(2.0, 4)
    yield from wave(10.0, 5)

run(complex_wave())
```
    >>>
    Output:  0.0
    Output:  6.1
    Output: -6.1
    Output:  0.0
    Output:  2.0
    Output:  0.0
    Output: -2.0
    Output:  0.0
    Output:  9.5
    Output:  5.9
    Output: -5.9
    Output: -9.5
This works with simple wave, it also works with `send` method. Here is the example of composing multiple calls to the `wave_modulating()` generator together:
```python
def complex_wave_modulating():
    yield from wave_modulating(3)
    yield from wave_modulating(5)
    yield from wave_modulating(4)

run_modulating(complex_wave_modulating())
```
    >>>
    Output is None
    Output:  0.0
    Output:  6.1
    Output: -6.1
    Output is None
    Output:  0.0
    Output:  1.9
    Output:  1.2
    Output: -5.9
    Output: -9.5
    Output is None
    Output:  0.0
This works, but there is a surprise: There are many `None` values. It happens because each `yield from` starts with bare `yield` - without a value - to receive a value from `send` method. This cause the parent generator to output `None` for each transition between child generators.

THis mean that even that these approaches work individually, will be broken when used together. Although, it's possible to modify `run_modulation` function to work around `None`, it does not worth a trouble. It is already complicated to understand how `send` works. The surprising effect of the `yield from` is even worse. We should avoid `send` method altogether and use simpler approach.

The easiest solution is to pass and iterator into the `wave()` function. The iterator should return an input amplitude each time the `next` build-in function is called. This arrangement ensures that each generator is progressed in a cascade as input and outputs a processed:
```python
def wave_cascading(amplitude_it, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        amplitude = next(amplitude_it)  # Get next input
        output = amplitude * fraction
        yield output
```
We can pass the same iterator into each child generator functions, because iterators are stateful and each child generator will start from the place where previous one has ended:
```python
def complex_wave_cascading(amplitude_it):
    yield from wave_cascading(amplitude_it, 3)
    yield from wave_cascading(amplitude_it, 4)
    yield from wave_cascading(amplitude_it, 5)
```
Now, we can run the composed generators by simply passing in an iterator from `amplitudes list:
```python
def run_cascading():
    amplitudes = [7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    it = complex_wave_cascading(iter(amplitudes))
    for amplitude in amplitudes:
        output = next(it)
        transmit(output)

run_cascading()
```
    >>>
    Output:  0.0
    Output:  6.1
    Output: -6.1
    Output:  0.0
    Output:  2.0
    Output:  0.0
    Output: -2.0
    Output:  0.0
    Output:  9.5
    Output:  5.9
    Output: -5.9
    Output: -9.5
The best part of this approach is that input can came from anywhere and can be completely dynamic. The only downside is that it assumes that input generator is thread safe, which may not be the case. If you need cross thread boundaries, `async` functions may be a better fit.

## Item 34: Avoid Causing State Transition in Generators With `throw`
In addition to the `yield from` and `send` advanced generators feature, there is a `throw` method used to re-raise `Exception` instances within generator functions. The way `throw` works is simple: When method is called, the next occurrence of a `yield` expression re-raised the provided `Exception` instances after its output is received instead of continuing normally. Simple example implemented here:
```python
class MyError(Exception):
    pass


def my_generator():
    yield 1
    yield 2
    yield 3


it = my_generator()
print(next(it))
print(next(it))
print(it.throw(MyError("test error")))
```
    >>>
    1
    2
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 3, in my_generator
    __main__.MyError: test error
When you call `throw`, the generator function may catch the injected exception with standard `try/except` compound statement that surrounds the last `yield` expression that was executed:
```python
def my_generator():
    yield 1
    try:
        yield 2
    except MyError:
        print("Got MyError!")
    else:
        yield 3
    yield 4

it = my_generator()
print(next(it))
print(next(it))
print(it.throw(MyError("test error")))
```
    >>>
    1
    2
    Got MyError!
    4
This functionality provides a two-way communication chanel between a generator and its caller That can be useful in certain situations. For example, we need a timer that supprts a sporadic resets. Here is a generator that relies on the `throw` method:
```python
class Reset(Exception):
    pass


def timer(period):
    current = period
    while current:
        current -= 1
        try:
            yield current
        except Reset:
            current = period
```
In this code, whenever the `Reset` is raised by the yield expression, the counter resets itself to the initial position.

We can connect this counter reset to an external input that's pulled every second. Then We can define `run` function to drive the `timer` generator, which injects exception with `throw` to cause reset, or calls `announce` for each generator output:
```python
RESET = [
    False, False, False, True, False, True, False,
    False, False, False, False, False, False, False]

def check_for_reset():
    # Poll for external event
    return RESET.pop(0)

def announce(remaining):
    print(f"{remaining} ticks remaining")

def run():
    it = timer(50)
    while True:
        try:
            if check_for_reset():
                current = it.throw(Reset())
            else:
                current = next(it)
        except StopIteration:
            break
        else:
            announce(current)

run()
```
    >>>
    3 ticks remaining
    2 ticks remaining
    1 ticks remaining
    3 ticks remaining
    2 ticks remaining
    3 ticks remaining
    2 ticks remaining
    1 ticks remaining
    0 ticks remaining
This code works, but it is much harder to read than it should be.

The simpler approach is to define a stateful closure using an iterable container object. Here is this approach:
```python
class Timer:
    def __init__(self, period):
        self.current = period
        self.period = period
    def reset(self):
        self.current = self.period
    def __iter__(self):
        while self.current:
            self.current -= 1
            yield self.current
```
Now, the `run` function can be rewritten using `for` loop:
```python
def run():
    timer = Timer(4)
    for current in timer:
        if check_for_reset():
            timer.reset()
        announce(current)

run()
```
    >>>
    3 ticks remaining
    2 ticks remaining
    1 ticks remaining
    0 ticks remaining
    3 ticks remaining
    2 ticks remaining
    3 ticks remaining
    2 ticks remaining
    1 ticks remaining
    0 ticks remaining
The output matches the previous version using `throw`, but this implementation is much easier to understand. Often, if you need to mix generators and exceptions, you should better use asynchronous features. So, don't use `throw`. 

## Item 36: Consider `itertools` for Working with Iterators and Generators
The `itertools` buit-in module contains a large numbers of functions that a re useful for organizing and interacting with iterators. 
```python
import itertools
```
Whenever you find yourself dealing with tricky iteration code, consider looking onto the `itertools` module again, there might be something interesting for you. 

Here are functions grouped in three most interesting categories:
### 1: Linking iterators together:
* ***chain***
Use `chain` to combine several iterators into a single iterator:
```python
it = itertools.chain([1, 2, 3], [4, 5, 6])
print(list(it))
```
    >>>
    [1, 2, 3, 4, 5, 6]
* ***repeat***
Use `repeat` to output a value forever, or with second parameter to specify for how many times:
```python
it = itertools.repeat("hello", 3)
print(list(it))
```
    >>>
    ['hello', 'hello', 'hello']
* ***cycle***
Use `cycle` to repeat the iterator forever:
```python
it = itertools.cycle([1, 2])
result = [next(it) for _ in range(10)]
print(result)
```
    >>>
    [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
* ***tee***
Use `tee` to divide one iterator into multiple parallel iterators. Number of the parallel iterators specified in second parameter. Memory usage will grow if iterators don't progress at the same speed. 
```python
it1, it2, it3 = itertools.tee(["first", "second"], 3)
print(list(it1))
print(list(it2))
print(list(it3))
```
    >>>
    ['first', 'second']
    ['first', 'second']
    ['first', 'second']
* ***zip_longest***
This is variant of `zip` function. Returns a placeholder value when one of the iterators shorter. 
```python
keys = ["one", "two", "three"]
values = [1, 2]

normal = list(zip(keys, values))
print("zip:", normal)

it = itertools.zip_longest(keys, values, fillvalue="nope")
longest = list(it)
print("zip_longest:", longest)
```
    >>>
    zip:         [('one', 1), ('two', 2)]
    zip_longest: [('one', 1), ('two', 2), ('three', 'nope')]

### 2: Filtering items from an Iterator
* ***islice***
Use `islice` to slice an iterator by numerical indexes without copying. It uses `end`, `start-end`, `start-end-step` syntax and the behavior is similar to usual slicing and striding.
```python
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

first_five = itertools.islice(values, 5)
print("First five:", list(first_five))

middle_odds = itertools.islice(values, 2, 8, 2)
print("Middle odds:", list(middle_odds))
```
    >>>
    First five: [1, 2, 3, 4, 5]
    Middle odds: [3, 5, 7]
* ***takewhile***
`takewhile` returns values from an iterator until predefined function returns `False`:
```python
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
less_than_seven = lambda x: x < 7
it = itertools.takewhile(less_than_seven, values)
print(list(it))
```
    >>>
    [1, 2, 3, 4, 5, 6]
* ***dropwhile***
`dropwhile` is the opposite of the `takewhile`. It starts to return values only after predefined function returns `True`:
```python
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
less_than_seven = lambda x: x < 7
it = itertools.dropwhile(less_than_seven, values)
print(list(it))
```
    >>>
    [7, 8, 9, 10]
* ***filterfalse***
`filterfalse`, which is the opposite of the `filter` built-in function, returns all values from iterator which values are `False` in predicated function:
```python
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = lambda x: x % 2 == 0

filter_results = filter(evens, values)
print("Filter:      ", list(filter_results))

filter_false_results = itertools.filterfalse(evens, values)
print("Filter false:", list(filter_false_results))
```
    >>>
    Filter:       [2, 4, 6, 8, 10]
    Filter false: [1, 3, 5, 7, 9]
### 3:Producing Combination of Items from Iterators
* ***accumulate***
`accumulate` folds an item from the iterator into a running value by applying a function that takes two parameters. It outputs current accumulated result for each input value:
```python
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
sum_reduce = itertools.accumulate(values)
print("Sum:   ", list(sum_reduce))

def sum_modulo_20(first, second):
    output = first + second
    return output % 20

modulo_reduce = itertools.accumulate(values, sum_modulo_20)
print("Modulo:", list(modulo_reduce))
```
    >>>
    Sum:    [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]
    Modulo: [1, 3, 6, 10, 15, 1, 8, 16, 5, 15]
If second parameter to `accumulate` is not given it will return accumulated sum of the input. It is same as `reduce` built-in function from the `functools`, but with outputs yielded 
one step at the time.
* ***product***
`product` returns Cartesian product of items from one or more iterators:
```python
single = itertools.product([1, 2], repeat=2)
print("Single:  ", list(single))

multiple = itertools.product([1, 2], ["a", "b"])
print("Multiple:", list(multiple))
```
    >>>
    Single:   [(1, 1), (1, 2), (2, 1), (2, 2)]
    Multiple: [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
* ***permutation***
`permutation` returns the unique ordered permutations on length `N` with items from an iterator:
```python
it = itertools.permutations([1,2,3,4], 2)
print(list(it))
```
    >>>
    [(1, 2), (1, 3), (1, 4), (2, 1), (2, 3), (2, 4), (3, 1), (3, 2), (3, 4), (4, 1), (4, 2), (4, 3)]
* ***combinations***
`combinations` returns the unordered combinations of length `N` with unrepeated items from an iterator:
```python
it = itertools.combinations([1, 2, 3, 4], 2)
print(list(it))
```
    >>>
    [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
* ***combinations_with_replacement***
`combinations_with_replacement` is the same as a `combinations`, but repeated values are allowed:
```python
it = itertools.combinations_with_replacement([1, 2, 3, 4], 2)
print(list(it))
    >>>
    [(1, 1), (1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (2, 4), (3, 3), (3, 4), (4, 4)]
    
# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
