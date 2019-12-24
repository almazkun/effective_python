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


# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
