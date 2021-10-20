import regex

SUFFIX_REGEX = regex.compile(r'([^?&/]+)(?:\?.+)?$')

BRACE_PAIRS = [
    ('{', '}'),
    ('(', ')'),
    ('[', ']'),
    ('【', '】'),
]

PARENTHESIS_REGEX = regex.compile("|".join(
    r'({0}[^{1}]*{1})'.format(regex.escape(s), regex.escape(e)) for s, e in BRACE_PAIRS))


def name_index(element):
    index = {'element': element}
    name = element.text_content()
    quality = regex.search(r'(\d+)pp?', name)
    fn = regex.sub(r'((\d+)pp?|x\.?26[45])', '', name)
    if quality:
        index.update({'quality': int(quality.group(1))})

    fn = PARENTHESIS_REGEX.sub('', fn)
    *anime, pe = regex.split(r'(?=-\s*?[VS]?\d+)', fn, 1, regex.I)
    index.update({'name': '-'.join(anime)})

    remove_seasonal = regex.sub(r'[VS]\d+\D', '', pe, flags=regex.I)
    pe_match = regex.search(r"e?(\d+)", remove_seasonal, regex.I)
    if pe_match:
        index.update({'episode': int(pe_match.group(1))})

    index.update({'extra': pe})
    return index
