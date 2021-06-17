"""
A one cli for all the anime.
"""

import shutil

import click

from core.clicore.commands import download, stream, continuation, grab, schedule
from core.config import MPV_EXECUTABLE

commands = {
    'download': download.animdl_download,
    'continue': continuation.animdl_continue,
    'grab': grab.animdl_grab,
    'schedule': schedule.animdl_schedule
}

mpv = bool(shutil.which(MPV_EXECUTABLE))

if mpv:
    commands.update({'stream': stream.animdl_stream})

@click.group(commands=commands)
def __animdl_cli__():
    pass

if __name__  == '__main__':
    __animdl_cli__()