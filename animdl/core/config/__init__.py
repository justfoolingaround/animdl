import os
import sys
import warnings
from pathlib import Path

import yaml


def merge_dicts(dict1, dict2):
    for k, v in dict1.items():
        if isinstance(v, dict):
            merge_dicts(v, dict2.setdefault(k, {}))
        else:
            if k not in dict2:
                dict2[k] = v
    return dict2


def get_existent_path(*user_paths):
    for _ in user_paths:
        if not isinstance(_, Path):
            _ = Path(_)
        if _.exists():
            return _


if sys.platform == "win32":
    USERPROFILE_ANIMDL_PATH = (
        Path(os.getenv("LOCALAPPDATA", ".")) / ".config" / "animdl" / "config.yml"
    )
    OLD_DEPRECATED_PATH = Path(os.getenv("USERPROFILE")) / ".animdl" / "config.yml"

    if OLD_DEPRECATED_PATH.exists():
        if not USERPROFILE_ANIMDL_PATH.exists():
            warnings.warn(
                f"The config file path @ {OLD_DEPRECATED_PATH.as_posix()} is deprecated and will be removed in the future. "
                f"Please migrate to {USERPROFILE_ANIMDL_PATH.as_posix()}. "
                f"This is not done automatically because this project does not want to mess with your files.",
            )
            USERPROFILE_ANIMDL_PATH = OLD_DEPRECATED_PATH

else:
    USERPROFILE_ANIMDL_PATH = (
        Path(os.getenv("HOME", ".")) / ".config" / "animdl" / "config.yml"
    )

CONFIGURATION_FILE_PATH = get_existent_path(
    os.getenv("ANIMDL_CONFIG", "./animdl_config.yml"),
    "/animdl_config.yml",
    USERPROFILE_ANIMDL_PATH,
)

DEFAULT_CONFIG = {
    "default_provider": "allanime",
    "site_urls": {
        "9anime": "https://9anime.pl/",
        "allanime": "https://allanime.site/",
        "animekaizoku": "https://animekaizoku.com/",
        "animeout": "https://animeout.xyz/",
        "animepahe": "https://animepahe.com/",
        "animeonsen": "https://animeonsen.xyz/",
        "animexin": "https://animexin.xyz/",
        "animixplay": "https://animixplay.to/",
        "animtime": "https://animtime.com/",
        "crunchyroll": "http://www.crunchyroll.com/",
        "kawaiifu": "https://kawaiifu.com/",
        "gogoanime": "https://gogoanime.cm/",
        "haho": "https://haho.moe/",
        "hentaistream": "https://hstream.moe/",
        "kamyroll_api": "https://kamyroll.herokuapp.com/",
        "tenshi": "https://tenshi.moe/",
        "nyaasi": "https://nyaa.si/",
        "twist": "https://twist.moe/",
        "zoro": "https://zoro.to/",
    },
    "quality_string": "best[subtitle]/best",
    "default_player": "mpv",
    "players": {
        "mpv": {
            "executable": "mpv",
            "opts": [],
        },
        "vlc": {
            "executable": "vlc",
            "opts": [],
        },
        "iina": {
            "executable": "iina",
            "opts": ["--keep-running"],
        },
        "celluloid": {
            "executable": "celluloid",
            "opts": [],
        },
        "ffplay": {
            "executable": "ffplay",
            "opts": [],
        },
        "android": {
            "executable": "am",
            "opts": [],
        },
    },
    "schedule": {
        "site_url": "https://graphql.anilist.co/",
        "date_format": "%b. %d, %A",
        "time_format": "%X",
    },
    "download_auto_retry": 300,
    "ffmpeg": {
        "executable": "ffmpeg",
        "hls_download": False,
        "submerge": True,
    },
    "discord_presence": False,
    "fzf": {
        "executable": "fzf",
        "opts": [],
        "state": False,
    },
    "download_directory": ".",
    "check_for_updates": True,
    "force_streaming_quality_selection": True,
    "aniskip": False,
    "superanime": {"return_all": False, "type_of": "sub"},
}

CONFIG = DEFAULT_CONFIG

if CONFIGURATION_FILE_PATH is not None:
    with open(CONFIGURATION_FILE_PATH, "r") as conf:
        CONFIG = merge_dicts(DEFAULT_CONFIG, yaml.load(conf, Loader=yaml.SafeLoader))

SITE_URLS = CONFIG.get("site_urls", {})

NINEANIME = SITE_URLS.get("9anime")
ALLANIME = SITE_URLS.get("allanime")
ANIMEKAIZOKU = SITE_URLS.get("animekaizoku")
ANIMEOUT = SITE_URLS.get("animeout")
ANIMEPAHE = SITE_URLS.get("animepahe")
ANIMEONSEN = SITE_URLS.get("animeonsen")
ANIMEXIN = SITE_URLS.get("animexin")
ANIMIXPLAY = SITE_URLS.get("animixplay")
ANIMTIME = SITE_URLS.get("animtime")
CRUNCHYROLL = SITE_URLS.get("crunchyroll")
KAWAIIFU = SITE_URLS.get("kawaiifu")
KAMYROLL_API = SITE_URLS.get("kamyroll_api")
GOGOANIME = SITE_URLS.get("gogoanime")
NYAASI = SITE_URLS.get("nyaasi")
TENSHI = SITE_URLS.get("tenshi")
HAHO = SITE_URLS.get("haho")
HENTAISTREAM = SITE_URLS.get("hentaistream")
TWIST = SITE_URLS.get("twist")
ZORO = SITE_URLS.get("zoro")

QUALITY = CONFIG.get("quality_string")

DEFAULT_PLAYER = CONFIG.get("default_player")
PLAYERS = CONFIG.get("players")

ANICHART = CONFIG.get("schedule", {}).get("site_url")

DATE_FORMAT = CONFIG.get("schedule", {}).get("date_format")
TIME_FORMAT = CONFIG.get("schedule", {}).get("time_format")

DEFAULT_PROVIDER = CONFIG.get("default_provider")

AUTO_RETRY = CONFIG.get("download_auto_retry", 300) / 1000

FFMPEG_SETTINGS = CONFIG.get("ffmpeg", {})

FFMPEG_EXECUTABLE = FFMPEG_SETTINGS.get("executable", "ffmpeg")
FFMPEG_HLS = FFMPEG_SETTINGS.get("hls_download", False)
FFMPEG_SUBMERGE = FFMPEG_SETTINGS.get("submerge", True)

DISCORD_PRESENCE = CONFIG.get("discord_presence", False)

FZF = CONFIG.get("fzf", {})
FZF_EXECUTABLE = FZF.get("executable", "fzf")
FZF_OPTS = FZF.get("opts", [])
FZF_STATE = FZF.get("state", False)

DOWNLOAD_DIRECTORY = CONFIG.get("download_directory", ".")
CHECK_FOR_UPDATES = CONFIG.get("check_for_updates", True)
FORCE_STREAMING_QUALITY_SELECTION = CONFIG.get(
    "force_streaming_quality_selection", True
)

USE_ANISKIP = CONFIG.get("aniskip", False)

SUPERANIME = CONFIG.get("superanime", {})

SUPERANIME_RETURN_ALL = SUPERANIME.get("return_all", False)
SUPERANIME_TYPE_OF = SUPERANIME.get("type_of", "sub")
