from .android import AndroidIntentVIEW
from .ffplay import FFPlay
from .mpv import CelluloidPlayer, IINAPlayer, MPVDefaultPlayer
from .vlc import VLCPlayer

player_mapping = {
    "mpv": MPVDefaultPlayer,
    "iina": IINAPlayer,
    "vlc": VLCPlayer,
    "celluloid": CelluloidPlayer,
    "ffplay": FFPlay,
    "android": AndroidIntentVIEW,
}
