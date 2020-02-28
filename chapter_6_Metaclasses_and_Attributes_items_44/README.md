# Chapter 6. Metaclasses and Attributes

Metaclasses are often listed as a Python's feature, but few understand what they accomplish in practice. Simply put, metaclass add special behavior to class each time its defined.

Similarly mysterious and powerful are Python's built-in features for dynamically customizing attribute access. Along with Python's object-oriented constructs, these facilities provide wonderful tools to ease he transit from simple class to complex ones. 

But, this features also come with pitfalls. Dynamic attributes enables you to override object and cause unexpected side effects. Metaclasses can create extremely bizarre behaviors that are unapproachable to newcomers. It is important to follow the `rule-of-least-surprize` and use this instrument to implement well-understood idioms. 

## Item 44: Use Plain Attributes instead of Setter and Getter Methods 
* Programmers coming to Python from another languages my use `getter` and `setter` methods in their classes:
```python
class OldResistor:
    def __init__(self, ohms):
        self._ohms = ohms
    def get_ohms(self):
        return self._ohms
    def set_ohms(self, ohms):
        self._ohms = ohms
```
Using this setter and getter is simple, but not Pythonic:
```python
r0 = OldResistor(50e3)
print(f"Before: {r0.get_ohms()}")
r0.set_ohms(10e3)
print(f"After: {r0.get_ohms()}")
```
    >>>
    Before: 50000.0
    After: 10000.0

This methods especially are clumsy for operations like incrementing in place:
```python
r0.set_ohms(r0.get_ohms() - 4e3)
assert r0.get_ohms() == 6e3
```
This method do help in defining interfaces for a class.

* In Python, however, you never need to implement explicit getter and setter. Instead you should always define class with simple public attributes:
```python
class Resistor:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0

r1 = Resistor(50e3)
r1.ohms = 10e3
```
This attributes makes operations like incrementing natural and clear:
```python
r1.ohms += 5e3
```
* Later, if we need to add special behavior when an attribute is set, we can migrate to `@property` decorator and its corresponding `setter` attribute. Here, we implement new functionality to change `current` by assigning the `voltage` property:
```python
class VoltageResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)
        self._voltage = 0
    @property
    def voltage(self):
        return self._voltage
    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage
        self.current = self.voltage / self.ohms
```
Now assigning a `voltage` property will return `voltage` setter method, which will in turn update the `current` attribute of the object to match:
```python
v2 = VoltageResistance(1e3)
print(f"Before: {v2.current:.2f} amps")
v2.voltage = 10
print(f"After: {v2.current:.2f} amps")
```
    >>>
    Before: 0.00 amps
    After: 0.01 amps
* Specifying `setter` in a `@property` also enables us to check the value passed to the attributes:
```python
class BoundedResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)
    @property
    def ohms(self):
        return self._ohms
    @ohms.setter
    def ohms(self, ohms):
        if ohms <= 0:
            raise ValueError(f"ohms must be > 0; got {ohms}")
        self._ohms = ohms

r3 = BoundedResistance(1e3)
r3.ohms = 0
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 10, in ohms
    ValueError: ohms must be > 0; got 0
Exception is also raised if we pass invalid value to the constructor:
```python
BoundedResistance(-5)
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 3, in __init__
      File "<stdin>", line 3, in __init__
      File "<stdin>", line 10, in ohms
    ValueError: ohms must be > 0; got -5

* We can even `@property` to make attributes from parent classes immutable:
```python
class FixedResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)
    @property
    def ohms(self):
        return self._ohms
    @ohms.setter
    def ohms(self, ohms):
        if hasattr(self, "_ohms"):
            raise AttributeError("Ohms is immutable")
        self._ohms = ohms
```
Now, trying to change attribute is raising an error:
```python
r4 = FixedResistance(1e3)
r4.ohms = 2e3
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 10, in ohms
    AttributeError: Ohms is immutable

* When using `@property` method be sure not that behavior you are implementing is not surprising. Don't set other attributes in getter property method:
```python
class MysteriousResistance(Resistor):
    @property
    def ohms(self):
        self.voltage = self._ohms * self.current
        return self._ohms
    @ohms.setter
    def ohms(self, ohms):
        self._ohms = ohms
