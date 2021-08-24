from setuptools import setup, find_packages
from animdl.core.__version__ import __core__

setup(
    name='animdl',
    version=__core__,
    author='kr@justfoolingaround',
    author_email='kr.justfoolingaround@gmail.com',
    description='A highly efficient, fast, powerful and light-weight anime downloader and streamer for your favorite anime.',
    packages=find_packages(),
    url='https://github.com/justfoolingaround/animdl-install',
    keywords=['stream', 'anime', 'download', 'anime-downloader', 'twist', '9anime',
              'gogoanime', 'animepahe', '4anime', 'anime-streamer', 'fouranime', 'animixplay'],
    install_requires=[
        'click',
        'comtypes',
        'httpx',
        'yarl',
        'lxml',
        'tqdm',
        'pycryptodomex',
    ],
    entry_points='''
        [console_scripts]
        animdl=animdl.__main__:__animdl_cli__
    '''
)
