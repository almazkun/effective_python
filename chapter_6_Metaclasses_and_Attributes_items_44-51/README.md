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
        print(f"* Returning {result!r}")
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

* Python implementation for generic functionality often relies on `hasattr` built-in function to determine is the property exist, and the `getattr` to retrieve a value. These functions also look for attribute name in the instance `__dict__` before calling `__getattr__`:
```python
data = LoggingLazyRecord()  # Implements __getattr__
print(f"Before:             {data.__dict__}")
print(f"Has first foo:      {hasattr(data, 'foo')}")
print(f"After:              {data.__dict__}")
print(f"Has second foo:     {hasattr(data, 'foo')}")
```
    >>>
    Before:             {'exists': 5}
    * Called __getattr__('foo'), populating instance dictionary
    * Returning 'Value for foo'
    Has first foo:      True
    After:              {'exists': 5, 'foo': 'Value for foo'}
    Has second foo:     True

In this example, `__getattr__` is called only once. In the next example `__getattribute__` will be called each time `hasattr` and `getattr` is used with an instance:
```python
data = ValidatingRecord()   # Implements __getattribute__
print(f"Has first foo:      {hasattr(data, 'foo')}")

print(f"Has second foo:     {hasattr(data, 'foo')}")
```
    >>>
    * Called __getattribute__('foo')
    * Setting 'foo' to 'Value for foo'
    Has first foo:  True

    * Called __getattribute__('foo')
    * Found 'foo', returning 'Value for foo'
    Has second foo: True

* Now, we want to save a value assigned to the Python object to the database. We can do it using `__setattr__` method:
```python
class SavingRecord():
    def __setattr__(self, name, value):
        # Save some data for the record
        ...
        super().__setattr__(name, value)
```
`__setattr__` method will be called each time when value is assigned:
```python
class LoggingSavingRecord(SavingRecord):
    def __setattr__(self, name, value):
        print(f"* Called __setattr__({name!r}, {value!r})")
        super().__setattr__(name, value)


data = LoggingSavingRecord()
print(f"Before:  {data.__dict__}")
data.foo = 5
print(f"After:   {data.__dict__}")
data.foo = 7
print(f"Finally: {data.__dict__}")
```
    >>>
    Before:  {}
    * Called __setattr__('foo', 5)
    After:   {'foo': 5}
    * Called __setattr__('foo', 7)
    Finally: {'foo': 7}

* The problem with `__getattribute__` and `__setattr__` is that they are called each time when an attribute is accessed, even when we don't want it. For example, we want to look up keys in associated dictionary:
```python
class BrokenDictionaryRecord:
    def __init__(self, data):
        self._data = {}
    def __getattribute__(self, name):
        print(f"* Called __getattribute__({name!r})")
        return self._data[name]
```
This require accessing `self._data` from the `__getattribute__` method. However, if we try to do it, Python will recurs until it reaches its stack limit and die:
```python
data = BrokenDictionaryRecord({"foo": 3})
data.foo 
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 6, in __getattribute__
      File "<stdin>", line 6, in __getattribute__
      File "<stdin>", line 6, in __getattribute__
      [Previous line repeated 992 more times]
      File "<stdin>", line 5, in __getattribute__
    RecursionError: maximum recursion depth exceeded while calling a Python object
    * Called __getattribute__('_data')

The problem is that `__getattribute__` accesses `self._data`, which causes `__getattribute__` to run again, which accesses `self._data`, and so on. To avoid this, we can use `super().__getattribute__` method to fetch values from instance dictionary:
```python
class DictionaryRecord:
    def __init__(self, data):
        self._data = data
    def __getattribute__(self, name):
        print(f"* Called __getattribute__({name!r})")
        data_dict = super().__getattribute__("_data")
        return data_dict[name]


data = DictionaryRecord({"foo": 3})
print(f"foo: {data.foo}")
```
    >>>
    * Called __getattribute__('foo')
    foo: 3
* With `___setattr__` is `super().__setattr__` also needs to be used.

## Item 48: Validate Subclasses with `__init_subclass__`
One of the simplest example of using metaclasses is verifying that a subclass was defined correctly. When working with complex class hierarchy, you way want to enforce a certain style, require overriding methods, or have strict relationships between attributes. Metaclasses enable this by providing a reliable way to run a validation code each time a subclass is defined. 

Often a class's validation is run in the `__init__` method, when object of the class's type is constructed at runtime. Metaclasses can provide class validation even earlier: when module containing a class is being imported at the start of the program.

Before implementing metaclasses it is a good idea to understand the metaclass action for standard object. Metaclass is defined by inheriting from `type`. By default, a metaclass receives the contents of associated `class` statements in its `__new__`method. Here we can inspect and modify a class information before the type is actually constructed:
```python
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        print(f"* Running {meta}.__new__ for {name}")
        print(f"Bases: {bases}")
        print(class_dict)
        return type.__new__(meta, name, bases, class_dict)


