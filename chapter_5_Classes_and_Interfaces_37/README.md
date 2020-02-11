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
Dictionaries and other built-ins are so easy to use and it is very tempting to over extend them to write a brittle code. For example, we need to extend the SimpleGradebook class to also store a grades. We can do it by changing the `_grades` dictionary, to hold as a value inner dictionary with key as a subject and a value as a list of grades:
```python
from collections import defaultdict


class BySubjectGradebook:
    def __init__(self):
        self._grades = {}                       # Outer dict
    def add_student(self, name):
        self._grades[name] = defaultdict(list)  # Inner dict
```
Methods, however, grew quiet complex to handle new functionality, but it is ok:
```python
    def report_grade(self, name, subject, grade):
        by_subject = self._grades[name]
        grade_list = by_subject[subject]
        grade_list.append(grade)
    def average_grade(self, name):
        by_subject = self._grades[name]
        total, count = 0, 0
        for grades in by_subject.values():
            total += sum(grades)
            count += len(grades)
        return total / count

book = BySubjectGradebook()
book.add_student("Albert Einstein")
book.report_grade("Albert Einstein", "Math", 75)
book.report_grade("Albert Einstein", "Math", 65)
book.report_grade("Albert Einstein", "Gym", 90)
book.report_grade("Albert Einstein", "Gyn", 95)
print(book.average_grade("Albert Einstein"))
```
    >>>
    81.25
Now, imagine, we need to store weight of each score toward the overall grade in the class so that midterm and final exams are more important than other grades. We can do that by changing the innermost list to hold tuple of score and weight. 
```python
class WeightedGradebook:
    def __init__(self):
        self._grades = {}
    def add_student(self, name):
        self._grades[name] = defaultdict(list)
    def report_grade(self, name, subject, score, weight):
        by_subject = self._grades[name]
        grade_list = by_subject[subject]
        grade_list.append((score, weight))
```
Now, even that the `report_grade` method is change a little, the `average_grade` become more complicated:
```python
    def average_grade(self, name):
        by_subject = self._grades[name]
        score_sum, score_count = 0, 0
        for subject, scores in by_subject.items():
            subject_avg, total_weight = 0, 0
            for score, weight in scores:
                subject_avg += score * weight
                total_weight += weight
            score_sum += subject_avg / total_weight
            score_count += 1
        return score_sum / score_count

book = WeightedGradebook()
book.add_student("Albert Einstein")
book.report_grade("Albert Einstein", "Math", 75, 0.05)
book.report_grade("Albert Einstein", "Math", 65, 0.15)
book.report_grade("Albert Einstein", "Math", 70, 0.80)
book.report_grade("Albert Einstein", "Gym", 100, 0.40)
book.report_grade("Albert Einstein", "Gym", 85, 0.60)
print(book.average_grade("Albert Einstein"))
```
    >>>
    80.25
It is hard to read and understand. If you come across complexity tike this, using and nesting (more than one level deep (like it is done here(in this sentence(I mean)))) multiple built-ins together, it is a sight that you should move to a hierarchy of classes.

As soon as your that your bookkeeping becomes complicated, break it all into classes. Then it is possible to provide clear interfaces that better encapsulates your data. This also enables you to create a layer of abstraction between your interfaces and your concrete implementations.

### Refactoring to Classes
There are many approaches to refactoring. 

Here we can start at the bottom of the dependency tree: a single grade. We used `tuple` to store `(score, weight)`:
```python
grades = []
grades.append((95, 0.45))
grades.append((85, 0.55))
total = sum(score * weight for score, weight in grades)
total_weight = sum(weight for _, weight in grades)
average_grade = total / total_weight
print(average_grade)
```
Underscore `_` variable name is used for unused variable.

The problem with this code is that `tuple` instances are positional, which mean if we will need to store more information regarding grades, such us teachers comments, wi will need to rewrite our calculations with more `_`:
```python
grades = []
grades.append((95, 0.45, "Great job"))
grades.append((85, 0.55, "Better next time"))
total = sum(score * weight for score, weight, _ in grades)
total_weight = sum(weight for _, weight, _ in grades)
average_grade = total / total_weight
print(average_grade)
```
To avoid this we can use `namedtuple` form `collections` built-in.
```python
from collections import namedtuple


Grade = namedtuple("Grade", ("score", "weight"))
```
These classes can be constructed using positional or keyword arguments. 
    
    ***Limitations of `namedtuple`***
    
    * You can't define a default argument values for `namedtuple` classes.
    * The attribute values are still accessible using numerical indexes.
    
Next, we cal create a class representing a single object containing set of grades:
```python
class Subject:
    def __init__(self):
        self._grades = []
    def report_grade(self, score, weight):
        self._grades.append(Grade(score, weight))
    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
            total_weight += grade.weight
        return total / total_weight
```
Then, we can create a class to hold all the subjects that can be studied be a student:
```python
class Student:
    def __init__(self):
        self._subjects = defaultdict(Subject)
    def get_subject(self, name):
        return self._subjects[name]
    def average_grade(self):
        total, count = 0, 0 
        for subject in self._subjects.values():
            total += subject.average_grade()
            count += 1
        return total / count
```
Finally, we write a container for all students:
```python
class Gradebook:
    def __init__(self):
        self._students = defaultdict(Student)
    def get_student(self, name):
        return self._students[name]
```
Even though, this example is twice as long as the previous implementation, it is much easier to read and work with:
```python
book = Gradebook()
albert = book.get_student('Albert Einstein')
math = albert.get_subject('Math')
math.report_grade(75, 0.05)
math.report_grade(65, 0.15)
math.report_grade(70, 0.80)
gym = albert.get_subject('Gym')
gym.report_grade(100, 0.40)
gym.report_grade(85, 0.60)
print(albert.average_grade())
```
    >>>
    80.25

## Item 38: Accept Functions Instead of Classes for Simple Interfaces
Many Python's built-in can accept function as a parameter's value. Like in `list`'s `sort` method:
```python
names = ['Socrates', 'Archimedes', 'Plato', 'Aristotle']
names.sort(key=len)
print(names)
```
    >>>
    ['Plato', 'Socrates', 'Aristotle', 'Archimedes']

This is possible because functions in Python are `first class` objects: they can be passed around and reference like any other value.

For example, we want to customize the behavior of the `defaultdict` class. Now it will print out a message each time missing key was called:
```python 
from collections import defaultdict

def log_missing():
    print("Key added")
    return 0

current = {"green": 12, "blue": 3}
increment = [
    ("red", 5),
    ("blue", 17),
    ("orange", 9),
]
result = defaultdict(log_missing, current)
print(f"Before: {dict(result)}")

for key, amount in increment:
    result[key] += amount

print(f"After: {dict(result)}")
```
    >>>
    Before: {'green': 12, 'blue': 3}
    Key added
    Key added
    After: {'green': 12, 'blue': 20, 'red': 5, 'orange': 9}












# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
