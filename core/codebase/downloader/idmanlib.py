"""
Internet Download Manager Support.

This is made strictly for Windows.
"""

import time

IDM_MID = ["{ECF21EAB-3AA8-4355-82BE-F777990001DD}", 1, 0]
DOWNLOAD_FOLDER = "Downloads"

idmlib, client = None, None
supported = lambda: bool(idmlib)

try:
    import comtypes.client as cc
    cc.GetModule(IDM_MID)
    
    import comtypes.gen.IDManLib as idmlib
    client = cc.CreateObject(idmlib.CIDMLinkTransmitter, None, None, idmlib.ICIDMLinkTransmitter2)
except:
    pass

within_range = lambda t, t1, t2: t1 <= t <= t2

def idm_download(url, headers={}, form_data='', auth=(None,  None), filename='', download_folder=DOWNLOAD_FOLDER, lflag=5):    
    return client.SendLinkToIDM(url, headers.get('referer', ''), headers.get('cookie', ''), form_data, auth[0] or '', auth[1] or '', download_folder, filename, lflag)

def wait_until_download(url, headers={}, form_data='', auth=(None,  None), filename='', download_folder=DOWNLOAD_FOLDER):
    idm_download(url, headers, form_data, auth, filename.as_posix(), download_folder.as_posix(), lflag=5)
    while not (download_folder / filename).exists():
        """IDM doesn't save the file until download completion."""
        try:
            time.sleep(.5)
        except KeyboardInterrupt:
            return print("[IDM] Interrupted the wait for current download completion. Continuing with the next in queue.")