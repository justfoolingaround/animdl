import importlib
import pathlib

EXEMPT = [
    '__init__.py',
    '__pycache__'
]

try:
    __this_path__ = pathlib.Path(__path__[0])
except:
    __this_path__ = pathlib.Path()

def iter_providers(*, exempt=EXEMPT):
    for path in __this_path__.glob('*/'):
            if path.name not in exempt:
                yield importlib.import_module('.{.name}'.format(path), package=__name__), path.name

def get_provider(url, *, raise_on_failure=True):
    for provider_module, name in iter_providers():
        if provider_module.REGEX.match(url):
            return provider_module, name
    
    if raise_on_failure:
        raise Exception("Can't find a provider for the url {!r}.")

    return None, None

def get_appropriate(session, url, check=lambda *args: True):
    return get_provider(url)[0].fetcher(session, url, check)
