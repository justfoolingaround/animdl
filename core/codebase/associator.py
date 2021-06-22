import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from .helper import append_protocol
from .providers import get_appropriate


class Associator(object):
    """
    Associator associates a anime with its url, filler list and stream url.
    """
    
    def __init__(self, uri, afl_uri=None, *, session=None):
        self.url = append_protocol(uri)
        self.filler_list = afl_uri
        self.session = session or requests.Session()

    def raw_fetch_using_check(self, check):
        yield from get_appropriate(self.session, self.url, check=check)