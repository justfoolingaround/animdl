import importlib
import pathlib


from ..helper import append_protocol

EXEMPT = [
    '__init__.py',
    '__pycache__'
]

__this_path__ = pathlib.Path('.').resolve()

def iter_providers(*, exempt=EXEMPT):
    for path in __this_path__.glob('*/'):
            if path.name not in exempt:
                yield importlib.import_module('.{.name}'.format(path), package=__name__), path.name

def get_provider(url, *, raise_on_failure=True):
    for provider_module, name in iter_providers():
        match = provider_module.REGEX.match(url)
        if match:
            return match, provider_module, name
    
    if raise_on_failure:
        raise Exception("Can't find a provider for the url {!r}.")

    return None, None, None

def get_appropriate(session, url, check=lambda *args: True):
    regex_match, provider_module, _ = get_provider(append_protocol(url))
    return provider_module.fetcher(session, url, check, match=regex_match)
