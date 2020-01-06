# Chapter 3. Functions

## Item 19: Never Unpack More Than Three Variables When Function Return Multiple Values

* Unpacking allows seemingly return more than one value:
```python
def get_stats(numbers):
    minimum = min(numbers)
    maximum = max(numbers)
    return minimum, maximum

lengths = [63, 73, 72, 60, 67, 66, 71, 61, 72, 70]

minimum, maximum = get_stats(lengths)

print(f"Min: {minimum}, Max: {maximum}")
```
    >>>
    Min: 60, Max: 73

* Multiple values also can be packed using `*stared_expressions`:
```python
def get_avg_ratio(numbers):
    average = sum(numbers) / len(numbers)
    scaled = [x / average for x in numbers]
    scaled.sort(reverse=True)
    return scaled

longest, *middle, shortest = get_avg_ratio(lengths)

print(f"Longest: {longest:>4.0%}")
print(f"Shortest: {shortest:>4.0%}")
```
    >>>
    Longest: 108%
    Shortest: 89%

* Now, imagine you need to show also min, max, avg, median and total population. It can be dome by extending our previous function:
```python
def get_stats(numbers):
    maximum = max(numbers)
    minimum = min(numbers)
    count = len(numbers)
    average = sum(numbers) / count

    sorted_numbers = sorted(numbers)
    middle = count // 2
    if middle % 2 == 0:
        lower = sorted_numbers[middle - 1]
        upper = sorted_numbers[middle]
        median = (lower + upper) / 2
    else:
        median = sorted_numbers[middle]
    return minimum, maximum, average, median, count

minimum, maximum, average, median, count = get_stat(numbers)

print(f"Min: {minimum}, Max: {maximum}")
print(f"Average: {average}, Median: {median}, Count {count}")
```
    >>>
    Min: 60, Max: 73
    Average: 67.5, Median: 70, Count 10

But, this approach has two main problems. First, all the return values are numeric and it is easy to reorder them accidentally and not to notice that. Which, will lead to the hard-to-find bugs in the future. Second, is that line of unpacking of the values is to long and, according to the PEP 8, it should be divided into more lines. Which will hurt readability. 

To avoid these problems you should never use more than tree(3) variables when unpacking multiple return values from a function. Instead, small class or `namedtuple` maybe used.

## Item 20: Prefer Raising Error to Returning `None`
Sometimes returning `None` in helper function seems natural. Like in case of division function:
```python
def careful_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
```
It can work properly:
```python
x, y = 1, 0
result = careful_divide(x, y)
if result is None:
    print("Invalid inputs")
```
But, `None` could also mean `False`. So, following code will be wrong:
```python
x, y = 0, 5

result = careful_divider(x, y)
if not result:
    print("Invalid inputs") # This runs, but shouldn't.
```

* To avoid such problems, you may return tuple with two values indicating of division was successful and the result of the division:
```python
def careful_divider(a, b):
    try:
        return True, a / b
    except ZeroDivisionError:
        return False, None

success, result = careful_division(x, y)
if not success:
    print("Invalid inputs")
```
But it alo can lead to the same problems, for instance, `_` underscore variable name may be used to ignore part or the `tuple`:
```python
_, result = careful_division(x, y)
if not result:
    print("Invalid inputs")
```

* The next better way is to raise an exception and make the caller to handle it:
```python
def careful_division(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        raise ValueError("Invalid inputs")
```
This way the caller do not need to check if the result is valid and use it in `else` block:
```python
x, y = 3, 9
try:
    result = careful_division(x, y)
except ValueError:
    print("Invalid inputs")
else:
    print(f"Result is {result:>.1}")
```

* This approach can be extended by using `type annotation` and `docstring`:
```python 
def careful_division(a: float, b:float) -> float:
    """Divides a by b.

    Raises:
        ValueError: When inputs cannot be divided.
    """
    try:
        return a / b
    except ZeroDivisionError as e:
        raise ValueError("Invalid inputs")
```

