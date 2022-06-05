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
        "anitopy==2.1.0",
        "click==8.0.4",
        "comtypes==1.1.11",
        "cssselect==1.1.0",
        "httpx==0.23.0",
        "lxml==4.8.0",
        "tqdm==4.62.3",
        "pycryptodomex==3.14.1",
        "regex==2022.3.15",
        "yarl==1.7.2",
        "pyyaml==6.0",
    ],
    entry_points="""
        [console_scripts]
        animdl=animdl.__main__:__animdl_cli__
    """,
)
