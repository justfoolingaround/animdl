"""
Internet Download Manager Support.

This is made strictly for Windows.
"""

import pathlib
import time
import typing
from collections import namedtuple

import rich

authentication = namedtuple(
    "authentication", "username password", defaults=(None, None)
)


idmlib, idmlib_object = None, None


try:
    from comtypes import client

    idmlib = client.GetModule(["{ECF21EAB-3AA8-4355-82BE-F777990001DD}", 1, 0])

    idmlib_object = client.CreateObject(
        idmlib.CIDMLinkTransmitter, None, None, idmlib.ICIDMLinkTransmitter2
    )
except Exception:
    pass


def supported():
    return bool(idmlib)


def idm_download(
    url: str,
    *,
    headers: typing.Optional[typing.Dict[str, str]] = None,
    form_data: typing.Optional[str] = None,
    auth: authentication = authentication(),
    filename: typing.Optional[str] = None,
    download_folder: pathlib.Path = pathlib.Path("."),
    lflag: int = 5,
):
    return idmlib_object.SendLinkToIDM(
        url,
        headers.get("referer"),
        headers.get("cookie"),
        form_data,
        auth.username,
        auth.password,
        download_folder.resolve(strict=True).as_posix(),
        filename,
        lflag,
    )


def wait_until_download(
    url,
    download_folder: pathlib.Path,
    headers=None,
    form_data=None,
    auth=authentication(),
    filename=None,
):
    idm_download(
        url,
        headers=headers,
        form_data=form_data,
        auth=auth,
        filename=filename,
        download_folder=download_folder,
        lflag=5,
    )

    if filename is None:
        return

    while not (download_folder / filename).exists():
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            console = rich.get_console()

            console.print(
                "[bold red]Detected KeyboardInterrupt[/], continue or terminate?",
            )

            if console.input("[C/t]: ").lower() == "t":
                raise

            return
