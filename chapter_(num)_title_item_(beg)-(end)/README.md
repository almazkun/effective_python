# Chapter (NUM). (TITLE)

## Item (NUM): (TITLE)

Some message to remember

> python (code prime example)


## item (NUM+1): {TITLE.next())

#### Whitespace matters

> * Use 4 [spaces]
> * no more than 79 lines in 
> * 
> * 
> * 
> * 
> * 

#### Naming

#### Expressions and Statements

```python
def bubble_sort(a):
    for _ in range(len(a)):
        for i in range(1, len(a)):
            if a[i] < a[i-1]:
                print(a, a[i], a[i-1])
                a[i-1], a[i] = a[i], a[i-1] # Swap

names = ["pretzels", "carrots", "arugula", "bacon"]
bubble_sort(names)
print(names)

```

    >>>
    ['arugula', 'bacon', 'carrots', 'pretzels']






* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
