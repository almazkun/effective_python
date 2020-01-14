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
















# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