class MyClass(metaclass=Meta):
    stuff=123
    def foo(self):
        pass


class MySubclass(MyClass):
    other = 567
    def bar(self):
        pass
```
The metaclass has access to the class, the parent classes (`bases`) and all the methods that are defined in the body of a class. All classes inherit from `object`, so it is not explicitly listed in the `tuple` of the base class:
    >>>
    * Running <class '__main__.Meta'>.__new__ for MyClass
    Bases: ()
    {'__module__': '__main__',
     '__qualname__': 'MyClass',
     'stuff': 123,
     'foo': <function MyClass.foo at 0x0000022D3520E828>}

    * Running <class '__main__.Meta'>.__new__ for MySubclass
    Bases: (<class '__main__.MyClass'>,)
    {'__module__': '__main__',
     '__qualname__': 'MySubclass',
     'other': 567, 
     'bar': <function MySubclass.bar at 0x0000022D3520EC18>}

* We can add functionality to the `Meta.__new__` method in order to validate all of the parameters of an associated class before it's defined. For example, we want te represent any type of multi sided polygon. It can be done by defining a special validating metaclass and using it in the base class of my polygon class hierarchy. Note, it is important not to apply same validation to the base class.
```python
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate subclasses of the Polygon class
        if bases:
            if class_dict["sides"] < 3:
                raise ValueError("Polygon need 3+ sides")
        return type.__new__(meta, name, bases, class_dict)


class Polygon(metaclass=ValidatePolygon):
    sides = None # Must be specified by subclasses
    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180


class Triangle(Polygon):
    sides = 3


class Rectangle(Polygon):
    sides = 4


class Nonagon(Polygon):
    sides = 9


assert Triangle.interior_angles() == 180
assert Rectangle.interior_angles() == 360
assert Nonagon.interior_angles() == 1260
```
The exception will be raised when number of sides is fewer than 3:
```python
print("Before class")


class Line(Polygon):
    print("Before sides")
    sides = 2
    print("After sides")


print("After class")
```
    Before class
    Before sides
    After sides
    *** A Thing being made
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 7, in __new__
    ValueError: Polygon need 3+ sides

* this seems like a lot of machinery to accomplish a simple task. Luckily, Python 3.6 introduced simplified syntax `__init_subclass__` special class method - for achieving this behavior with much simpler syntax, avoiding metaclasses entirely. Here is an example of same functionality using new method:
```python
class BetterPolygon:
    sides = None # Must be specified by subclass
    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.sides < 3:
            raise ValueError("Polygon need 3+ sides")
    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180


class Hexagon(BetterPolygon):
    sides = 6


assert Hexagon.interior_angles() == 720
```
The code is much shorter now, easier and exception is working:
```python
print("Before class")


class Point(BetterPolygon):
    sides = 1


