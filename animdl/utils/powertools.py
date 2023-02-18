import functools
import importlib
import inspect
import pathlib

DO_NOTHING = lambda *args, **kwargs: True


class ProjectContext(dict):
    """
    Context for the project so that we can set
    and get variables across various different
    activities in the project.

    (This is just a hashable dict.)

    Usage:

    >>> ctx = ProjectContext({
    ...     "foo": "bar"
    })
    >>> ctx["foo"]

    (from else where in the project)

    >>> from xyz.abc import jkl
    >>> assert jkl.ctx["foo"] == "bar"
    """

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


ctx = ProjectContext()


def inactivated_iterator(genexp_iterator_factory=tuple):
    """
    A decorator, that ensures that the function
    returns another function, which when called,
    returns the actual result of the function.

    Done to ensure that a generator expression
    is not called before it is actually needed.

    Usage:

    >>> @inactivated_iterator(list)
    ... def foo(n):
    ...     yield from range(n)
    >>> foo(n=10)()
    ... [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            def inactivated_function():
                retval = func(*args, **kwargs)
                if inspect.isgenerator(retval):
                    return genexp_iterator_factory(retval)
                return retval

            return functools.partial(inactivated_function)

        return wrapper

    return decorator


def iterate_modules_from_path(path: pathlib.Path, package: str, *, exempt: list = None):
    """
    Module iterator from a path for lazy loading.
    """
    if exempt is None:
        exempt = []

    for module_path in path.glob("*/"):
        if module_path.name not in exempt:
            yield module_path, importlib.import_module(
                "." + module_path.name, package=package
            )
