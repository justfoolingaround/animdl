import re

SUFFIX_REGEX = re.compile(r'([^?&/.]+)\.(?:[^?&/.]+)(?:\?.+)?$')

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
    
    fallback = re.search('(\d+)pp?', fn)
    fn = re.sub('(\d+)pp?', '', fn)
    if fallback:
        index.update({'quality': int(fallback.group(1))})

    fn = PARENTHESIS_REGEX.sub('', fn)
    
    *anime, pe = fn.rsplit('-', 1)
    
    index.update({'name': '-'.join(anime)})
    
    pe = pe.strip().removesuffix('v2')
    if pe.isdigit():
        index.update({'episode': int(pe)})
    
    index.update({'extra': pe})
    return index