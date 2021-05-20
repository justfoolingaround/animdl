import requests
import lxml.html as htmlparser

Q = "https://cdn.animixplay.to/api/search"
# "https://v1.nmtvjxdtx42qdwktdxjfoikjq.workers.dev/"


def animix_search(query):
    """
    Returns a tuple containing the site url to the anime, it's title and cover image.
    """
    data = htmlparser.fromstring(requests.post(Q, data={'qfast': query}).json().get('result'))

    return [(c.get('href'), c.get('title'), i.get('src')) for c, i in zip(data.xpath('//a'), data.xpath('//img'))]