# Registry

The `Registry` can be used to register a class or a function.

## Register an object

This section explains the basics on how to register an object (class or function).
There are two approaches to register an object to the registry:

- by using the decorator `register`
- by using the function `register_object`

### Decorator `register`

You can use the decorator `register` to register an object to the registry.
For example if you want to register the class `ClassToRegister`, you can write:

```python
# file: my_package/my_module.py
from objectory import Registry

registry = Registry()


@registry.register()
class ClassToRegister:
    pass


print(registry.registered_names())
```

*Output*:

```textmate
{'my_package.my_module.ClassToRegister'}
```

The class `ClassToRegister` is registered with the name `my_package.my_module.ClassToRegister`.
You can see the registered names by using the function `registered_names`.
The function `registered_names` returns the set of registered names.

You can also use the decorator `register` to register a function:

```python
# file: my_package/my_module.py
from objectory import Registry

registry = Registry()


@registry.register()
def function_to_register(*args, **kwargs):
    pass


print(registry.registered_names())
```

*Output*:

```textmate
{'my_package.my_module.function_to_register'}
```

The function `function_to_register` is registered with the
name `my_package.my_module.function_to_register`.

### Function `register_object`

The decorator approach works well when you can change the source code, but it will not work if you
cannot modify the source code.
You cannot use the decorator `register` to register an object in a third party library.
To register a class or function from a third party library, you can use the
function `register_object`.
For example if you want to register the class `ClassToRegister` of the library `third_party`, you
can write the following lines:

```python
# file: my_package/my_module.py
from objectory import Registry
from third_party import ClassToRegister

registry = Registry()

registry.register_object(ClassToRegister)
```

Similarly to the decorator `register`, you can use the function `register_object` to register a
function:

```python
# file: my_package/my_module.py
from objectory import Registry
from third_party import function_to_register

registry = Registry()

registry.register_object(function_to_register)
```

:warning: It is not possible to register a lambda function.
Please use a regular python function instead.
The registry will raise the exception `IncorrectObjectFactoryError` if you try to register a lambda
function.

## Advanced object registration

This section presents some advanced features to register an object.

### Sub-registry

Previously we showed how to register an object to the registry, but all the objects will be
registered to the same registry which can be messy in some cases.
Instead, you can decide to use a hierarchical structure and to use sub-registries.
The registry will have a tree structure. `registry` is the main registry, and you can add some
sub-registries.
Each sub-registry works like the main registry.
In fact, the main registry and the sub-registries are implemented with the same class (`Registry`).
It is not a hard coded rule, but it is recommended to use one sub-registry for each "family" of
objects to group the similar objects.

If you want to register the class in the sub-registry `other`, you can write:

```python
# file: my_package/my_module.py
from objectory import Registry

registry = Registry()


@registry.other.register()
class ClassToRegister:
    pass


print(registry.registered_names())
print(registry.other.registered_names())
```

*Output*:

```textmate
{'other'}
{'my_package.my_module.ClassToRegister'}
```

You can check the registered objects in `registry` and `registry.other`.
The class `ClassToRegister` is registered into `registry.other` and not `registry`.
Note that the sub-registry `other` is registered to the main registry with the name `other`.
It means you cannot use the name `other` to register an object.
Each sub-registry is considered as a registered object in the parent registry.
The sub-registry `other` will be created if it does not exist, so you do not have to manually
register the new sub-registry.
It is possible to have a nested structure where you add a sub-registry to a sub-registry:

```python
from objectory import Registry

registry = Registry()


@registry.animal.cat.register()
class MyCat:
    pass


@registry.animal.bear.register()
class MyBear:
    pass
```

### Register all the child classes

In some cases, you may want to register a class and all its child classes.
Instead of doing manually, you can use the function `register_child_classes`.
This function will automatically register the given class and all its child classes.
It will find all the child classes and will add them to the registry.
It finds the child classes recursively, so it will also find the child classes of the child classes.

Let's imagine you have the following classes and you want to register them.

```python
# file: my_package/my_module.py
from objectory import Registry


class Foo:
    pass


class Bar(Foo):
    pass


class Baz(Foo):
    pass


class Bing(Bar):
    pass


registry = Registry()

# If you want to register Foo and all its child classes.
registry.register_child_classes(Foo)
print(registry.registered_names())

# If you want to register Bar and all its child classes.
registry.bar.register_child_classes(Bar)
print(registry.bar.registered_names())
```

*Output*:

```textmate
{'my_package.my_module.Foo', 'my_package.my_module.Baz',
 'my_package.my_module.Bing', 'my_package.my_module.Bar'}
{'my_package.my_module.Bing', 'my_package.my_module.Bar'}
```

By default, the function `register_child_classes` ignores all the abstract classes because you
cannot instantiate them.
If you want to also register the abstract classes, you can use the
argument `ignore_abstract_class=False`.
The following example shows how to register all the `torch.nn.Module` including the abstract
classes.

```python
import torch
from objectory import Registry

registry = Registry()
registry.register_child_classes(torch.nn.Module, ignore_abstract_class=False)
```

### Customized name

By default, the registry uses the full name of the object to identify the object in the registry.
It is possible to customize the name used to register an object.
For example if you want to register the class `ClassToRegister` with the name `my_class`, you can
write the following code:

```python
# file: my_package/my_module.py
from objectory import Registry

registry = Registry()


@registry.register("my_class")
class ClassToRegister:
    pass


registry.register_object(ClassToRegister, "my_class")
# or
registry.register_object(ClassToRegister, name="my_class")
```

