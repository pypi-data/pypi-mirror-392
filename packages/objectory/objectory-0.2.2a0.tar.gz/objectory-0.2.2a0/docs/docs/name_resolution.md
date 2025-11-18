# Name Resolution Mechanism

:book: Before to read this page, it is recommended to know how an object factory works.
This page introduces the name resolution mechanism (NRM) which is used to find the real full name of
the object that you want to load dynamically.

## Motivation

This section explains why the name resolution mechanism is important.
To instantiate dynamically an object with an object factory, you need to specify the name of the
object.
Then, the object factory will look at its internal registry to find where is the object associated
to the name that you gave.
A problem happens when there are several ways to instantiate an object.

Let's take the example of [PyTorch](https://pytorch.org/) –note that the motivation is not specific
to PyTorch and you can find similar situations in other libraries.
PyTorch is an open source machine learning framework that accelerates the
path from research prototyping to production deployment.
In particular, let's look at
the [`torch.nn.Linear`](https://pytorch.org/docs/stable/generated/torch.nn.Linear.html)
class.
According to the documentation, you can use this class in your code by writing something like:

```python
from torch.nn import Linear
```

It will work but if you print the class `Linear`, you will see that the real path to it is
not `torch.nn.Linear`.
The real path of the class `Linear` class is:

```python
torch.nn.modules.linear.Linear
```

Another way to import the class `Linear` is to write:

```python
from torch.nn.modules.linear import Linear
```

So there are at least two ways to import the class `Linear`:

- `from torch.nn import Linear`
- `from torch.nn.modules.linear import Linear`

Both approaches will give the same result.
Which one should you use? :thinking:

Choosing one approach is probably not a good idea because it will force all the users to use the
same approach which can be challenging in practice.
A solution is to use a name resolution mechanism which will allow using several approaches
to instantiate an object.
By default, the `objectory` library uses the real full name to register an object.
Each object is registered with its real full name, so in the PyTorch example, the class `Linear` is
registered with the name `torch.nn.modules.linear.Linear`.

The factory should understand that you can use `torch.nn.modules.linear.Linear` or `torch.nn.Linear`
to instantiate the class `Linear`.
If you give `torch.nn.Linear`, the name resolution mechanism should transform it
in `torch.nn.modules.linear.Linear`.

For the PyTorch library, the development team recommend to use `torch.nn.Linear` instead
of `torch.nn.modules.linear.Linear` because it will make your code more robust to some changes in
the package `torch.nn`.
The name resolution mechanism will allow you to do that because you do not have to give the real
full name of the object.
Internally, the factory uses `torch.nn.modules.linear.Linear` and it connects the
name `torch.nn.Linear` to `torch.nn.modules.linear.Linear` so specifying `torch.nn.Linear` is
equivalent to write `torch.nn.modules.linear.Linear`.

Another advantage of the name resolution mechanism is that you can specify only the object (class or
function) name.
Writing the full name of each object can be time-consuming.
The advantage of writing the full name is that there is no ambiguity of the object that you want to
instantiate if there are several objects with the same name.
However, it is possible to use the information about the registered objects in the factory to find
the object to use.
For example if you want to instantiate an object of class `X`, you can look at how many objects with
name `X` are registered in the factory.
The name resolution mechanism will work if there is a single match i.e. there is a single registered
object with the name `X`.
It will not work if there are several matches because the factory does not know which object to
choose.
In that case you will have to use the full name of the object to break the ambiguity.

If we continue with the previous example, you can use the query `Linear` to instantiate the class if
there is no other object with that name in the factory.
The name resolution mechanism will explore the names registered in the factory and will find it
matches with `torch.nn.modules.linear.Linear`.
It will associate `Linear` to `torch.nn.modules.linear.Linear`.

## How to use name resolution mechanism

It is quite easy to use the name resolution mechanism, and it can be used outside the object
factories.
The first input is the query name, and the second input is the set of possible object names.
In the object factory implementations, it is the set of registered object names.
For the following example, let's assume the set of possible object names
is: `{'torch.nn.modules.linear.Linear', 'my_package.MyClass'}`.
The name resolution mechanism will try to find the query name in the set of possible object names.
Let's assume that the query name is `'Linear'`.
To use the name resolution mechanism, you can write the following code:

```python
from objectory.utils import resolve_name

print(resolve_name("Linear", {"torch.nn.modules.linear.Linear", "my_package.MyClass"}))
```

*Output*:

```textmate
torch.nn.modules.linear.Linear
```

In this example, the resolved name is `'torch.nn.modules.linear.Linear'` because there is a
single object with the name `Linear` in the set.
Please read the next section to learn how the name resolution is done.
The name resolution mechanism returns `None` if it cannot find the name.

## How does the name resolution mechanism work?

The name resolution mechanism works in several steps. The inputs are a query name, and a set of
object names.
Then, the name resolution mechanism will try to find the full name of the object by using the
following sequential process:

- **Step 1.** The first step looks at if the query name is in the set of object names.
  If yes, it returns the query name because it can be directly used to instantiate the object.
  If no, it goes to the second step.
- **Step 2.** The second step looks at the potential matches to the query name.
  If there is a single match, it returns the matched object name because it can be directly used to
  instantiate the object.
  If there are multiple matches, it goes to the third step.
  This step is useful to manage the case where the user only specifies the object name.
  For example, it will work if the query name is `Linear` and the set of possible object names
  is: `{'torch.nn.modules.linear.Linear', 'my_package.MyClass'}`.
- **Step 3.** The last step tries to import the object.
  If the object can be imported, it returns the full name of the object.
  If the object cannot be imported, it returns `None`.
  This step is useful to manage the case where there are multiple ways to import an object.
  For example if the query name is `torch.nn.Linear`, it will find that the real full
  name is `torch.nn.modules.linear.Linear`.

## Matching mechanism

This section explains the matching mechanism used in the step 2 of the name resolution mechanism.
Similarly to the name resolution mechanism, the inputs of the matching mechanism are a query name,
and a set of object names.
The matching mechanism returns a set of matches.
First, the matching mechanism looks at if the query name is a valid python identifier.
You can read
this [page](https://data-flair.training/blogs/identifiers-in-python/#:~:text=A%20Python%20identifier%20can%20be,Uppercase%20letters%20(A%20to%20Z))
to learn more about the Python identifier.
If the query name is not a valid python identifier, the matching mechanism returns an empty set.
If the query name is a valid python identifier, it finds the matches between the query name, and
the python identifier of each object name in the set of object names.
It returns the set of matches.

## Ignore new import

It is possible to ignore the new imports in the third step by setting `allow_import=False`.
In some cases, we do not want to use an object which is not in the set of object names.
By default, the name resolution mechanism returns the full name of the object if the import was
successful in the third step.
If `allow_import=False`, the name resolution mechanism tries to import the object and check if the
name is in the set of object names.
If we use the example presented above on `torch.nn.Linear`, we can write something:

```python
from objectory.utils import resolve_name

print(
    resolve_name(
        "torch.nn.Linear", {"torch.nn.modules.linear.Linear"}, allow_import=False
    )
)
```

*Output*:

```textmate
torch.nn.modules.linear.Linear
```

The name resolution mechanism finds that the full name of `torch.nn.Linear`
is `torch.nn.modules.linear.Linear`.
If `torch.nn.modules.linear.Linear` is not in the set of object names, the name resolution mechanism
does not find the full name and returns `None`:

```python
from objectory.utils import resolve_name

print(resolve_name("torch.nn.Linear", {"something.my_linear"}, allow_import=False))
```

*Output*:

```textmate
None
```