## Item 21: Know How Closures Interact with Variable Scope
Let's imagine that you want to sort `list` of numbers, but prioritize one group of number to come first. You can do it by passing a helper function as a `key` argument to the `sort()` method.  
```python
def sort_priority(values, group):
    def helper(x):
        if x in group:
            return (0, x)
        return (1, x)
    values.sort(key=helper)
```
This function works for simple inputs:
```python
numbers = [8, 3, 1, 2, 5, 4, 7, 6]
group = {2, 3, 5, 7}
sort_priority(numbers, group)
print(numbers)
```
    >>>
    [2, 3, 5, 7, 1, 4, 6, 8]

There are 3 reasons why this is working:
1. Python supports *Closures* - that is, functions that refer to the variable from scope in which they were defined. That is why `helper` function can access `group` argument from `sort_priority`.
2. Functions are *first-class* objects in Python. They you can refer them directly, assign the to the variables, pass them as a arguments to other functions, compare them in expressions and if statements, and so on. This is why `sort()` method can accept closure `helper` function as a `key` argument. 
3. Python has specific rules for comparing elements. Fist, it compares element with index `0`, then, if they are equal, compare elements and index `1` and so on. That is why the return values from the `helper` closure causes the sort order to have two distinct groups. 


It'd be nice if this function also return a flag if the numbers from group is present. Adding this seems like not a hard problem:
```python
def sort_priority2(values, group):
    found = False
    def helper(x):
        if x in group:
            found = True
            return (0, x)
        return (1, x)
    values.sort(key=helper)
    return found

found = sort_priority2(numbers, group)
print('Found:', found)
print(numbers)
```
    >>>
    Found: False
    [2, 3, 5, 7, 1, 4, 6, 8]

Function is not working. This happens because variable assignment does not go outside of the helper's scope. 

    Python scans for references in following order"

    1. The current function's scope.
    2. Any enclosing scopes (such as other containing functions).
    3. The scope of the module that contains the code (aka *Global scope*).
    4. The built-in scope (that contains functions line `len()` and `str()`).

    If it cant find it in this places, `NameError` exception will be raised.

* To get date out of a closure, `nonlocal` syntax can be used:
```python
def sort_priority3(values, group):
    found = False
    def helper(x):
        nonlocal found
        if x in group:
            found = True
            return (0, x)
        return (1, x)
    values.sort(key=helper)
    return found


found = sort_priority3(numbers, group)
print('Found:', found)
print(numbers)
```
    >>>
    True
    [2, 3, 5, 7, 1, 4, 6, 8]

However, you should be careful with `global` and `nonlocal` statements and use them in relatively small functions only. 

If it is getting complicated, better to use wrapper class:
```python
class Sorter:
    def __init__(self, group):
        self.group = group
        self.found = False
    def __call__(self, x):
        if x in self.group:
            self.found = True
            return (0, x)
        return (1, x)

sorter = Sorter(group)
numbers.sort(key=sorter)
assert sorter.found is True
```
## Item 22: Reduce Visual Noise with Variable Positional Argument
Positional arguments in functions may reduce visual noise and increase readability. Positional arguments are often called `varargs` or `star args` (because of the way they are declared `*args`).

* With fixed number of parameters you can have a function like this:
```python
def log(message, values):
    if not values:
        print(message)
    else:
        values_str = ", ".join(str(x) for x in values)
        print(f"{message}: {values_str}")

log("My numbers are", [1, 2])
log("Hi there", [])
```
    >>>
    My numbers are: 1, 2
    Hi there

As you can see, call with empty list does not look great. You can avoid it with prefixing optional arguments with `*`:
```python
def log(message, *values): # The only change
    if not values:
        print(message)
    else:
        values_str = ", ".join(str(x) for x in values)
        print(f"{message}: {values_str}") 

log("My numbers are", [1, 2])
log("Hi there") # And a function call is changed.
```
    >>>
    My numbers are: 1, 2
    Hi there

* A sequence can be passed to the function call using `*` operator:
```python
favorites = [7, 33, 99]
log('Favorite colors', *favorites)
```
    >>>
    Favorite colors: 7, 33, 99

* There are two problems with accepting variable number of positional arguments. 
1. Optional positional arguments are always turned into `tuple`. This mean if a generator function is called with `*` argument it will be iterated until its over, which can eat a lot of memory and result in crush:
```python
def my_generator():
    for i in range(10**100):
        yield i

def my_func(*args):
    print(args)

it = my_generator()
my_func(*it)
```
`*args` parameters are good in situation when you now the number of arguments and it is a relatively small number. 

