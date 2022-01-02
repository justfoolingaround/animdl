import importlib
import pathlib

EXEMPT = [
    '__init__.py',
    '__pycache__'
]


__this_path__ = pathlib.Path('.').resolve()

def iter_extractors(*, exempt=EXEMPT):
    for path in __this_path__.glob('*/'):
        if path.name not in exempt:
            yield importlib.import_module('.{.name}'.format(path), package=__name__), path.name
