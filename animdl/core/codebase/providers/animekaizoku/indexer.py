import re

SUFFIX_REGEX = re.compile(r'([^?&/]+)(?:\?.+)?$')

BRACE_PAIRS = [
    ('{', '}'),
    ('(', ')'),
    ('[', ']'),
    ('【', '】'),
]

PARENTHESIS_REGEX = re.compile("|".join(
    r'({0}[^{1}]*{1})'.format(re.escape(s), re.escape(e)) for s, e in BRACE_PAIRS))


def name_index(element):
    index = {'element': element}
    name = element.text_content()
    quality = re.search(r'(\d+)pp?', name)
    fn = re.sub(r'((\d+)pp?|x\.?26[45])', '', name)
    if quality:
        index.update({'quality': int(quality.group(1))})

    fn = PARENTHESIS_REGEX.sub('', fn)
    *anime, pe = re.split(r'(?=-\s*?[VS]?\d+)', fn, 1, re.I)
    index.update({'name': '-'.join(anime)})

    pe_match = re.search(r"(?<![VS])(\d+).*?", pe, re.I)
    if pe_match:
        index.update({'episode': int(pe_match.group(1))})

    index.update({'extra': pe})
    return index
