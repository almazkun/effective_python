# Chapter 3. Functions

## Item 19: Never Unpack More Than Three Variables When Function Return Multiple Values

* Unpacking allow seemingly return more than one value:
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

* Now, imagine you have to need to show also min, max, avg, median and total population. It can be dome by extending our previous function:
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

But, this approach has two main problems. First, all the return values are numeric and it is easy to reorder them accidentals and not to notice that. Which, will lead to the hard-to-find bugs in the future. Second, is that line of unpacking of the values is to long and, according to the PEP 8, it should be divided into more lines. Which will hurt readability. 

To avoid this problem you should never use more than tree(3) variables when unpacking multiple return values from a function. Instead, maybe used small class or `namedtuple`.

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

* This approach can be extended using `type annotation` and `docstring`:
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


# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