print("After class")
```
    >>>
    Before sides
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 6, in __init_subclass__
    ValueError: Polygon need 3+ sides

* Another problem with standard Python metaclasses is that you can specify a single metaclass per class definition. If we need also validate color of the fill used for the region:
```python
class ValidateFilled(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate subclasses of the Filled class
        if bases:
            if class_dict["color"] not in ("red", "green"):
                raise ValueError("Fill color must be supported")
            return type.__new__(meta, name, bases, class_dict)


class Filled(metaclass=ValidateFilled):
    color = None # Must be specified by subclass
```
When you try to use `Polygon` and `Filled` metaclass together you get a error message:
```python
class RedPolygon(Filled, Polygon):
    color = "red"
    sides = 5
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases

It is possible to solve this problem by creating a complex hierarchy of metaclass `type` definition to layer validation:
```python
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate non-root classes
        if not class_dict.get("is_root"):
            if class_dict["sides"] < 3:
                raise ValueError("Polygons need 3+ sides")
        return type.__new__(meta, name, bases, class_dict)


class Polygon(metaclass=ValidatePolygon):
    is_root = True
    sides = None # Must be specified by subclass


class ValidateFilledPolygon(ValidatePolygon):
    def __new__(meta, name, bases, class_dict):
        # Only validate non-root classes
        if not class_dict.get("is_root"):
            if class_dict["color"] not in ("red", "green"):
                raise ValueError("Fill color must be supported")
        return super().__new__(meta, name, bases, class_dict)


class FilledPolygon(Polygon, metaclass=ValidateFilledPolygon):
    is_root = True
    color = None
```
This requires `FilledPolygon` instance to be `Polygon` instance:
```python
class GreenPentagon(FilledPolygon):
    color = "green"
    sides = 5


greenie = GreenPentagon()
assert isinstance(greenie, Polygon)
```
Validation works for colors:
```python
class OrangePentagon(FilledPolygon):
    color = "orange"
    sides = 5
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 6, in __new__
    ValueError: Fill color must be supported

and numbers of sides:
```python
class RedLine(FilledPolygon):
    color = "red"
    sides = 1
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 7, in __new__
      File "<stdin>", line 6, in __new__
    ValueError: Polygons need 3+ sides

However, if we want to use one of this validations to other class hierarchy, we would need te rewrite all metaclasses as well. 

The `__init_subclass__` special method can also be used to solve this method. It can be used with multiple layers of class hierarchy as long as the `super` built-in is used to call any parent or sibling `__init_subclass__` definitions. It is even compatible with multiple inheritance. Here is the modified `BetterPolygon` to validate colors as well:
```python
class Filled:
    color = None # Must be specified by subclass
    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.color not in ("red", "green", "blue"):
                raise ValueError("Fills need a valid color")
```
We can inherit both class to define a new class. Both classes call `super().__init_subclass__()`, causing both validations run when a subclass is created:
```python
class RedTriangle(Filled, BetterPolygon):
    color = "red"
    sides = 3


ruddy = RedTriangle()
assert isinstance(ruddy, Filled)
assert isinstance(ruddy, BetterPolygon)
```
Validation for number of sides works:
```python
print("Before class")


class BlueLine(Filled, BetterPolygon):
    color = "blue"
    sides = 2


print("After class")
```
    >>>
    Before class
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 4, in __init_subclass__
      File "<stdin>", line 6, in __init_subclass__
    ValueError: Polygon need 3+ sides

and for colors:
```python
print("Before class")


class BeigeSquare(Filled, BetterPolygon):
    color = "beige"
    sides = 4


print("After class")
```
    >>>
    Before class
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 6, in __init_subclass__
    ValueError: Fills need a valid color

* We can use `__init_subclass__` in complex cases like diamond inheritance. Here is an example:
```python
class Top:
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Top for {cls}")


class Left(Top):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Left for {cls}")


class Right(Top):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Right for {cls}")


class Bottom(Left, Right):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Bottom for {cls}")
```
    >>>
    Top for <class '__main__.Left'>
    Top for <class '__main__.Right'>
    Top for <class '__main__.Bottom'>
    Right for <class '__main__.Bottom'>
    Left for <class '__main__.Bottom'>

`Top.__init_subclass__` is called only ones per each class, even though there are two paths to it. 

## Item 49: Register Class Existence with `__init_subclass__`

Another common way of using a metaclass is to register types in the program. Registration is useful when you need to do a reverse lookup, when it needed to map a identifier to s corresponding class.

* For example, we need to make our own serializer, turn our objects into JSON strings. Here we it is implemented generically by defining a base class that records the constructor parameters and turns them into a JSON dictionary:
```python
import json


class Serializable :
    def __init__(self, *args):
        self.args = args
    def serialize(self):
        return json.dumps({"args": self.args})
```
This class makes it easy to serialize simple, immutable data structures like `Point2D` to a string:
```python
class Point2D(Serializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"


point = Point2D(5, 3)
print(f"Object:     {point}")
print(f"Serialized: {point.serialize()}")
```
    >>>
    Object:     Point2D(5, 3)
    Serialized: {"args": [5, 3]}

Now, we need to deserialize Json and make an `Point2D` object:
```python
class Deserializable(Serializable):
    @classmethod
    def deserialize(cls, json_data):
        params = json.loads(json_data)
        return cls(*params["args"])
```
This is also works well for simple immutable data structures in a generic way:
```python
class BetterPoint2D(Deserializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"


before = BetterPoint2D(5, 3)
print(f"Before:     {before}")
data = before.serialize()
print(f"Serialized: {data}")
after = BetterPoint2D.deserialize(data)
print(f"After:      {after}")
```
    >>>
    Before:     Point2D(5, 3)
    Serialized: {"args": [5, 3]}
    After:      Point2D(5, 3)

The problem with this approach that you need to know intended type of serialized data ahead of time.

* Ideally, we want to have many classes serializing data and one function deserializing any of them. To do so we can map object's class name in the JSON data:
```python
class BetterSerializable:
    def __init__(self, *args):
        self.args = args
    def serialize(self):
        return json.dumps({
            "class": self.__class__.__name__,
            "args": self.args,
        })
    def __repr__(self):
        name = self.__class__.__name__
        args_str = ", ".join(str(x) for x in self.args)
        return f"{name}({args_str})"
```
Then we can maintain a mapping of class names back to constructors for this objects. THe general `deserialize` function works for any class passed to `register_class`:
```python
registry = {}


def register_class(target_class):
    registry[target_class.__name__] = target_class

def deserialize(data):
    params = json.loads(data)
    name = params["class"]
    target_class = registry[name]
    return target_class(*params["args"])
```
To ensure that `deserialize` works properly, we must call `registry_class` for each class we want to deserialize in the future.
```python
class EvenBetterPoint2D(BetterSerializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y


register_class(EvenBetterPoint2D)
```
Now, we can deserialize any arbitrary string, without having to know which class it contains:
```python
before = EvenBetterPoint2D(5, 3)
print(f"Before:     {before}")
data = before.serialize()
print(f"Serialized: {data}")
after = deserialize(data)
print(f"After:      {after}")
```
    >>>
    Before:     EvenBetterPoint2D (5, 3)
    Serialized: {"class": "EvenBetterPoint2D", "args": [5, 3]}
    After:      EvenBetterPoint2D (5, 3)

The problem is that you may forget to call `register_class`:
```python
class Point3D(BetterSerializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

# Forgot to call register_class! Whoops!

point = Point3D(5, 9, -4)
data = point.serialize()
deserialize(data)
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 4, in deserialize
    KeyError: 'Point3D'

* We can implement the metaclass which will ensure to register a class immediately after class's body:
```python
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_class(cls)
        return cls


class RegisteredSerializable(BetterSerializable, metaclass=Meta):
    pass
```
Wen subclass of the `RegisteredSerializable` is defined we can be sure that `register_class` is called and deserialize will work properly:
```python
class Vector3D(RegisteredSerializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x, self.y, self.z = x, y, z


before = Vector3D(10, -7, 3)
print(f"Before:     {before}")
data = before.serialize()
print(f"Serialized: {data}")
print(f"After:      {deserialize(data)}")
```
    >>>
    Before:     Vector3D(10, -7, 3)
    Serialized: {"class": "Vector3D", "args": [10, -7, 3]}
    After:      Vector3D(10, -7, 3)

* Even better approach is to use `__init_subclass__` syntax:
```python
class BetterRegisteredSerializable(BetterSerializable):
    def __init_subclass__(cls):
        super().__init_subclass__()
        register_class(cls)


class Vector1D(BetterRegisteredSerializable):
    def __init__(self, magnitude):
        super().__init__(magnitude)
        self.magnitude = magnitude


before = Vector1D(6)
print(f"Before:     {before}")
data = before.serialize()
print(f"Serialized: {data}")
print(f"After:      {deserialize(data)}")
```
    >>>
    Before:     Vector1D(6)
    Serialized: {"class": "Vector1D", "args": [6]}
    After:      Vector1D(6)
By suing `__init_subclass__` (or metaclass) for class registration, you can be sure that class registration is done for each class. 


## Item 50: Annotate Class Attributes with `__set_name__`

Pne more useful feature enabled by metaclasses is the ability to modify or annotate an attribute after it a class is defined in class but before an instance is used. THis approach is commonly used with descriptors.

For example, we want to define a class which represents a row in a custom database. We need to have corresponding property on the class for each column in the database table:
```python
class Field:
    def __init__(self, name):
        self.name = name
        self.internal_name = "_" + self.name
    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")
    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)
```
Then, we can define each field:
```python
class Customer:
    first_name = Field("first_name")
    last_name = Field("last_name")
    prefix = Field("prefix")
    suffix = Field("suffix")
```
Using this class is simple:
```python
cust = Customer()
print(f"Before: {cust.first_name!r} {cust.__dict__}")
cust.first_name = "Euclid"
print(f"After: {cust.first_name!r} {cust.__dict__}")
```
    >>>
    Before: '' {}
    After: 'Euclid' {'_first_name': 'Euclid'}

* But this class definition seems redundant. Why do we need to write `first_name` twice:
```python
class Customer:
    # Left side is redundant with right side
    first_name = Field("first_name")
```
The problem is that the order of operation in the `Customer` class definition is opposite to how it reads from left to right. First, the `Field` constructor is called as `Field("first_name")`. Then the return value of that is assigned to `Customer.first_name`. There is now way for a `Field` instance to know to which attribute its value will be assigned.

We may use metaclass, to assign `Field.name` and `Field.internal_name` on the descriptor automatically:
```python
class Meta(type):
    def __new__(meta, name, bases, class_dict):
            for key, value in class_dict.items():
                    if isinstance(value, Field):
                        value.name = key
                        value.internal_name = "_" + key
                    cls = type.__new__(meta, name, bases, class_dict)
                    return cls

class DatabaseRow(metaclass=Meta):
    pass
```
To work with the metaclass, `Field` class is mostly unchanged:
```python
class Field:
    def __init__(self):
        # Will be assigned by the metaclass
        self.name = None
        self.internal_name = None
    def __get__(self, instance, instance_type):
        if instance is None:
            return Self
        return getattr(instance, self.internal_name, "")
    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)
