import regex


def bypass_ddos_guard(session, base_uri):
    js_bypass_uri = regex.search(
        r"'(.*?)'", session.get("https://check.ddos-guard.net/check.js").text
    ).group(1)

    session.get(base_uri + js_bypass_uri)
