import regex


def construct_site_based_regex(site_url, *, extra='', extra_regex=''):
    return regex.compile(
        "(?:https?://)?(?:\\S+\\.)*{}".format
        (regex.escape(
            regex.search(
                r"(?:https?://)?((?:\S+\.)+[^/]+)/?",
                site_url).group(1)) +
         extra) +
        extra_regex)


def append_protocol(uri, *, protocol='https'):
    if regex.search(r"^.+?://", uri):
        return uri
    return "{}://{}".format(protocol.rstrip(':/'), uri.lstrip('/'))