```
By using the metaclass and the new `Field` class, the class definition now doesn't have a redundant code:
```python
class BetterCustomer(DatabaseRow):
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()
```
And behavior is unchanged:
```python
cust = Customer()
print(f"Before: {cust.first_name!r} {cust.__dict__}")
cust.first_name = "Euclid"
print(f"After: {cust.first_name!r} {cust.__dict__}")
```
    >>>
    Before: '' {}
    After: 'Euclid' {'_first_name': 'Euclid'}

The problem with this code is that in order to use `Field` class we also need to inherit from `DatabaseRow` class. If we fail to do so, code wil not work:
```python
class BrokenCustomer:
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()


cust = BrokenCustomer()
cust.first_name = "Mersenne" 
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 11, in __set__
    TypeError: attribute name must be string, not 'NoneType'

* There is a solution for that in Python 3.6. It is `__set_name__` method. THis method is called on every descriptors instance and the attribute name to which descriptor instance was assigned. Now we don't need a metaclass:
```python
class Field:
    def __init__(self):
        self.name = None
        self.internal_name = None
    def __set_name__(self, owner, name):
        self.name = name
        self.internal_name = "_" + name
    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")
    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)
```
Here it is working:
```python
class FixedCustomer:
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()


cust = FixedCustomer()
print(f"Before: {cust.first_name!r} {cust.__dict__}")
cust.first_name = "Mersenne"
print(f"After: {cust.first_name!r} {cust.__dict__}")
```
    >>>
    Before: '' {}
    After: 'Mersenne' {'_first_name': 'Mersenne'}

