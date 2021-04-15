import lxml.html as htmlparser
import requests


def get_using_xpath(afl_url, xpath):
    """
    Make sure the xpath gets the `tr` attribute.
    
    Returns a list of tuples containing the episode number, title and aired-date.
    """
    parsed = htmlparser.fromstring(requests.get(afl_url).content)
    return [(int(tr.xpath('td[@class="Number"]')[0].text), tr.xpath('td[@class="Title"]/a')[0].text, tr.xpath('td[@class="Type"]/span')[0].text, tr.xpath('td[@class="Date"]')[0].text) for tr in parsed.xpath(xpath)]