from collections import namedtuple

import lxml.html as htmlparser

PartialEpisode = namedtuple('AFLEpisode', ['number', 'title', 'content_type', 'aired_date'])

def get_filler_list(session, afl_url, canon=True, mixed_canon=True, fillers=False):
    """
    A function that scrapes AnimeFillerList to get all the episodes and their filler status.
    """
    
    if not any((canon, mixed_canon, fillers)):
        raise ValueError('All the filler settings cannot be set to False.')
    
    initial_xpath = []
    
    if canon:
        initial_xpath.append("//tr[@class='manga_canon even'] | //tr[@class='manga_canon odd'] | //tr[@class='anime_canon even'] | //tr[@class='anime_canon odd']")
        
    if mixed_canon:
        initial_xpath.append("//tr[@class='mixed_canon/filler even'] | //tr[@class='mixed_canon/filler odd']")
            
    if fillers:
        initial_xpath.append("//tr[@class='filler even'] | //tr[@class='filler odd']")
    
    return get_using_xpath(session, afl_url, ' | '.join(initial_xpath))

def get_using_xpath(session, afl_url, xpath):
    """
    Returns a list of named tuples containing the episode number, title, content type (either canon, filler or mixed) and aired-date.
    """
    parsed = htmlparser.fromstring(session.get(afl_url).content)
    return [PartialEpisode(int(tr.xpath('td[@class="Number"]')[0].text), tr.xpath('td[@class="Title"]/a')[0].text.strip(), tr.xpath('td[@class="Type"]/span')[0].text.strip(), tr.xpath('td[@class="Date"]')[0].text.strip()) for tr in parsed.xpath(xpath)]