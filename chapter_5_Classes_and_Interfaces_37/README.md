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
There are many approaches to refactoring. Here we can start at the bottom of the dependency tree: a single grade.









# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
