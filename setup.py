from setuptools import setup, find_packages
from animdl.core.__version__ import __core__

setup(
    name="animdl",
    version=__core__,
    author="kr@justfoolingaround",
    author_email="kr.justfoolingaround@gmail.com",
    description="A highly efficient, fast, powerful and light-weight anime downloader and streamer for your favorite anime.",
    packages=find_packages(),
    url="https://github.com/justfoolingaround/animdl",
    keywords=[
        "stream",
        "anime",
        "download",
        "anime-downloader",
        "twist",
        "9anime",
        "gogoanime",
        "animepahe",
        "4anime",
        "anime-streamer",
        "fouranime",
        "animixplay",
    ],
    install_requires=[
        "anitopy",
        "click",
        "comtypes",
        "cssselect",
        "httpx==0.22.0",
        "pyyaml",
        "yarl",
        "lxml",
        "tqdm",
        "regex==2021.10.8",
        "pycryptodomex",
    ],
    entry_points="""
        [console_scripts]
        animdl=animdl.__main__:__animdl_cli__
    """,
)
