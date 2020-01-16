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














# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
