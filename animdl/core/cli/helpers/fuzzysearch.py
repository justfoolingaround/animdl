import difflib


def search(query, possibilities, cutoff=0.6, *, processor=lambda r: r):

    sequence_matcher = difflib.SequenceMatcher()
    sequence_matcher.set_seq2(query)

    for search_value in possibilities:
        sequence_matcher.set_seq1(processor(search_value))
        if query.lower() in processor(search_value).lower():
            yield (None, search_value)
            continue
        if (
            sequence_matcher.real_quick_ratio() >= cutoff
            and sequence_matcher.quick_ratio() >= cutoff
            and sequence_matcher.ratio() >= cutoff
        ):
            yield (sequence_matcher.ratio(), search_value)
