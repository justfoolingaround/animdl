"""
A one cli for all the anime.
"""

import shutil

import click

from core.clicore.commands import download, stream

commands = {
    'download': download.animdl_download,
}

mpv = bool(shutil.which('mpv'))

if mpv:
    commands.update({'stream': stream.animdl_stream})

@click.group(commands=commands)
def __animdl_cli__():
    pass

if __name__  == '__main__':
    __animdl_cli__()