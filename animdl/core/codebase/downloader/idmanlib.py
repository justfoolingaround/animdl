"""
Internet Download Manager Support.

This is made strictly for Windows.
"""

import time

IDM_MID = ["{ECF21EAB-3AA8-4355-82BE-F777990001DD}", 1, 0]
DOWNLOAD_FOLDER = "Downloads"

idmlib, client = None, None


def supported():
    return bool(idmlib)


try:
    import comtypes.client as cc

    idmlib = cc.GetModule(IDM_MID)

    client = cc.CreateObject(
        idmlib.CIDMLinkTransmitter, None, None, idmlib.ICIDMLinkTransmitter2
    )
except BaseException:
    pass


def within_range(t, t1, t2):
    return t1 <= t <= t2


def idm_download(
    url,
    headers={},
    form_data="",
    auth=(None, None),
    filename="",
    download_folder=DOWNLOAD_FOLDER,
    lflag=5,
):
    return client.SendLinkToIDM(
        url,
        headers.get("referer", ""),
        headers.get("cookie", ""),
        form_data,
        auth[0] or "",
        auth[1] or "",
        download_folder,
        filename,
        lflag,
    )


def wait_until_download(
    url,
    headers={},
    form_data="",
    auth=(None, None),
    filename="",
    download_folder=DOWNLOAD_FOLDER,
):
    idm_download(
        url, headers, form_data, auth, filename, download_folder.as_posix(), lflag=5
    )
    while not (download_folder / filename).exists():
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            return print(
                "[IDM] Interrupted the wait for current download completion. Continuing with the next in queue."
            )
