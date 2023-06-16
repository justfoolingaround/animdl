import importlib.metadata

try:
    __core__ = importlib.metadata.version("animdl")
except importlib.metadata.PackageNotFoundError:
    import pathlib

    from animdl.utils.optopt import regexlib

    __core__ = regexlib.search(
        r'name = "animdl"\nversion = "(.+?)"',
        (pathlib.Path(__file__).parent.parent / "pyproject.toml").read_text(),
    ).group(1)