## Item 51: Prefer Class Decorators Over Metaclasses for Composable Class Extensions

For example, we need a debugging decorator, which will prints arguments, return values, and raise exceptions:
```python
from functools import wraps


def trace_func(func):
    if hasattr(func, "tracing"): # Only decorate once
        return func
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print(f"{func.__name__} ({args!r}, {kwargs!r}) -> "
                  f"{result!r}")
    wrapper.tracing = True
    return wrapper
```
We can apply this decorator in our new `dict` subclass:
```python
class TraceDict(dict):
    @trace_func
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    @trace_func
    def __setitem__(self, *args, **kwargs):
        return super().__setitem__(*args, **kwargs)
    @trace_func
    def __getitem__(self, *args, **kwargs):
        return super().__getitem__(*args, **kwargs)
```
We can check the code:
```python
trace_dict = TraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]

try:
    trace_dict["does not exist"]
except KeyError:
    pass # Expected
```
    >>>
    __init__ (({'hi': 1}, [('hi', 1)]), {}) -> None
    __setitem__ (({'hi': 1, 'there': 2}, 'there', 2), {}) -> None
    __getitem__ (({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    __getitem__ (({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

The problem with this approach is that we need to redefine all of the methods that we want to decorate with `@trace_func`. It is redundant and error prone. If later methods are added to the `dict` superclass, these new methods won't be decorated unless added to the `TraceDict`. 

* One wey to solve this is to use metaclass to automatically decorate all methods of a class:
```python
import types


trace_types = (
    types.MethodType,
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType)


class TraceMeta(type):
    def __new__(meta, name, bases, class_dict):
        klass = super().__new__(meta, name, bases, class_dict)
        for key in dir(klass):
            value = getattr(klass, key)
            if isinstance(value, trace_types):
                wrapped = trace_func(value)
                setattr(klass, key, wrapped)
        return klass
```
To verify this approach, we will use `dict` subclass with metaclass:
```python
class TraceDict(dict, metaclass=TraceMeta):
    pass


trace_dict = TraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]

try:
    trace_dict["does not exist"]
except KeyError:
    pass # Expected

```
    >>>
    __new__ ((<class '__main__.TraceDict'>, [('hi', 1)]), {}) -> {}
    __getitem__ (({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    __getitem__ (({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

This works.

* What happen if we try to use `TraceMeta` when a superclass already has specified a metaclass:
```python
class OtherMeta(type):
    pass


class SimpleDict(dict, metaclass=OtherMeta):
    pass


class TraceDict(SimpleDict, metaclass=TraceMeta):
    pass
```
    >>>
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases

This happen when because `TraceMeta` does not inherit from `OtherMeta`. In theory, we can use metaclass inheritance, making `OtherMeta` inherit from `TraceMeta`:
```python
class TraceMeta(type):
    ...


class OtherMeta(TraceMeta):
    pass


class SimpleDict(dict, metaclass=OtherMeta):
    pass


class TraceDict(SimpleDict, metaclass=TraceMeta):
    pass


trace_dict = TraceDict([('hi', 1)])
trace_dict['there'] = 2
trace_dict['hi']
try:
    trace_dict['does not exist']
except KeyError:
    pass # Expected

```
    >>>
    __init_subclass__ ((), {}) -> None
    __new__ ((<class '__main__.TraceDict'>, [('hi', 1)]), {}) -> {}
    __getitem__ (({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    1
    __getitem__ (({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

This also works, but it won't work with if we can't modify metaclass or use other utility metaclasses. Overall, this approach puts too many constrains, to really be useful.

* We can make it work with `@class_decorators`. Class decorators works just like function decorators. THey are applied with the `@` symbol before the class declaration. The function is expected to modify or re-create the class accordingly and then return it:
```python
def my_class_decorator(klass):
    klass.extra_param = "hello"
    return klass


@my_class_decorator
class MyClass:
    pass


print(MyClass)
print(MyClass.extra_param)
```
    >>>
    <class '__main__.MyClass'>
    hello

* We can implement a class decorator to apply `trace_func` to all methods and functions of a class by moving the core of the `TraceMeta.__new__` method into stand-alone function. This implementation is much shorter than a metaclass version:
```python
def trace(klass):
    for key in dir(klass):
        value = getattr(klass, key)
        if isinstance(value, trace_types):
            wrapped = trace_func(value)
            setattr(klass, key, wrapped)
    return klass
```
We can apply class decorator to have the same effect as with a metaclass:
```python
@trace
class TraceDict(dict):
    pass


trace_dict = TraceDict([('hi', 1)])
trace_dict['there'] = 2
trace_dict['hi']
try:
    trace_dict['does not exist']
except KeyError:
    pass # Expected
```
    >>>
    __new__ ((<class '__main__.TraceDict'>, [('hi', 1)]), {}) -> {}
    __getitem__ (({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    1
    __getitem__ (({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

Class decorators also work with classes with already defined metaclasses:
```python
class OtherMeta(type):
    pass


@trace
class TraceDict(dict, metaclass=OtherMeta):
    pass


trace_dict = TraceDict([('hi', 1)])
trace_dict['there'] = 2
trace_dict['hi']
try:
    trace_dict['does not exist']
except KeyError:
    pass # Expected
```
    >>>
    __new__ ((<class '__main__.TraceDict'>, [('hi', 1)]), {}) -> {}
    __getitem__ (({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    1
    __getitem__ (({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

* Class decorators are the best tool for composable class extending.

# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)