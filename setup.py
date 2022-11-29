from setuptools import find_packages, setup

from animdl.core.__version__ import __core__

with open("requirements.txt") as requirements_txt:
    requirements = requirements_txt.read().splitlines()

with open("console_entry_points.conf") as console_entry_points_conf:
    console_entry_points = console_entry_points_conf.read()


setup(
    name="animdl",
    version=__core__,
    author="kr@justfoolingaround",
    author_email="kr.justfoolingaround@gmail.com",
    description="A highly efficient, fast, powerful and light-weight anime downloader and streamer for your favorite anime.",
    packages=find_packages(),
    url="https://github.com/justfoolingaround/animdl",
    install_requires=requirements,
    entry_points=console_entry_points,
    include_package_data=True,
)
