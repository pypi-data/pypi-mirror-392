# Quickstart

:book: This page gives a quick overview on how to use the `minrecord`.
You should read this page if you want to learn how to use the records.
This page does not explain the internal behavior of the records.
While `minrecord` was designed to work in a ML workflow, you can use it in other contexts if it fits
your need.

**Prerequisites:** You’ll need to know a bit of Python.
For a refresher, see the [Python tutorial](https://docs.python.org/tutorial/).

## Record

`minrecord` is organized around the `BaseRecord` class. It defines the interface to implement a
record object.
`minrecord` provides the `Record` class, which is a generic implementation of a record.
Each `Record` object has a name and tracks the last values.

```pycon

>>> from minrecord import Record
>>> record = Record("loss")
>>> record
Record(name=loss, max_size=10, size=0)
>>> record.name
'loss'

```

Usually, it is useful to keep only the last values, but it also possible to track a large number of
values, but it can consume a lot of memory of the values to track take significant amount of memory.
By default, the `Record` objects only track the last 10 values, but it is possible to control the
memory consumption by setting carefully the `max_size` argument.

```pycon

>>> from minrecord import Record
>>> record = Record("my_record", max_size=5)
>>> record
Record(name=my_record, max_size=5, size=0)

```

After creating a record, the `add_record` method can be used to add a value to the record.
The following example shows how to add the value `4.2` to the record.

```pycon

>>> from minrecord import Record
>>> record = Record("loss")
>>> record.add_value(4.2)
>>> record
Record(name=loss, max_size=10, size=1)

```

When adding a value, it is possible to specify a step to track when the value was added.

```pycon

>>> from minrecord import Record
>>> record = Record("loss")
>>> record.add_value(4.2, step=2)
>>> record
Record(name=loss, max_size=10, size=1)

```

The step can be a number or `None`. `None` means no valid step to track.
It is possible to get the last value added by using the `get_best_value` method.

```pycon

>>> from minrecord import Record
>>> record = Record("loss")
>>> record.add_value(4.2, step=1)
>>> record.add_value(2.4, step=2)
>>> record
Record(name=loss, max_size=10, size=2)
>>> record.get_last_value()
2.4

```

Calling `get_best_value` on an empty record raises a `EmptyRecordError` exception.
It is possible to check if a record is empty or not by using the `is_empty` method.

```pycon

>>> from minrecord import Record
>>> record = Record("loss")
>>> record.is_empty()
True
>>> record.add_value(4.2, step=1)
>>> record.is_empty()
False

```

If there are multiple values to add, it is possible to use the `update` method.
The input is a sequence of 2-tuples where the first item is the step and the second item is the
value.

```pycon

>>> from minrecord import Record
>>> record = Record("loss")
>>> record.update([(0, 42), (None, 45), (2, 46)])
>>> record
Record(name=loss, max_size=10, size=3)
>>> record.get_last_value()
46

```

In the example above, the second element does not have a valid step so the value is set to `None`.
It is possible to add elements when creating the record.

```pycon

>>> from minrecord import Record
>>> record = Record("loss", elements=[(0, 42), (None, 45), (2, 46)])
>>> record
Record(name=loss, max_size=10, size=3)
>>> record.get_last_value()
46

```

It is possible to access the most recent values added to the record by using the `get_most_recent`
method.

```pycon

>>> from minrecord import Record
>>> record = Record("loss", elements=[(0, 42), (None, 45), (2, 46)])
>>> record.add_value(40)
>>> record.get_most_recent()
((0, 42), (None, 45), (2, 46), (None, 40))

```

It is possible to check if two `Record` objects are equal by calling the `equal` method.

```pycon

>>> from minrecord import Record
>>> record1 = Record("loss")
>>> record2 = Record("loss", elements=[(0, 42), (None, 45), (2, 46)])
>>> record3 = Record("loss", elements=[(0, 42), (None, 45), (2, 46)])
>>> record1.equal(record2)
False
>>> record3.equal(record2)
True

```

## Comparable Record

`minrecord` also provides some comparable records i.e. records that track the best value.
There is a generic `ComparableRecord` class where the user just needs to implement the comparator
object that is used to find the nest value.
There are `MaxScalarRecord` and `MinScalarRecord` that are specialized implementations
of `ComparableRecord` for scalars (e.g. `float` or `int`).
It is possible to know if a record is comparable by calling the `is_comparable` methods.

```pycon

>>> from minrecord import MaxScalarRecord, MinScalarRecord, Record
>>> record = Record("my_value")
>>> record.is_comparable()
False
>>> record_max = MaxScalarRecord("accuracy")
>>> record_max.is_comparable()
True
>>> record_min = MinScalarRecord("loss")
>>> record_min.is_comparable()
True

```

These records support the `Record` functionalities, and additional functionalities.
It is possible to use the `get_best_value` method to get the best value.

```pycon

>>> from minrecord import MaxScalarRecord, MinScalarRecord
>>> record_max = MaxScalarRecord("accuracy")
>>> record_max.update([(0, 42), (None, 45), (2, 46)])
>>> record_max.add_value(40)
>>> record_max.get_best_value()
46
>>> record_min = MinScalarRecord("loss")
>>> record_min.update([(0, 42), (None, 45), (2, 46)])
>>> record_min.add_value(50)
>>> record_min.get_best_value()
42

```

The record tracks the best value even if the best value is not store in the record.
Below is an example where the record's maximum size is set to 3.

```pycon

>>> from minrecord import MinScalarRecord
>>> record = MinScalarRecord("loss", max_size=3)
>>> record.update([(0, 42), (None, 45), (2, 46)])
>>> record.add_value(50)
>>> record.add_value(60)
>>> record.get_most_recent()
((2, 46), (None, 50), (None, 60))
>>> record.get_best_value()
42

```

Calling `get_best_value` on an empty record raises an `EmptyRecordError` exception.
It is possible to know if the last value added improved the best value or not by calling the
`has_improved` method.

```pycon

>>> from minrecord import MinScalarRecord
>>> record = MinScalarRecord("loss")
>>> record.add_value(50)
>>> record.has_improved()
True
>>> record.add_value(60)
>>> record.has_improved()
False
>>> record.add_value(42)
>>> record.has_improved()
True
>>> record.add_value(43)
>>> record.has_improved()
False

```

By definition, `has_improved` will return `True` if the last value is equal to the best value as
shown in the example below.

```pycon

>>> from minrecord import MinScalarRecord
>>> record = MinScalarRecord("loss")
>>> record.add_value(42)
>>> record.has_improved()
True
>>> record.add_value(42)
>>> record.has_improved()
True


```

:warning: Calling `has_improved` or `get_best_value` on non-comparable record raises
a `NotAComparableRecord` exception.

**:warning: Note about constructors:** the constructor of `ComparableRecord` works slightly
differently from `Record`.
If you pass some elements to the constructor, you also need to pass the `best_value` and `improved`
arguments to have the correct behavior.
It is not a mistake but the expected behavior as the best value can be outside of the values store
in the record.

```pycon

>>> from minrecord import MinScalarRecord
>>> # Incorrect behavior
>>> record = MinScalarRecord("loss", elements=[(0, 42), (None, 45), (2, 46)])
>>> record.add_value(50)
>>> record.get_best_value()
50
>>> # Correct behavior
>>> record = MinScalarRecord("loss")
>>> record.update([(0, 42), (None, 45), (2, 46)])
>>> record.add_value(50)
>>> record.get_best_value()
42

```

To automatically instantiate the record based on the input elements, you can use the `from_elements`
class method.

```pycon

>>> from minrecord import MinScalarRecord
>>> record = MinScalarRecord.from_elements("loss", elements=[(0, 42), (None, 45), (2, 46)])
>>> record.add_value(50)
>>> record.get_best_value()
42

```
