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
increments = [
    ("red", 5),
    ("blue", 17),
    ("orange", 9),
]
result = defaultdict(log_missing, current)
print(f"Before: {dict(result)}")

for key, amount in increments:
    result[key] += amount

print(f"After: {dict(result)}")
```
    >>>
    Before: {'green': 12, 'blue': 3}
    Key added
    Key added
    After: {'green': 12, 'blue': 20, 'red': 5, 'orange': 9}

Using such functions also makes tasting easier. For example, if we want to count missing values, we may achieve this by using closure:
```python
def increment_with_report(current, increments):
    added_count = 0
    def missing():
        nonlocal added_count
        added_count += 1
        return 0
    result = defaultdict(missing, current)
    for key, amount in increments:
        result[key] += amount
    return result, added_count

result, count = increment_with_report(current, increments)
assert count == 2
```
This also can be done by storing state in class rather than in closure:
```python
class CountMissing:
    def __init__(self):
        self.added = 0
    def missing(self):
        self.added += 1
        return 0

counter = CountMissing()
result = defaultdict(counter.missing, current) # Method ref
for key, amount in increments:
    result[key] += amount

assert counter.added == 2
```
It works well, but it is not clear for new reader what is the purpose of this helper class. 

To clarify this situation Python has `__call__` method. This method allows an object to called like a regular function. All objects that can be executed in this manner are called *callables*:
```python
class BetterCountMissing:
    def __init__(self):
        self.added = 0
    def __call__(self):
        self.added += 1
        return 0

counter = BetterCountMissing()
assert counter() == 0
assert callable(counter)

result = defaultdict(counter, current) # Relies on __call__
for key, amount in increments:
    result[key] += amount

assert counter.added == 2
```

## Item 39: Use `@classmethod` Polymorphism to Construct Objects Generically

In Python, not only objects support polymorphism, but classes do as well. 

Polymorphism enables hierarchy of classes to implement their own unique versions of a method. THis mean that many classes can fulfill the same interface of abstract base class while providing different functionality.

For example, let's implement MapReduce functionality with a common class to represent a input date. Here is a such class with `read` method, which needs to be implemented by subclass:
```python
class InputData:
    def read(self):
        raise NotImplementedError
```
Here is a subclass of `InputData` which reads data from a file on disk:
```python
class PathInputData(InputData):
    def __init__(self, path):
        super().__init__()
        self.path = path
    def read(self):
        with open(self.path) as f:
            return f.read()
```
It is possible to have any number of subclasses, with each of them implementing their own version of `read` method.

Now, we want a MapReduce worker that consumes the input data in a standard way:
```python
class Worker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None
    def map(self):
        raise NotImplementedError
    def reduce(self, other):
        raise NotImplementedError