One of the advantage of using customizable names is that you can define shorter name: `my_class` is
shorter than `my_package.my_module.ClassToRegister`.
But using customizable names is not a free lunch, and it has a cost: it will be your responsibility
to manage the names to avoid the conflicts.
If two objects are registered with the same name, only the last object will be registered.
For this reason, it is recommended to use the full name (default) because the full name is unique.

Please think carefully about the pros and cons of this feature before to use it.
In most of the cases you probably do not need it.
Keep in mind that **with power comes responsibility.**

## Factory

The reserved keywords are:

- `_target_`: the class/function to instantiate
- `_init_`: the constructor to use to instantiate a class

## Remove objects

In the previous sections, we explain how to add objects to the registry.
In this section, we will explain how to remove them.

### Remove all the objects

If you want to remove all the objects in a registry, you can use the function `clear`:

```python
from objectory import Registry

registry = Registry()


class ClassToRegister:
    pass


registry.register_object(ClassToRegister)
print(registry.registered_names())

registry.clear()
print(registry.registered_names())
```

*Output*:

```textmate
set()
```

This function remove all the registered objects including the sub-registries.
For example, if the registry has a sub-registry `other`, this line of code will also clear the
sub-registry `other`.
You can use this function on a sub-registry to clear only this sub-registry.
For example, you can use the following command to remove all the classes and functions registered in
the sub-registry `other`:

```python
from objectory import Registry

registry = Registry()

registry.other.clear()
print(registry.other.registered_names())
```

*Output*:

```textmate
set()
```

Note that by default, the function `clear` removes the sub-registries from the current registry but
it does not clear the sub-registries.

```python
# file: my_package/my_module.py
from objectory import Registry

registry = Registry()


class ClassToRegister:
    pass


registry.other.register_object(ClassToRegister)
registry_other = registry.other

registry.clear()
print(registry.registered_names())
print(registry_other.registered_names())
```

*Output*:

```textmate
set()
{'my_package.my_module.ClassToRegister'}
```

To also clear all the sub-registries, you can set `nested=True` and the sub-registry `other` is also
cleared.

```python
# file: my_package/my_module.py
from objectory import Registry

registry = Registry()


class ClassToRegister:
    pass


registry.other.register_object(ClassToRegister)
registry_other = registry.other

registry.clear(nested=True)
print(registry.registered_names())
print(registry_other.registered_names())
```

*Output*:

```textmate
set()
set()
```

### Remove a specific object

The function `clear` is useful to remove all the objects in the registry, but it does not work if
you want to only remove a registered object and keep all the other registered objects.

```python
# file: my_package/my_module.py
from objectory import Registry

registry = Registry()


@registry.register()
class ClassToRegister1:
    pass


@registry.register()
class ClassToRegister2:
    pass


print(registry.registered_names())
registry.unregister("my_package.my_module.ClassToRegister1")
print(registry.registered_names())
```

*Output*:

```textmate
{'my_package.my_module.ClassToRegister1', 'my_package.my_module.ClassToRegister2'}
{'my_package.my_module.ClassToRegister2'}
```

If the object name is unique in the registry, you can only specify the object name:

```python
from objectory import Registry

registry = Registry()

registry.unregister("ClassToRegister")
# is equivalent to
registry.unregister("my_package.my_module.ClassToRegister")
```

Please read the [name resolution](name_resolution.md) documentation to learn more about this
feature.

## Filters

### Child class filter

Usually you want to control the objects that you want to add to the registry.
For example, it is usually a good idea to register similar objects in the same registry.
A usual scenario is to define a base class, and then register only the child classes of the base
class.
For example if you want to register `torch.nn.Module`, you probably want to check that the object is
a `torch.nn.Module` before to register it.
Let's imagine you want to register only `torch.nn.Module` in the sub-registry `other`.

```python
import torch
from objectory import Registry

registry = Registry()

registry.set_class_filter(torch.nn.Module)
registry.register_object(torch.nn.Linear)
registry.register_object(torch.nn.Conv2d)
...
```

You can only register classes that inherits torch.nn.Module in the sub-registry `other`.
If you try to register a class which is not a child class, the registry will raise the
exception `IncorrectObjectFactoryError`:

```python
import torch
from objectory import Registry

registry = Registry()


class Foo:
    pass


registry.set_class_filter(torch.nn.Module)
registry.register_object(Foo)
```

The previous example will raise an exception because `Foo` is not a child class
of `torch.nn.Module`.
To unset the class filter, you can set it to ``None``:

```python
from objectory import Registry

registry = Registry()
registry.set_class_filter(None)
```

:warning: Note that the class filter is only used when you try to register a new object.
It will not filter the existing objects into the registry.
You can look at the following example:

```python
# file: my_package/my_module.py
import torch

from objectory import Registry


class Foo:
    pass


registry = Registry()
registry.register_object(Foo)
print(registry.registered_names())

registry.set_class_filter(torch.nn.Module)
registry.register_object(torch.nn.Linear)
print(registry.registered_names())
```

*Output*:

```textmate
{'my_package.my_module.Foo'}
{'my_package.my_module.Foo', 'torch.nn.Linear'}
```

You can see that the class `my_package.my_module.Foo` is still registered after the filter is set
to `torch.nn.Module`.
It is because this class was added before to set the class filter.
If you want to filter all the objects before to add them to the registry, please set the class
filter before to register the first object.
It will guarantee that all the registered objects are inherited from the filtered class.

### Clear all filters

You can remove all the filters of a registry by using the function `clear_filters`:

```python
from objectory import Registry

registry = Registry()
registry.clear_filters()
```

By default, the function `clear_filters` removes the filters on the current registry but not the
filters of the sub-registries.
To also remove the filters of all the sub-registries, you can set `nested=True`:

```python
from objectory import Registry

registry = Registry()
registry.clear_filters(nested=True)
```
