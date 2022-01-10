from .stream_url import fetcher

from ....config import ANIMIXPLAY
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(ANIMIXPLAY, extra_regex=r"/v\d+/([^?&/]+)")