```
After that, we define a subclass of `Worker` to implement a specific MapReduce function - a simple new line counter:
```python
class LineCountWorker(Worker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count("\n")
    def reduce(self, other):
        self.result += other.result
```
It looks like th implementation is doing great. But we have come upon the biggest hurdle of all. What connects all of these peaces together?

The simplest approach is to manually build and connect the objects with some helper functions. Let's start with listing all files in directory and constructing a `PathInputData` instance for each file:
```python
import os


def generate_inputs(data_dir):
    for name in os.listdir(data_dir):
        yield PathInputData(os.path.join(data_dir, name))
```
Now, we need to create `LineCountWorker` instance by using `InputData` instance:
```python
def create_workers(input_list):
    workers = []
    for input_data in input_list:
        workers.append(LineCountWorker(input_data))
    return workers
```
We execute `Worker` instance by fanning out the `map` step in multiple threads. Then call `reduce` repeatedly to combine the results into one final value:
```python
from threading import Thread


def execute(workers):
    threads = [Thread(target=w.map) for w in workers]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    first, *rest = workers
    for worker in rest:
        first.reduce(worker)
    return first.result
```
Finally, we connect of the peaces in a function to run each step:
```python
def mapreduce(data_dir):
    inputs = generate_inputs(data_dir)
    workers = create_workers(inputs)
    return execute(workers)
```
Let' test how it works:
```python
import os
import random


def write_test_files(tmpdir):
    os.makedirs(tmpdir)
    for i in range(100):
        with open(os.path.join(tmpdir, str(i)), "w") as f:
            f.write("\n" * random.randint(0,100))

tmpdir = "test_inputs"
write_test_files(tmpdir)

result = mapreduce(tmpdir)
print(f"There are {result} lines")
```
    >>>
    There are 4600 lines
It works! But there is a huge problem, that is `mapreduce` function is not generic at all. If we would need to write another `InputData` or `Worker` we would need to rewrite `generate_inputs`, `create_workers` and `mapreduce` functions!

This problem boils down to the need of a generic way to construct an object. The best way to solve this problem is to use `class method` polymorphism. 

Let's apply this idea to the MapReduce classes. We will extend `InputData` class with a generic `@classmethod` to create new `InputData`:
```python
class GenericInputData:
    def read(self):
        raise NotImplementedError
    @classmethod
    def generate_inputs(cls, config):
        raise NotImplementedError
```
We put a set of configuration parameters that the `GenericInputData` subclass need to interpret:
```python
class PathInputData(GenericInputData):
    def __init__(self, path):
        super().__init__()
        self.path = path
    def read(self):
        with open(self.path) as f:
            return f.read()
    @classmethod
    def generate_inputs(cls, config):
        data_dir = config["data_dir"]
        for name in os.listdir(data_dir):
            yield cls(os.path.join(data_dir, name))
```
Similarly, we can make `create_worker` helper part of the `GenericWorker` class. Here we use `input_class` parameter, which should be a subclass of the `GenericInputData`:
```python
class GenericWorker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None
    def map(self):
        raise NotImplementedError
    def reduce(self, other):
        raise NotImplementedError
    @classmethod
    def create_worker(cls, input_class, config):
        workers = []
        for input_data in input_class.generate_inputs(config):
            workers.append(cls(input_data))
        return workers
```
Note that the call to `input_class.generate_inputs` in the class polymorphism that we are truing to achieve. Here `create_worker` calling `cls()` is a alternative way to construct `GenericWorkers` object.
The effect of my concrete `GenericWorker` subclass is nothing more than changing its parent class:
```python
class LineCountWorker(GenericWorker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count("\n")
    def reduce(self, other):
        self.result += other.result
```
Rewriting the `mapreduce` function to the completely generic form:
```python
def mapreduce(worker_class, input_class, config):
    workers = worker_class.create_worker(input_class, config)
    return execute(workers)
```
Running the new worker produces the same result:
```python
config = {"data_dir": tmpdir}
result = mapreduce(LineCountWorker, PathInputData, config)
print(f"There are {result} lines")
```
    >>>
    There are 4600 lines
We can write other `GenericInputData` and `GenericWorker` subclass, without rewriting any glue code.

## Item 40: Initialize Parent classes with `super`
The old to initialize parent class from a child class is to call parent's `__init__` method in child instance:
```python
class MyBaseClass:
    def __init__(self, value):
        self.value = value


class MyChildClass(MyBaseClass):
    def __init__(self):
        MyBaseClass.__init__(self, 5)
```
This approach works in simple cases but brakes in cases with complicated inheritance. 

If class is affected with multiple inheritance calling the superclasses' `__init__` method directly can lead to unexpected behavior:

One problem is that the `__init__` call order isn't specific across all subclasses. For example, here is two classes with `value` field:
```python
class TimesTwo:
    def __init__(self):
        self.value *= 2


class PlusFive:
    def __init__(self):
        self.value += 5
```
This class define its parents ordering in one way:
```python
class OneWay(MyBaseClass, TimesTwo, PlusFive):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)
```
And constructing it produces a result that matches the parent class ordering:
```python
foo = OneWay(5)
print(f"First ordering value is (5 * 2) + 5 = {foo.value}")
```
    >>>
    First ordering value is (5 * 2) + 5 = 15

Here is another class ordering it parents differently(`PlusFive`- first, `TimesTwo` - second):
```python
class AnotherWay(MyBaseClass, PlusFive, TimesTwo):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)
```
However, we lest the calls to the parent class constructor - `PlusFive.__init__` and `TimesTwo.__init__` - in the same order as before, which mean this class behavior doesn't match the order of the parent classes in its definition. THis types of conflict is hard to spot and it is especially difficult for new readers to understand:
```python
bar = AnotherWay(5)
print(f"Second ordering value is {bar.value}")
```
    >>>
    Second ordering value is 15

Another problem occurs with `Diamond inheritance`. Diamond inheritance happens when a subclass inherits from two separate classes that have the same superclass somewhere in the hierarchy. Diamond inheritance cause the common superclass's `__init__` method to run multiple times, causing unexpected behavior:
```python
class TimesSeven(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value *= 7


class PlusNine(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value += 9
```
Then we define a child class which inherits from both of these classes, making `MyBaseClass` the top of the diamond:
```python
class ThisWay(TimesSeven, PlusNine):
    def __init__(self, value):
        TimesSeven.__init__(self, value)
        PlusNine.__init__(self, value)

foo = ThisWay(5)
print(f"Should be (5 * 7) + 9 = 44 but is {foo.value}.")
```
    >>>
    Should be (5 * 7) + 9 = 44 but is 14.

The call to the second patent class's constructor, `PlusNine.__init__`, causes `self.value` to be reset to `5` again when `MyBaseClass.__init__` get called a second time. The result of a calculation is completely ignoring `TimesSeven.__init__` constructor. This behavior is surprising and very hard to debug in more complex cases.

Python have the `super` built-in function and standard method resolution order (MRO). `super` ensures that the common superclasses in diamond hierarchies are run only once. MRO ordering follows `C3 lineariztion` algorithm.

Let's try to use this `super` function:
```python
class TimesSevenCorrect(MyBaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value *= 7


class PlusNineCorrect(MyBaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value += 9
```
Now `super` ensures that `MyBaseClass.__init__` is run only once and the order in which parent classes are run is defined in `class` statement:
```python
class GoodWay(TimesSevenCorrect, PlusNineCorrect):
    def __init__(self, value):
        super().__init__(value)


foo = GoodWay(5)
print(f"Should be 7 * (5 + 9) = 98 but is {foo.value}")
```
    >>>
    Should be 7 * (5 + 9) = 98 but is 98

THis seems backwards at first. Let's see what is happening. You can check the order by calling `mro`:
```python
mro_str = "\n".join(repr(cls) for cls in GoodWay.mro())
print(mro_str)
```
    >>>
    <class '__main__.GoodWay'>
    <class '__main__.TimesSevenCorrect'>
    <class '__main__.PlusNineCorrect'>
    <class '__main__.MyBaseClass'>
    <class 'object'>

So, we we call `GoodWay(5)`, it calls `TimesSevenCorrect.__init__`, which calls `PlusNineCorrect.__init__`. which calls `MyBaseClass.__init__`. After reaching the top of the Diamond, all of the initialization methods actually do their job in opposite order. `MyBaseClass.__init__` assigns `5` to `value`. `PlusNineCorrect.__init__` adds `9` to make value total `14`. `TimesSeven.__init__` multiplies by `7` to make it `98`.

Besides, making multiple inheritance robust, the call `super().__init__` is also much more maintainable. Later we can rename the `MyBaseClass` or have `TimesSevenCorrect` and `PlusNineCorrect` inherit from different superclass without having to update their `__init__` methods to match.

`super` also can be called with two parameters:
1. The type os class whose MRO parent view you're trying to access;
2. The instance on which to access that view.

Using this two optional parameters in the constructor looks like this:
```python
class ExplicitTrisect(MyBaseClass):
    def __init__(self, value):
        super(ExplicitTrisect, self).__init__(value)
        self.value /= 3
```
However, this parameters are not required for `object` instance initialization.
```python
class AutomaticTrisect(MyBaseClass):
    def __init__(self, value):
        super(__class__, self).__init__(value)
        self.value /= 3


class ImplicitTrisect(MyBaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value /= 3


assert ExplicitTrisect(9).value == 3
assert AutomaticTrisect(9).value == 3
assert ImplicitTrisect(9).value == 3
```

## Item 41: Consider Composing Functionality with Mix-in classes
It is better to avoid multiple inheritance.

Consider writing mix-ins instead of multiple inheritance.

*Mix-in is a class that defines only a small set of additional methods for its child classes to provide. Mix-in classes don't define their own instance attributes not require their `__init__` constructor to be called.*

Mix-ins are easy to write and they can be composed and layered to minimize repetitive code and maximize reuse. 

For example, we want to have a functionality to convert in-memory Python object to serializable dict representation. Here is a mix-in to accomplish that:
```python
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)
    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output
    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, "__dict__"):
            return self._traverse_dict(value.__dict__)
        else:
            return value
```
Here, is a class which make a dictionary representation of a binary tree using our mix-in:
```python
class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


tree = BinaryTree(10, left=BinaryTree(7, right=BinaryTree(9)),
                    right=BinaryTree(13, left=BinaryTree(11)))
print(tree.to_dict())
```
    >>>
    {'value': 10, 
    'left': {'value': 7,
            'left': None,
            'right': 
                    {'value': 9, 
                    'left': None, 
                    'right': None}}, 
    'right': 
            {'value': 13, 
            'left': 
                {'value': 11, 
                'left': None, 
                'right': None}, 
            'right': None}}

Behavior of mix-in can be easily overridden when required. For example, here is a subclass of `BinaryTree` that holds a reference to the parent. This circular reference would cause the default implementation of `ToDictMixin.to_dict` to loop forever:
```python
class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None, right=None, parent=None):
        super().__init__(value, left=left, right=right)
        self.parent = parent
    def _traverse(self, key, value):
        if isinstance(value, BinaryTreeWithParent) and key == "parent":
            return value.value # Prevent cycling
        else:
            return super()._traverse(key, value)
```
We have overridden `_traverse` method, which now is inserting the parent's numerical value and otherwise defers to the mix-ins default implementation by calling `super` built-in.

Calling `BinaryTreeWithParent.to_dict` works fine now:
```python
root = BinaryTreeWithParent(10)
root.left = BinaryTreeWithParent(7, parent=root)
root.left.right = BinaryTreeWithParent(9, parent=root.left)
print(root.to_dict())
```
    >>>
    {'value': 10, 
    'left': 
        {'value': 7, 
        'left': None, 
        'right': {'value': 9, 
                'left': None, 
                'right': None, 
                'parent': 7}, 
        'parent': 10}, 
    'right': None, 
    'parent': None

By defining `BinaryTreeWithParent._traverse`, also enabled any class that has an attribute `BinaryTreeWithParent` to automatically work with the `ToDoMixin`:
```python
class NamedSubTree(ToDictMixin):
    def __init__(self, name, tree_with_parent):
        self.name = name
        self.tree_with_parent = tree_with_parent


my_tree = NamedSubTree("foobar", root.left.right)
print(my_tree.to_dict())
```
    >>>
    {'name': 'foobar', 
    'tree_with_parent': {'value': 9, 
                        'left': None, 
                        'right': None, 
                        'parent': 7}}

Mix-ins can also be composed together. For example, we need a mix-in that provides JSON serialization for any class:
```python
import json


class JsonMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)
    def to_json(self):
        return json.dumps(self.to_dict())
```
Note how the `JsonMixin` defines both instance and class methods. And here is how it could be used:
```python
class DatacenterRack(ToDictMixin, JsonMixin):
    def __init__(self, switch=None, machines=None):
        self.switch = Switch(**switch)
        self.machines = [
            Machine(**kwargs) for kwargs in machines]


class Switch(ToDictMixin, JsonMixin):
    def __init__(self, ports=None, speed=None):
        self.ports = ports
        self.speed = speed


class Machine(ToDictMixin, JsonMixin):
    def __init__(self, cores=None, ram=None, disk=None):
        self.cores = cores
        self.ram = ram
        self.disk = disk


serialized = """{
"switch": {"ports": 5, "speed": 1e9},
"machines": [
{"cores": 8, "ram": 32e9, "disk": 5e12},
{"cores": 4, "ram": 16e9, "disk": 1e12},
{"cores": 2, "ram": 4e9, "disk": 500e9}
]
}"""

deserialized = DatacenterRack.from_json(serialized)
roundtrip = deserialized.to_json()
assert json.loads(serialized) == json.loads(roundtrip)
```

## Item 42: Prefer Public Attributes over Private ones
In Python there are only *public* or *private* class attributes:
```python
class MyObject:
    def __init__(self):
        self.public_field = 5
        self.__private_field = 10
    def get_private_field(self):
        return self.__private_field
```
Public attributes can be accessed directly:
```python
foo = MyObject()
assert foo.public_field == 5
```
Private attributes are with names started with double underscores `__` and can be accessed through class's methods:
```python
assert foo.get_private_field() == 10
```
But cannot be accessed directly:
```python
foo.__private_field
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'MyObject' object has no attribute '__private_field'
Class methods also have access to the private attributes of the same class:
```python
class MyOtherObject:
    def __init__(self):
        self.__private_field = 71 
    @classmethod
    def get_private_field_of_instance(cls, instance):
        return instance.__private_field

bar = MyOtherObject()
assert MyOtherObject.get_private_field_of_instance(bar) == 71
```
Subclasses cannot access parent's private fields:
```python
class MyParentObject:
    def __init__(self):
        self.__private_field = 71

class MyChildObject(MyParentObject):
    def get_private_field(self):
        return self.__private_field

baz = MyChildObject()
baz.get_private_field()
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 3, in get_private_field
    AttributeError: 'MyChildObject' object has no attribute '_MyChildObject__private_field'

However, the private attributes are implemented by simply transforming a attribute name. Because the field is defined in `MyParentObject.__init__` it is named `MyParentObject.__private_field`. THis is why subclass method cannot access it, Python is looking for `MyChildObject.__private_field`. 

So, knowing that, it is possible to access private attributes of any class from outside easily:
```python
assert baz._MyParentObject__private_field == 71
```
We can look it up the following way:
```python
print(baz.__dict__)
```
    >>>
    {'_MyParentObject__private_field': 71}

That being said, it is better not to use private attributes when you want them to be hidden from outer world:
```python
class MyStringClass:
    def __init__(self, value):
        self.__value = value
    def get_value(self):
        return str(self.__value)

foo = MyStringClass(5)
assert foo.get_value() == "5"
```
This is wrong approach, one of the down sides is that if latter you decide to extend or subclass this class, it will make it more prone to errors and bags and just harder to write.
```python
class MyIntegerSubclass(MyStringClass):
    def get_value(self):
        return int(self._MyStringClass__value)

foo = MyIntegerSubclass("5")
assert foo.get_value() == 5
```
In this case, if the class hierarchy changes, this classes will break:
```python
class MyBaseClass:
    def __init__(self, value):
        self.__value = value
    def get_value(self):
        return self.__value

class MyStringClass(MyBaseClass):
    def get_value(self):
        return str(super().get_value()) # Updated

class MyIntegerSubclass(MyStringClass):
    def get_value(self):
        return int(self._MyStringClass__value) # Not updated


foo = MyIntegerSubclass("5")
foo.get_value
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 3, in get_value
    AttributeError: 'MyIntegerSubclass' object has no attribute '_MyStringClass__value'

In general, it is better to document each protected field and explain why:
```python
class MyStringClass:
    def __init__(self):
        # This stores the user-supplied value for the object.
        # It should be coercible to a string. Once assigned in
        # the object it should be treated as immutable.
        self.value = value
...
```
The only time when you should seriously consider private attributes is when your worried about naming conflicts with subclasses. It happens when of the child's attribute is the same:
```python
class ApiClass:
    def __init__(self):
        self._value = 5
    def get(self):
        return self._value

class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = "hello"

a = Child()
print(f"{a.get()} and {a._value} should be different")
```
    >>>
    hello and hello should be different

This kind of problem are especially common in public APIs with common names (like `value`). In this situations you should use private attributes:
```python
class ApiClass:
    def __init__(self):
        self.__value = 5        # Double underscore
    def get(self):
        return self.__value     # Double underscore

class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = "hello"   # OK!

a = Child()
print(f"{a.get()} and {a._value} should be different")
```

## Item 43: Inherit from `collections.abc` for Custom Container Types
Much of the programming in Python is defining classes that in one way or another stores some data and describes its relations to other objects. Every Python class is a container of some kind, encapsulating attributes and functionality together. Python provides built-in container types: lists, tuples, sets and dictionaries. 

* You can subclass a built-in `list` type with some additional methods for counting the frequency of its members:
```python
class FrequencyList(list):
    def __init__(self, members):
        super().__init__(members)
    def frequency(self):
        counts = {}
        for item in self:
            counts[item] = counts.get(item, 0) + 1
        return counts
```
By subclassing `list` we get all the functionality and methods of it and have our own new method. 
```python
foo = FrequencyList(["a", "b", "a", "c", "b", "a", "d"])
print(f"Length is {len(foo)}")

foo.pop()
print(f"After pop: {repr(foo)}")
print(f"Frequency: {foo.frequency()}")
```
    >>>
    Length is 7
    After pop: ['a', 'b', 'a', 'c', 'b', 'a']
    Frequency: {'a': 3, 'b': 2, 'c': 1}

* Now imagine, we need an object like `list` that allows indexing but isn't `list` subclass. For example, in this binary tree:
```python
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```
How to make this class a sequence type? Python implement this type of behavior by calling `__getitem__`:
```python
bar = [1, 2, 3]
bar[0]
```
This mean Python will call:
```python
bar.__getitem__(0)
```
To make our class a sequence we can define this method in a subclass:
```python
class IndexableNode(BinaryNode):
    def _traverse(self):
        if self.left is not None:
            yield from self.left._traverse()
        yield self
        if self.right is not None:
            yield from self.right._traverse()
    def __getitem__(self, index):
        for i, item in enumerate(self._traverse()):
            if i == index:
                return item.value
        raise IndexError(f"Index {index} is out of range")

tree = IndexableNode(10, 
                    left=IndexableNode(
                        5, 
                        left=IndexableNode(2), 
                        right=IndexableNode(
                            6, 
                            right=IndexableNode(7))),
                    right=IndexableNode(
                        15, left=IndexableNode(11)))

print(f"LRR is {tree.left.right.right.value}")
print(f"Index 0 is {tree[0]}")
print(f"Index 1 is {tree[1]}")
print(f"11 is in tree? {11 in tree}")
print(f"17 is in tree? {17 in tree}")
print(f"Tree is {list(tree)}")
```
    >>>
    LRR is 7
    Index 0 is 2
    Index 1 is 5
    11 is in tree? True
    17 is in tree? False
    Tree is [2, 5, 6, 7, 10, 11, 15]

The problem is, `__getitem__` alone does not implement other methods of a `list` type. The `len()` method needs to be implemented as well:
```python
len(tree)
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: object of type 'IndexableNode' has no len()

Implementation on `__len__` method:
```python
class SequenceNode(IndexableNode):
    def __len__(self):
        for count, _ in enumerate(self._traverse(), 1):
            pass
        return count

tree = SequenceNode(10, 
                    left=SequenceNode(
                        5, 
                        left=SequenceNode(2), 
                        right=SequenceNode(
                            6, 
                            right=SequenceNode(7))),
                    right=SequenceNode(
                        15, left=SequenceNode(11)))

print(f"Tree length is {len(tree)}")
```
    >>>
    Tree length is 7

Unfortunately, it still isn;t enough for the class to have oll the perks of the `list` type, it missing things like `count` and `index`, and implementing them all is very difficult. 

To solve this problem in Python, there is a `collections.abc` module defines a set of abstract base classes that provide you with all the typical methods for each container. Also, when you subclass them and forget to implement required methods a exception will be raised:
```python
from collections.abc import Sequence


class BadType(Sequence):
    pass

foo = BadType()
```
    >>>
    >>> foo = BadType()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: Can't instantiate abstract class BadType with abstract methods __getitem__, __len__

When you implement all the required methods, it will provide all the additional methods for free:
```python
class BetterNode(SequenceNode, Sequence):
    pass

tree = BetterNode(10, 
                    left=BetterNode(
                        5, 
                        left=BetterNode(2), 
                        right=BetterNode(
                            6, 
                            right=BetterNode(7))),
                    right=BetterNode(
                        15, left=BetterNode(11)))

print(f"Index of 7 is {tree.index(7)}")
print(f"Count of 10 is {tree.count(10)}")
```
    >>>
    Index of 7 is 3
    Count of 10 is 1

Benefits of inheriting from `collections.abc` are even greater for types like `set` and `MutableMapping`.

# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)