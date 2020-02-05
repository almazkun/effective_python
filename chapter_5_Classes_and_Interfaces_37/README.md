# Chapter 5. Classes and Interfaces
Python is object-oriented language and supports full range of features, such as inheritance, polymorphism and encapsulation.

## Item 37: Compose Classes Instead of Nesting Many Levels of Built-in Types
Python's built-in dictionary type `dict` is wonderful for maintaining dynamic internal state over lifetime of a object. Dynamic means that we need to store an unexpected set if identifiers. 

For example, we need to store grade of the students, with names aren't known in advance. We will define a new class for that:
```python
class SimpleGradebook:
    def __init__(self):
        self._grades = {}
    def add_student(self, name):
        self._grades[name] = []
    def report_grade(self, name, score):
        self._grades[name].append(score)
    def average_grade(self, name):
        grades = self._grades[name]
        return sum(grades) / len(grades)


book = SimpleGradebook()
book.add_student("Isaac Newton")
book.report_grade("Isaac Newton", 90)
book.report_grade("Isaac Newton", 95)
book.report_grade("Isaac Newton", 85)

print(book.average_grade("Isaac Newton"))
```
    >>>
    90.0









# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
