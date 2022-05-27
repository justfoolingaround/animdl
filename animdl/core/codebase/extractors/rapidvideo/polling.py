import json
import time

import regex

recv_data_regex = regex.compile(r"(\d+)(.+)")

POLLING_PARAMETERS = {
    "EIO": "4",
    "transport": "polling",
}


def parse_response(response_text):
    match = recv_data_regex.search(response_text)

    if match:
        return int(match.group(1)), json.loads(match.group(2))

    return None, response_text


def ws_stimulation(
    session,
    *,
    url="https://ws1.rapid-cloud.ru/socket.io/",
    close_event,
    sid_holder,
    parent_thread,
):
    def ws_poll(params={}, data=None):
        soft = POLLING_PARAMETERS.copy()
        soft.update(params)

        if data is None:
            response = session.get(url, params=soft)
        else:
            response = session.post(url, params=soft, data=data)

        return parse_response(response.text)

    _, response = ws_poll()

    ping_interval = response.get("pingInterval", 25000) // 1000
    polling_sid = response.get("sid")

    _, client_check = ws_poll(
        {
            "sid": polling_sid,
        },
        data="40",
    )

    if client_check != "ok":
        raise RuntimeError(
            f"Websocket server has returned a faulty value: {client_check!r}"
        )

    _, response = ws_poll(
        {
            "sid": polling_sid,
        }
    )

    user_sid = response.get("sid")

    sid_holder.update(sid=user_sid)

    while not active_sleep(
        ping_interval, lambda: not (close_event.is_set() or parent_thread.is_alive())
    ):

        _, data = ws_poll({"sid": polling_sid})

        if data != "2":
            raise RuntimeError(
                f"Websocket server has returned a faulty value: {data!r}"
            )

        _, data = ws_poll({"sid": polling_sid}, data="3")

        if data != "ok":
            raise RuntimeError(
                f"Websocket server has returned a faulty value: {data!r}"
            )


def active_sleep(interval, predicate, *, delay=0.1):

    time_now = time.time()

    while (time.time() - time_now) < interval:

        if predicate():
            return False

        time.sleep(delay)

    return True
