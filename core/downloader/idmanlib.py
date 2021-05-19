"""
Internet Download Manager Support.

This is made strictly for Windows.
"""

import comtypes.client as cc
import psutil

IDM_MID = ["{ECF21EAB-3AA8-4355-82BE-F777990001DD}", 1, 0]
DOWNLOAD_FOLDER = "Downloads"

idmlib, client = None, None
supported = lambda: bool(idmlib)

try:
    import comtypes.gen.IDManLib as idmlib
    cc.GetModule(IDM_MID)
    client = cc.CreateObject(idmlib.CIDMLinkTransmitter, None, None, idmlib.ICIDMLinkTransmitter2)
except:
    pass

def idm_process():
    """
    Get the active Internet Download Manager process.
    """
    for process in psutil.process_iter():
        if process.name().lower() == 'idman.exe':
            return process

within_range = lambda t, t1, t2: t1 <= t <= t2

def get_downloader_hook():
    """
    TODO & Coming soon: Inject a hook onto IDM to keep track of downloads so that \
        download start and end events can be easily detected for proper downloading.
    """

def idm_download(url, headers={}, form_data='', auth=(None,  None), filename='', download_folder=DOWNLOAD_FOLDER, lflag=5):
    """
    This is unstable due to its incapacity to wait for an existing download to complete.
    
    Due to this incapacity, all the episodes (in case of One Piece, all 900~) would download concurrently with IDM without anything to stop them. 
    Hence, an hook is being developed and this feature is marked as coming soon.
    """
    client.SendLinkToIDM(url, headers.get('referer', ''), headers.get('cookie', ''), form_data, auth[0] or '', auth[1] or '', download_folder, filename, lflag)
    downloader_process = idm_process()
    
    if not downloader_process:
        return 2
    
    return 0