2. Second problem is: you cannot add new positional arguments in the future without breaking old calls (backward incompatible):
```python
def log(sequence, message, *values):
    if not values:
        print(f"{sequence} - {message}")
    else:
        values_str = ", ".join(str(x) for x in values)
        print(f"{sequence} - {message}: {values_str}")

log(1, 'Favorites', 7, 33)          # RIGHT New call
log(1, 'Hi there')                  # RIGHT New call
log('Favorite numbers', 7, 33)      # WRONG Old usage breaks
```
    >>>
    1 - Favorites: 7, 33
    1 - Hi there
    Favorite numbers - 7: 33

This kind of bugs are hurd to track down because function runs without exception. To avoide this, you can add new functionality by using keyword-only arguments or, even more robust, use type annotation. 

## item 23: Provide Optional Behavior with Keyword Arguments
In Python argument to a function call maybe positional or keyword. You may use keyword-only arguments in any order in the call:
```python
def remainder(number, divisor):
    return number % divisor

remainder(20, 7)
remainder(20, divisor=7)
remainder(number=20, divisor=7)
remainder(divisor=7, number=20)
```

* Positional arguments should be passed before keyword arguments:
```python
remainder(number=20, 7)
```
    >>>
    Traceback ...
    SyntaxError: positional argument follows keyword argument

* And, each argument can be specified only once:
```python
remainder(20, number=7)
```
    >>>
    Traceback ...
    TypeError: remainder() got multiple values for argument 'number'

* If you have a `dict` and want to have it content to pass as function call - you can use `**` and keys of the `dict` will be used as the keyword argument names and values as a arguments:
```python
my_kwargs = {
    'number': 20,
    'divisor': 7,
}
remainder(**my_kwargs)
```
    >>>
    6
* This cool feature can be used with two(2) dictionaries if they don't have same keys:
```python
my_kwargs = {
    "number": 20,
}
other_kwargs = {
    "divisor": 7,
}
reminder(**my_kwargs, ^^other_kwargs)
```
    >>>
    6

* If you want function to catch all the named arguments, you can use `**kwargs` as well:
```python
def print_parameters(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} = {value}")

print_parameters(alpha=1.5, beta=9, gamma=4)
```
    >>>
    alpha = 1.5
    beta = 9
    gamma = 4

Keyword arguments provides three significant benefits:
1. First benefit is that it is always clearer to the new caller of the function which argument is which, without locking in to the implementation.
2. Second is that you can assign default values to the argument, thus provide additional functionality. 
    For instance, let's look at the function computing the rate of the fluid going into the vat:

```python
def flow_rate(weight_diff, time_diff):
    return weight_diff / time_diff

weight_diff = 0.5
time_diff = 3

flow = flow_rate(weight_diff, time_diff)
print(f"{flow:.3}, kg per second")
``` 
    >>>
    0.167 kg per second

Now, let's say you need to add a functionality to change a period from second to hours or more. We can do it by adding new `period` argument. But we dint want to specified it each call. We want the function to compute rate at per second by default and only, if needed, change the period. We can achieve this by using `default` value for the `argument`:
```python
def flow_rate(weight_diff, time_diff, period=1):
    return (weight_diff / time_diff) * period


flow_per_second = flow_rate(weight_diff, time_diff)
flow_per_hour = flow_rate(weight_diff, time_diff, period=3600)

print(f"{flow_per_second:.3} kg per second")
print(f"{flow_per_hour} kg per hour")
```
    >>>
    0.167 kg per second
    600.0 kg per hour

3. Third reason is that keyword arguments provide you with the way to add functionality without breaking backward compatibility. This mean you can add functionality without big changes in existing code base. 

Here, we will add new functionality `units_per_kg` to the function:
```python
def flow_rate(weight_diff, time_diff, period=1, units_per_kg=1):
    return ((weight_diff * units_per_kg)/ time_diff) * period

pounds_per_hour = flow_rate(weight_diff, time_diff, period=3600, units_per_kg=2.2)
print(f"{pounds_per_hour} pounds per hour")
```
    >>>
    1320.0 pounds per hour

The only problem with this approach is that keyword argument can also be called using its position. Following call will work:
```python
pounds_per_hour = flow_rate(weight_diff, time_diff, 3600, 2.2)
```

# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
