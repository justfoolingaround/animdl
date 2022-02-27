import yaml
import os
from pathlib import Path


def merge_dicts(dict1, dict2):
    for k, v in dict1.items():
        if isinstance(v, dict):
            merge_dicts(v, dict2.setdefault(k, {}))
        else:
            if k not in dict2:
                dict2[k] = v
    return dict2


def get_existent_path(*paths):
    for path in paths:
        path_object = Path(path)
        if path_object.exists():
            return path_object


USERPROFILE_ANIMDL_PATH = os.getenv("userprofile", ".") + "/.animdl/config.yml"

CONFIGURATION_FILE_PATH = get_existent_path(
    os.getenv("ANIMDL_CONFIG", "./animdl_config.yml"),
    "/animdl_config.yml",
    USERPROFILE_ANIMDL_PATH,
)

DEFAULT_CONFIG = {
    "session_file": "cli_session_animdl.json",
    "default_provider": "zoro",
    "site_urls": {
        "9anime": "https://9anime.to/",
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
        "hentaistream": "https://hentaistream.moe/",
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
            "executable": "iina-cli",
            "opts": [],
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
    "qbittorrent": {
        "endpoint_url": "http://127.0.0.1:8080",
        "credentials": {
            "username": "admin",
            "password": "youshallnotpass",
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

SESSION_FILE = CONFIG.get("session_file")
DEFAULT_PROVIDER = CONFIG.get("default_provider")

AUTO_RETRY = CONFIG.get("download_auto_retry", 300) / 1000

FFMPEG_SETTINGS = CONFIG.get("ffmpeg", {})

FFMPEG_EXECUTABLE = FFMPEG_SETTINGS.get("executable", "ffmpeg")
FFMPEG_HLS = FFMPEG_SETTINGS.get("hls_download", False)
FFMPEG_SUBMERGE = FFMPEG_SETTINGS.get("submerge", True)

QBITTORENT_CONFIG = CONFIG.get("qbittorrent", {})

QBITTORENT_ENDPOINT = QBITTORENT_CONFIG.get("endpoint_url")
QBITTORENT_CREDENTIALS = QBITTORENT_CONFIG.get("credentials", {})
