import re

SUFFIX_REGEX = re.compile(r'([^?&/]+)(?:\?.+)?$')

BRACE_PAIRS = [
    ('{', '}'),
    ('(', ')'),
    ('[', ']'),
    ('【', '】'),
]

PARENTHESIS_REGEX = re.compile("|".join(r'({0}[^{1}]*{1})'.format(re.escape(s), re.escape(e)) for s, e in BRACE_PAIRS))

def index_by_url(url):
    index = {'url': url}
    fn_match = SUFFIX_REGEX.search(url)
    if not fn_match:
        return {}

    fn = fn_match.group(1) 
    
    fallback = re.search(r'(\d+)pp?', fn)
    fn = re.sub(r'((\d+)pp?|x\.?26[45])', '', fn)
    if fallback:
        index.update({'quality': int(fallback.group(1))})

    fn = PARENTHESIS_REGEX.sub('', fn)
    *anime, pe = re.split(r'(?=-\s*?[VS]?\d+)', fn, 1, re.I)
    index.update({'name': '-'.join(anime)})
    
    pe_match = re.search(r"(?<![VS])(\d+).*?", pe, re.I)
    if pe_match:
        index.update({'episode': int(pe_match.group(1))})
    
    index.update({'extra': pe})
    return index