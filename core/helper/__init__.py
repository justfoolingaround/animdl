
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