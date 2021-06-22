import re

def construct_site_based_regex(site_url, *, extra='', extra_regex=''):
    return re.compile("(?:https?://)?(?:\S+\.)*%s" % (re.escape(re.search(r"(?:https?://)?((?:\S+\.)+[^/]+)/?", site_url).group(1)) + extra) + extra_regex)

def append_protocol(uri, *, protocol='https'):
    if re.search(r"^\S+://", uri):
        return uri
    return "%s://%s" % (protocol.rstrip(':/'), uri.lstrip('/'))