import re

def filter_episodes(episode_list, start=None, end=None, offset=None):
    
    if not episode_list:
        return
    
    offset = offset or 0
    
    start = (start or 1) + offset
    end = ((end or (episode_list[-1].number - offset)) + offset) or episode_list[-1].number
    
    for episode in episode_list:
        if start <= episode.number <= end:
            yield episode
            
def construct_check(episode_list, offset):
    
    if not episode_list:
        return lambda *args, **kwargs: True
    
    numeric_list = [e.number for e in episode_list]
    return lambda n: (n + offset) in numeric_list

def construct_site_based_regex(site_url, *, extra='', extra_regex=''):
    return re.compile("(?:https?://)?(?:\S+\.)*%s" % (re.escape(re.search(r"(?:https?://)?((?:\S+\.)+[^/]+)/?", site_url).group(1)) + extra) + extra_regex)

def append_protocol(uri, *, protocol='https'):
    if re.search(r"^\S+://", uri):
        return uri
    return "%s://%s" % (protocol.rstrip(':/'), uri.lstrip('/'))