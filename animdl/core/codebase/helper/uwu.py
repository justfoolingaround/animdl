import base64
import functools

import regex
import yarl

RECAPTCHA_API_JS = "https://www.google.com/recaptcha/api.js"


def bypass_ddos_guard(session, base_uri):
    js_bypass_uri = regex.search(
        r"'(.*?)'", session.get("https://check.ddos-guard.net/check.js").text
    ).group(1)

    session.get(base_uri + js_bypass_uri)


def bypass_recaptcha(session, url, headers):
    domain = (
        base64.b64encode("{0.scheme}://{0.host}:443".format(yarl.URL(url)).encode())
        .decode()
        .strip("=")
        + "."
    )
    initial_page = session.get(url, headers=headers)

    site_key_match = regex.search(r"recaptchaSiteKey = '(.+?)'", initial_page.text)

    if site_key_match is None:
        return {}

    response = {
        "token": get_token_recaptcha(
            session,
            domain,
            site_key_match.group(1),
            "{0.scheme}://{0.host}/".format(yarl.URL(url)),
        )
    }

    number_match = regex.search(r"recaptchaNumber = '(\d+?)'", initial_page.text)

    if number_match:
        response.update(number=number_match.group(1))

    return response


@functools.lru_cache()
def get_token_recaptcha(session, domain, recaptcha_site_key, url):

    recaptcha_out = session.get(
        RECAPTCHA_API_JS,
        params={"render": recaptcha_site_key},
        headers={"referer": url},
    ).text

    v_token_match = regex.search(r"releases/([^/&?#]+)", recaptcha_out)

    if v_token_match is None:
        return

    v_token = v_token_match.group(1)
    anchor_out = session.get(
        "https://www.google.com/recaptcha/api2/anchor",
        params={
            "ar": 1,
            "k": recaptcha_site_key,
            "co": domain,
            "hl": "en",
            "v": v_token,
            "size": "invisible",
            "cb": "kr42069kr",
        },
    ).text

    recaptcha_token_match = regex.search(r'recaptcha-token.+?="(.+?)"', anchor_out)

    if recaptcha_token_match is None:
        return

    recaptcha_token = recaptcha_token_match.group(1)

    token_out = session.post(
        "https://www.google.com/recaptcha/api2/reload",
        params={"k": recaptcha_site_key},
        data={
            "v": v_token,
            "reason": "q",
            "k": recaptcha_site_key,
            "c": recaptcha_token,
            "sa": "",
            "co": domain,
        },
        headers={"referer": "https://www.google.com/recaptcha/api2"},
    ).text

    token_match = regex.search(r'rresp","(.+?)"', token_out)
    if token_match is None:
        return

    return token_match.group(1)