```
Setting other attributes in getter property method leads to extremely strange behavior:
```python
r7 = MysteriousResistance(10)
r7.current = 0.01
print(f"Before: {r7.voltage:.2f}")
r7.ohms
print(f"After: {r7.voltage:.2f}")
```
    >>>
    Before: 0.00
    After: 0.10
Try not to use expensive and slow thing in @property methods. 

Remember that `property` methods can only be shared with subclasses, unrelated classes can't share the same implementation. In this case `descriptors` may be used.

## Item 45: Consider @property Instead of Refactoring Attributes
The built-in `@property` decorator makes it easy for simple accesses of an instance's attributes to act smarter. One advanced but common use of `@property` is transition of simple numerical attribute into an on-the-fly calculation. This is extremely helpful because it lets you migrate all existing usage of a class to have a new behavior without changing calls to that class.

For example, we need to have a leaky bucket quota. Here the `Bucket` class show how much of the quota remains and the duration for which quota will be available:
```python
from datetime import datetime, timedelta


class Bucket:
    def __init__(self,period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.quota = 0
    def __repr__(self):
        return f"Bucket (quota={self.quota})"
```
The leaky bucket algorithm works by ensuring that, whenever the bucket is filled, amount of quota is not carried over from one period to another:
```python
def fill(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount
```
Each time a quota consumer want to do something, it must first ensure that it can deduct the amount of quota it needs to use:
```python
def deduct(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        return False                # Bucket hasn't been filled this period.
    if bucket.quota - amount < 0:
        return False                # Bucket was filled, but not enough
    bucket.quota -= amount 
    return True                     # Bucket has enough, quota consumed
```
To use this class, first fill the bucket:
```python
bucket = Bucket(60)
fill(bucket, 100)
print(bucket)
```
    >>>
    Bucket (quota=100)
Then I deduct quota that:
```python
if deduct(bucket, 99):
    print("Had 99 quota")
else:
    print("Not enough for 99 quota")

print(bucket)
```
    >>>
    Had 99 quota
    Bucket (quota=1)
Eventually, it will prevent to use quotas:
```python
if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")

print(bucket)
```
    >>>
    Not enough for 3 quota
    Bucket (quota=1)
* Problem with this implementation is that we never now what is the quota level started with. It would be helpful to know why have deduct blocked the quota usage, is it because it has runout of the quota or haven't been filled this period.

To fix this we may implement `max_quota` and `quota_consumed` for this period:
```python
class NewBucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.max_quota = 0
        self.quota_consumed = 0
    def __repr__(self):
        return (f"NewBucket(max_quota={self.max_quota}, "
                f"quota_consumed={self.quota_consumed})")
```
To match the previous interface of the `Bucket` class, we can use `@property` method to compute the current level on-the-fly using this new attributes:
```python
    @property
    def quota(self):
        return self.max_quota - self.quota_consumed
```
Implementing `fill` and `deduct` methods:
```python
    @quota.setter
    def quota(self, amount):
        delta = self.max_quota - amount
        if amount == 0:
            # Quota being reset for a new period
            self.quota_consumed = 0
            self.max_quota = 0
        elif delta < 0:
            # Quota being filled for the new period
            assert self.quota_consumed == 0
            self.max_quota = amount
        else:
            # Quota being consumed during the period
            assert self.max_quota >= self.quota_consumed
            self.quota_consumed += delta
```
Code will work with previous demo:
```python
bucket = NewBucket(60)
print("Initial", bucket)
fill(bucket, 100)
print("Filled", bucket)

if deduct(bucket, 99):
    print("Had 99 quota")
else:
    print("Not enough for 99 quota")

print("Now", bucket)

if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")

print("Still", bucket)
```
    >>>
    Initial NewBucket(max_quota=0, quota_consumed=0)
    Filled NewBucket(max_quota=100, quota_consumed=0)
    Had 99 quota
    Now NewBucket(max_quota=100, quota_consumed=99)
    Not enough for 3 quota
    Still NewBucket(max_quota=100, quota_consumed=99)

`@property` especially convenient because it lets make you incremental incremental progress toward better data model over time. It is better to implement `fill` and `deduct` methods as instance methods from the beginning, however it a real-world example when code growth over time, scope increases, multiple authors contribute without anyone considering long-term hygiene and so on.

It is better to think about refactoring a class when you start to overuse `@property` methods.

## Item 46: Use Descriptors for Reuseable `@property` Methods.
The biggest problem of `@property` methods is reuse. These methods can't be reused by multiple attributes within a class, also cannot be sheared among unrelated classes. 

* For example,we want a class witch validated that grade received by a student is a percentage:
```python
class Homework:
    def __init__(self):
        self._grade = 0
    @property
    def grade(self):
        return self._grade
    @grade.setter
    def grade(self, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._grade = value
```
Using `@property` makes it easy to use:
```python
galileo = Homework()
galileo.grade = 95
```
* Now, we want to give a grade for a exam, where exam has several subjects, each with separate grade:
```python
class Exam:
    def __init__():
        self._writing_grade = 0
        self._math_grade = 0

    @staticmethod
    def _check_grade(value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
```
This quickly gets tedious, now we need to add `@property` methods to each subject:
```python
    @property
    def writing_grade(self):
        return self._writing_grade
    @writing_grade.setter
    def writing_grade(self, value):
        self._check_grade(value)
        self._writing_grade = value
    @property
    def math_grade(self):
        return self._math_grade
    @math_grade.setter
    def math_grade(self, value):
        self._check_grade(value)
        self._math_grade = value
```
Also, we will need to rewrite these methods to every new class. 

* The better way to do it is use a `descriptor`. The `descriptor protocol` defines how attribute access is interpreted by the language. A descriptor class can provide `__get__` and `__set__` methods that let you reuse the grade validator.

Here the `Grade` class implementing descriptor protocol:
```python
class Grade:
    def __get__(self, instance, instance_type):
        ...
    def __set__(self, instance, value)
        ...


class Exam:
    # Class Attributes
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()
```
It important to understand how the `Grade` works, what will python do when such descriptor attributes are accessed on an `Exam` instance.

* When a property is assigned:
```python
exam = Exam()
exam.writing_grade = 40
```
It is interpreted as:
```python
Exam.__dict__["writing_grade"].__set__(exam, 40)
```
* When a property is retrieved:
```python
exam.writing_grade
```
Is is interpreted as:
```python
Exam.__dict__["writing_grade"].__get__(exam, Exam)
```
* The `__getattribute__` method of a object is driving this behavior. In short, when `Exam` instance doesn't have `writing_grade` attribute, Python falls back to the `Exam` class's attribute instead. If this class attribute is an object and have `__get__` and `__set__` methods, Python assumes that you want follow `descriptor protocol`.

Knowing that, here is our first attempt to implement `Grade` descriptor:
```python
class Grade:
    def __init__(self):
        self._value = 0
    def __get__(self, instance, instance_type):
        return self._value
    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._value = value
```
Unfortunately, this implementation will work only on a single `Exam` instance:
```python
class Exam:
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()

first_exam = Exam()
first_exam.writing_grade = 82
first_exam.science_grade = 99
print(f"Writing {first_exam.writing_grade}")
print(f"Science {first_exam.science_grade}")
```
    >>>
    Writing 82
    Science 99
But, accessing these attributes on multiple `Exam` instances cause unexpected behavior:
```python
second_exam = Exam()
second_exam.writing_grade = 75
print(f"Second {second_exam.writing_grade} is right")
print(f"First  {first_exam.writing_grade} is wrong; "
        f"should be 82")
```
    >>>
    Second 75 is right
    First 75 is wrong; should be 82
The problem is that single `Grade` instance is shared among all `Exam` instances for the class attribute `writing_exam`. The `Grade` instance for this attribute is created once in a programs lifetime, when class `Exam` is first defined, not each time exam instance is created.

* To solve this problem, we need `Grade` class to keep track of its value for each  unique `Exam` instance. We can do it by saving the per-instance state in a dictionary:
```python
class Grade:
    def __init__(self):
        self._values = {}
    def __get__(self, instances, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)
    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._values[instance] = value
```
This implementation is simple and works well, but it leaks memory. `_values` dictionary hold a reference to every instance of `Exam` ever passed to `__set__` over program lifetime.

To fix this we can use `WeakKeyDictionary` from `weakref` built-in module instead of `dict` used for `_values`. THe `WeakKeyDictionary` has a unique behavior to remove all `Exam` instances from the set when Python's runtime knows it's holding the instance's last remaining reference in the program:
```python
from weakref import WeakKeyDictionary


class Grade:
    def __init__(self):
        self._values = WeakKeyDictionary()
    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)
    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._values[instance] = value


class Exam:
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()


first_exam = Exam()
first_exam.writing_grade = 82
second_exam = Exam()
second_exam.writing_grade = 75
print(f"First  {first_exam.writing_grade} is right")
print(f"Second {second_exam.writing_grade} is right")
```
    >>>
    First  82 is right
    Second 75 is right

## Item 47: Use `__getattr__`, `__getattribute__` and `__setattr__` for Lazy Attributes

Python object hooks are good way to write generic code to glue a system together.

* For example, we need to represent our database records as a Python objects. Database ahs its schema already. Good thing is that code in Python, which connects code to database does not need to know the exact schema, it can be generic.

THis dynamic behavior is possible with the `__getattr__` special methods. If a class defines `__getattr__`, that method calls each time when an attribute can't be found in an object's instance dictionary:
```python
class LazyRecord:
    def __init__(self):
        self.exists = 5
    def __getattr__(self, name):
        value = f"Value for {name}"
        setattr(self, name, value)
        return value
```
Here we access a missing attribute `foo`, which forces Python call `__getattr__` method:
```python
data = LazyRecord()
print(f"Before: {data.__dict__}")
print(f"Foo: {data.foo}")
print(f"After: {data.__dict__}")
```
    >>>
    Before: {'exists': 5}
    Foo: Value for foo
    After: {'exists': 5, 'foo': 'Value for foo'}

Here is a logging implemented. Note how `super().__getattr__()` calling superclass's implementation of `__getattr__` to fetch the real property and avoid infinite recursion:
```python
class LoggingLazyRecord(LazyRecord):
    def __getattr__(self, name):
        print(f"* Called __getattr__({name!r}), "
                f"populating instance dictionary")
        result = super().__getattr__(name)
        print(f"Reading {result!r}")
        return result

data = LoggingLazyRecord()
print(f"Exists:     {data.exists}")
print(f"First foo:  {data.foo}")
print(f"Second.foo: {data.foo}")

```
    >>>
    Exists:     5
    * Called __getattr__('foo'), populating instance dictionary
    Reading 'Value for foo'
    First foo:  Value for foo
    Second.foo: Value for foo

The `exists` attribute is present, `__getattr__` not called. The foo attribute is absent and `__getattr__` is called. However, on second calling of the `foo` attribute `__getattr__` is not called, because `foo` is populated in the instance dictionary by `__setattr__`.

This behavior is helpful for use cases like lazily accessing schemaless data. `__getattr__` runs ones populating all the attributes, al the following accesses retrieve the existing results.

If we need to have it updated each call, we way use `__getattribute__` method instead. This attribute will is called every time a attribute is accessed. It may be expensive on the program resource wise. Here is the example of `__getattribute__`:
```python
class ValidatingRecord:
    def __init__(self):
        self.exist = 5
    def __getattribute__(self, name):
        print(f"* Called __getattribute__({name!r})")
        try:
            value = super().__getattribute__(name)
            print(f"* Found {name!r}, returning {value!r}")
            return value
        except AttributeError:
            value = f"Value for {name}"
            print(f"* Setting {name!r} to {value!r}")
            setattr(self, name, value)
            return value


data = ValidatingRecord()
print(f"exists:     {data.exist}")
print(f"First foo:  {data.foo}")
print(f"Second foo: {data.foo}")
```
    >>>
    * Called __getattribute__('exist')
    * Found 'exist', returning 5
    exists:     5
    * Called __getattribute__('foo')
    * Setting 'foo' to 'Value for foo'
    First foo:  Value for foo
    * Called __getattribute__('foo')
    * Found 'foo', returning 'Value for foo'
    Second foo: Value for foo

* In the event when some attribute shouldn't exist, we can raise an `AttributeError` both on `__getattr__` and `__getattribute__`:
```python
class MissingPropertyRecord:
    def __getattr__(self, name):
        if name == "bad_name":
            raise AttributeError(f"{name} is missing")
            ...


data = MissingPropertyRecord()
data.bad_name
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 4, in __getattr__
    AttributeError: bad_name is missing


    
# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)