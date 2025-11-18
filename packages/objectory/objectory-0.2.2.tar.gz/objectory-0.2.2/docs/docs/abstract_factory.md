# Abstract Factory

This page presents the `AbstractFactory` metaclass which implement an
[abstract factory](https://refactoring.guru/design-patterns/abstract-factory) design pattern.
The abstract factory is a creational design pattern that lets you produce families of related
objects without specifying their concrete classes.
This design pattern is also known as "Factory of Factories" because it is a "super-factory" which
creates other factories.
This metaclass proposes an implementation for creating a factory of related objects without
explicitly specifying their classes.
Each generated factory can instantiate the objects as per the Factory pattern.

## Create a factory

The `AbstractFactory` metaclass is not a factory, but it contains the blueprint on how to build a
factory.
To create a factory, you will define a base class.
This class is used to register the other classes but also to define the common interface of the
factory.
In the following of the documentation, we will call this class the base factory class.
The example below shows the minimal implementation of a base class:

```python
from objectory import AbstractFactory


class BaseClass(metaclass=AbstractFactory):
    pass
```

The base class should inherit the `AbstractFactory` metaclass.
This metaclass will implement the factory mechanism to the base class.
The base class can implement functions and attributes like a regular python class.
It can also be an abstract class or not.

## Register an object

This section explains the basics on how to register an object to a factory.
It is possible to register a function.
This section assumes you already created a factory as explained above.
There are two approaches to register an object to the factory:

- by using the inheritance (only for class)
- by using the `register_object` function (both class and function)

### Inheritance

The recommended approach to register a class to the factory is to use the inheritance.
Every time that you create a new child class of the base factory class, the child class is
automatically registered to the factory.
For example, you can define the `Child1Class` class with the following implementation:

```python
from objectory import AbstractFactory


class BaseClass(metaclass=AbstractFactory):
    pass


class Child1Class(BaseClass):
    pass
```

When the `Child1Class` class is created, it is automatically added to the `BaseClass` factory.
The developer does not have to write any additional line to register the class.
It is possible to define more complex child classes with a constructor or any functions/attributes.
For example, you can define the `Child2Class` class with the following implementation:

```python
class Child2Class(BaseClass):
    def __init__(self, dim: int):
        self.dim = dim
```

Similarly, any grand child class of the base factory class is automatically registered to the
factory.
In the following example, the `Child3Class` class which inherits from `Child1Class` class will be
added to the `BaseClass` factory:

```python
class Child3Class(Child1Class):
    pass
```

### `register_object` function

The inheritance approach works when it is possible to modify the source code of the classes because
each registered need to inherit from the base factory class.
However, it is not possible to do that in particular when the code depends on a third party library.
To overcome this limitation, it is possible to use the `register_object` function to manually
register some classes that are defined outside the project.

Let's take the example of [PyTorch](https://pytorch.org/).
PyTorch is an open source machine learning framework.
To define a machine learning model in PyTorch, you can implement a new class that inherits from
the `torch.nn.Module` class.
PyTorch also provides many module implementations.
If you want to build a factory that includes both your module implementations and the PyTorch ones,
you can do it by using the inheritance and the `register_object` function.
First, you need to define the base factory class:

```python
import torch
from objectory import AbstractFactory


class BaseModule(torch.nn.Module, metaclass=AbstractFactory):
    pass


class MyModule1(BaseModule):
    pass


class MyModule2(BaseModule):
    pass
```

Then you can register some modules implemented in PyTorch.
For example if you want to register the class `torch.nn.Linear` to the factory of `BaseModule`, you
can write the following lines:

```python
import torch

BaseModule.register_object(torch.nn.Linear)
```

The `register_object` function can be used to register a class but also a function.
To be consistent with the factory idea, you should **only register functions that returns an object
that is compatible with the common interface of the factory**.
Note that no warning will be raised if you do not follow this rule, but it will be your
responsibility to manage this situation.
Please keep in mind that **with power comes responsibility**.
The following example shows how to register a function:

```python
import torch


def my_nodule(input_size: int, output_size: int) -> torch.nn.Module:
    return torch.nn.Sequential(
        torch.nn.Linear(input_size, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, output_size),
    )


BaseModule.register_object(my_nodule)
```

Another approach to register a function is to use the decorator `register`:

```python
import torch
from objectory import register


@register(BaseModule)
def my_nodule(input_size: int, output_size: int) -> torch.nn.Module:
    return torch.nn.Sequential(
        torch.nn.Linear(input_size, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, output_size),
    )
```

The argument of the decorator is the base factory class where the function will be registered.

:warning: It is not possible to register a lambda function.
Please use a regular python function instead.
The registry will raise the exception `IncorrectObjectFactoryError` if you try to register a lambda
function.

## Registered objects

### Inheritors

Sometimes it is important to know what are the registered objects to the factory.
You can see the list of the objects that are registered to the base class by using the
attribute `inheritors`.
This attribute contains the full name of the class as well as the class.
If you print the value of `inheritors`,

```python
print(BaseClass.inheritors)
```

*Output:*

```textmate
{
  "my_package.base.BaseClass": <class "my_package.base.BaseClass">,
  "my_package.child1.Child1Class": <class "my_package.child1.Child1Class">,
  "my_package.child2.Child2Class": <class "my_package.child2.Child2Class">,
  "my_package.child3.Child3Class": <class "my_package.child3.Child3Class">
}
```

This example assumes that the `BaseClass` is written in the file `my_package/base.py`
and `Child<X>Class` is written in the file `my_package/child<X>.py`.

Note that the base class and all its children classes have the attribute `inheritors` so you can
check the registered objects with any of these classes:

```python
print(Child1Class.inheritors)
print(Child2Class.inheritors)
```

*Output:*

```textmate
{
  "my_package.base.BaseClass": <class "my_package.base.BaseClass">,
  "my_package.child1.Child1Class": <class "my_package.child1.Child1Class">,
  "my_package.child2.Child2Class": <class "my_package.child2.Child2Class">,
  "my_package.child3.Child3Class": <class "my_package.child3.Child3Class">
}
{
  "my_package.base.BaseClass": <class "my_package.base.BaseClass">,
  "my_package.child1.Child1Class": <class "my_package.child1.Child1Class">,
  "my_package.child2.Child2Class": <class "my_package.child2.Child2Class">,
  "my_package.child3.Child3Class": <class "my_package.child3.Child3Class">
}
```

The key of each object is the full name of the object.
If you register two objects with the same full class name (package name + module name + class name),
only the last object will be registered.
It is the responsibility of the user to manage the object name to avoid duplicate.

If you have registered some functions, you should see them in the inheritors.
For example if you have registered the function `my_nodule` in the `BaseModule`, you should see
something like: `'my_package.nodule.my_nodule': <function my_nodule at 0x...>`.

### Missing objects

To be added to the factory, an object has to be loaded at least one time.
The objects are automatically registered when they are loaded the first time.
An object which is never loaded will never be registered.
If you do not see an object in the list of inheritors, it is probably because it was not loaded.
First, verify that the object inherits from the base factory class or the `register` function is
called.
Then, check if the python module with the object is loaded at least one time.

A solution to this problem is to write the child classes in the same python module that the base
factory class.
However, this solution is not always good or possible.
When there is a lot of objects, it is usually better to write them in several python modules.

Let's assume the following situation where each class is written in a different python module.
The package should have the following structure:

```textmate
my_package/
    __init__.py
    base.py
    child1.py
    child2.py
```

A solution is to import the child classes in the `__init__.py`. The file `__init__.py` should have
the following lines

```python
from my_package import child1
from my_package import child2
```

Another solution is to use the [import package tool](#import-a-package).

## Factory

This section explains how to instantiate dynamically a class registered in a `AbstractFactory`.
One of the operation done by the `AbstractFactory` metaclass is to add the `factory` function to the
base factory class and all its child classes.
This function can instantiate any registered class given its configuration.
The signature of the`factory` function is:

```python
def factory(cls, _target_: str, *args, _init_: str = "__init__", **kwargs): ...
```

where `*args` and `**kwargs` are the parameters of the object to instantiate.
The input `_target_` is used to define the name of the object to instantiate and `_init_` indicates
the function used to create the object.
The following sections will explain the role of each parameter and how to use them.

### Target object

One of the key features of the `factory` function is that you can specify the name of the object
that you want to instantiate.
The `_target_` input is used to define the name of the object to instantiate.
For example if you want to create an  `Child1Class` object, you can write:

```python
my_obj = BaseClass.factory("my_package.child1.Child1Class")
```

When you instantiate an object, you can also specify the arguments.
For example if you want to create a `Child2Class` object with 10 layers, you can write:

```python
my_obj = BaseClass.factory("my_package.child2.Child2Class", num_layers=10)
```

Sometimes it can be time consuming to write the full class name.
If the class name is unique, you can instantiate the object by only specifying the class name.
In the previous example, instead of the full class name (`my_package.child1.Child1Class`) you can
specify only the class name (`Child1Class`):

```python
my_obj = BaseClass.factory("Child1Class")
```

The second approach is easier to use, but it forces each class name to be unique.
Under the hood, the factory uses the [name resolution mechanism](name_resolution.md) to find the
path where the class is.
If the class name is not unique, the name resolution mechanism will not be able to instantiate the
object because of the ambiguity.
If several classes have the same name, you need to specify the full name to break the ambiguity.

Let's imagine the case where there are two classes with the same name `Linear`.

```python
import torch

# Register the class Linear from PyTorch
BaseModule.register_object(torch.nn.Linear)


# Register another class Linear
class Linear(BaseModule):
    pass
```

There is no problem to register to class with the same class name because their full class name are
different (`torch.nn.modules.linear.Linear` vs `__main__.Linear`).
Please read the [name resolution mechanism documentation](name_resolution.md) to learn why the real
full name of `torch.nn.linear.Linear` is `torch.nn.modules.linear.Linear`.
If you want to instantiate the `Linear` class from PyTorch, you will need to give the full class
name:

```python
my_obj = BaseModule.factory("torch.nn.Linear", in_features=8, out_features=6)
```

If you want to instantiate the local `Linear` class, you will need to give the full class name:

```python
my_obj = BaseModule.factory("__main__.Linear", in_features=8, out_features=6)
```

If you only specify `Linear`, the factory does not know what class you want to instantiate and will
raise an error.

```python
my_obj = BaseModule.factory("Linear", in_features=8, out_features=6)
# Raise the error: factory.error.UnregisteredObjectFactoryError: Unable to create the object Linear.
# Registered objects of BaseModule are {'__main__.Linear', 'torch.nn.modules.linear.Linear'}
```

If several classes have the same name, the only solution is to specify the full class name.
Similarly to class, it is possible to specify the name of the function to call.
For example if you want to call the `my_nodule` function previously defined, you can write:

```python
net = BaseModule.factory("my_package.nodule.my_nodule", input_size=4, output_size=12)
```

Finally, you can call the `factory` function with any class that inherits from the base factory
class:

```python
my_obj = BaseClass.factory("my_package.child1.Child1Class")
# or
my_obj = Child1Class.factory("my_package.child1.Child1Class")
# or
my_obj = Child2Class.factory("my_package.child1.Child1Class")
```

### Initialization function

By default, the `factory` function calls the function `__init__` of a class to create an object.
You can also create an object by using a class method.
You can use the keyword to `_init_` to specify the function to use to create the object.
The default value of this keyword is `"__init__"` so you do not need to change it if you call the
default constructor.
Note the initialization function input is only available for the classes.
This input is ignored when you call a function to instantiate an object.

Let's define a new class that has a class method to create an object:

```python
# file: my_package/child4.py
class Child4Class(BaseClass):
    def __init__(self, dim: int):
        self.dim = dim

    @classmethod
    def default(cls):
        return cls(dim=256)
```

Then, you can create an `Child4Class` object with the default method with the following command:

```python
my_obj = BaseClass.factory(
    _target_="my_package.child4.Child4Class",
    _init_="default",
)
```

### Instantiate an unregistered object

The `AbstractFactory` metaclass provides some functionalities to dynamically instantiate an
unregistered object.
This feature is enabled by the [name resolution mechanism](name_resolution.md).
It is useful to instantiate an object which is not defined in a third party package.
For example if you want to load the class `torch.nn.GRU`, you can use the following line:

```python
net = BaseClass.factory("torch.nn.GRU", input_size=4, hidden_size=12)
```

It is not necessary to register this class to instantiate it.
If the `_target_` value is a module path, the `factory` function tries to import it.
If the import is successful, the object is registered in the factory, so it is possible to reuse it
later.
This functionality is also useful when an object can be initialized by specifying several ways.
Due to some imports in the `__init__.py` of some packages, some objects have several module paths.
For example, a GRU object in PyTorch can be created by using the two approaches below:

```python
net = BaseClass.factory("torch.nn.GRU", input_size=4, hidden_size=12)
net = BaseClass.factory("torch.nn.modules.rnn.GRU", input_size=4, hidden_size=12)
```

Please read the [name resolution mechanism](name_resolution.md) documentation to learn more about
it.

## Tools

This section presents some useful tools for the `AbstractFactory` metaclass.

### Register all the child classes

In some cases, you may want to register a class and all its child classes.
Instead of doing manually, you can use the function `register_child_classes`.
This function will automatically register the given class and all its child classes.
It will find all the child classes and will add them to the registry.
It finds the child classes recursively, so it will also find the child classes of the child classes.

Let's imagine you have the following classes, and you want to register them to the base class
factory `BaseClass`:

```python
# file: my_package/my_module.py
from objectory.abstract_factory import register_child_classes


class Foo:
    pass


class Bar(Foo):
    pass


class Baz(Foo):
    pass


class Bing(Bar):
    pass


register_child_classes(BaseClass, Foo)
print(BaseClass.inheritors)
```

*Output*:

```textmate
{
  'my_package.my_module.Foo',
  'my_package.my_module.Baz',
  'my_package.my_module.Bing',
  'my_package.my_module.Bar'
}
```

By default, the function `register_child_classes` ignores all the abstract classes because you
cannot instantiate them.
If you want to also register the abstract classes, you can use the
argument `ignore_abstract_class=False`.
The following example shows how to register all the `torch.nn.Module` including the abstract
classes.

```python
import torch
from objectory.abstract_factory import register_child_classes

register_child_classes(BaseClass, torch.nn.Module, ignore_abstract_class=False)
```

## Error messages

This section lists some of the most frequent error messages and explain how to fix the error.
If you try to instantiate a class that is not registered (e.g. `Child3Class`), you will see the
following error message:

```text
objectory.abstract_factory.UnregisteredClassAbstractFactoryError: Unable to create
the class Child3Class. Verify that the class was added to the __init__.py file of its module.
Registered child classes of BaseClass are ["child1class", "child2class"]
```

The error shows the list of classes that are registered
(`["my_package.base.BaseClass", "my_package.child1.Child1Class", "my_package.child2.Child2Class"]`
in this example).
If your class does not appear in that list, it is probably because your class was never imported and
registered.
Keep in mind that each class has to be loaded at least once to be registered.
The error `AbstractClassAbstractFactoryError` will be raised if you try to instantiate an abstract
class because an abstract class cannot be instantiated.

## Limitations

The  `AbstractFactory` metaclass adds some attributes and methods to the classes.
To avoid potential conflicts with the other classes, all the non-public attributes and functions
starts with `_abstractfactory_****` where `****` is the name of the attribute or the function.
As presented above, you cannot define the following methods:

- `inheritors`
- `factory`
- `register_object`
- `unregister`
