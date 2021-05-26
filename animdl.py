"""
A one cli for all the anime.
"""

import shutil

import click

from core.clicore.commands import download, stream, continuation

commands = {
    'download': download.animdl_download,
    'continue': continuation.animdl_continue,
}

mpv = bool(shutil.which('mpv'))

if mpv:
    commands.update({'stream': stream.animdl_stream})

@click.group(commands=commands)
def __animdl_cli__():
    pass

if __name__  == '__main__':
    __animdl_cli__()