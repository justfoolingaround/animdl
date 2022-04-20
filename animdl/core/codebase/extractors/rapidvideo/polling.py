import sys
import threading
import time

import httpx
import regex


class DeathThread(threading.Thread):

    kill_state = threading.Event()

    def run(self):
        sys.settrace(self.global_trace)
        return super().run()

    def global_trace(self, stack_frame, reason, *args, **kwargs):
        if reason == "call":
            return self.local_trace

    def local_trace(self, stack_frame, reason, *args, **kwargs):
        if self.kill_state.is_set() and reason == "line":
            raise SystemExit()
        return self.local_trace

    def kill(self):
        return self.kill_state.set()


SID_REGEX = regex.compile(r'"sid":"(.+?)"')

POLLING_PARAMETERS = {
    "EIO": "4",
    "transport": "polling",
}


def ws_stimulation(session, *, url="https://ws1.rapid-cloud.ru/socket.io/"):
    def poll(params={}, data=None):
        soft = POLLING_PARAMETERS.copy()
        soft.update(params)

        if data is None:
            return session.get(url, params=soft)
        else:
            return session.post(url, params=soft, data=data)

    def get_sid(text: str) -> str:
        return SID_REGEX.search(text).group(1)

    polling_sid = get_sid(poll().text)

    assert poll({"sid": polling_sid}, data="40").text == "ok"

    setattr(ws_stimulation, "session_sid", get_sid(poll({"sid": polling_sid}).text))

    while 1:
        poll({"sid": polling_sid}).text == "2"
        poll({"sid": polling_sid}, data="3").text == "ok"


ws_stimulation.session_sid = None

ws_thread = DeathThread(target=ws_stimulation, args=(httpx.Client(timeout=60.0),))
ws_thread.start()


def thread_watcher():

    main_thead = threading.main_thread()

    while main_thead.is_alive():
        time.sleep(0.1)
    ws_thread.kill()


threading.Thread(target=thread_watcher).start()
