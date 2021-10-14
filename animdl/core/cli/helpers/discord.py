import json
import os
import pathlib
import struct
import threading
import time
import uuid

class OP:
    CLOSE = 2
    FRAME = 1
    HANDSHAKE = 0
    PING = 3
    PONG = 4

class DiscordRichPresence():

    RPC_PIPE_PATH = r'\\?\pipe\discord-ipc-{}'

    def __init__(self, client_id):
        self.client_id = client_id
        open_pipe = self.get_open_ipc_pipe()
        self.conn = open(open_pipe, 'wb+') if open_pipe else None


    def get_open_ipc_pipe(self):
        for mime in range(10):
            if pathlib.Path(self.RPC_PIPE_PATH.format(mime)).exists():
                return self.RPC_PIPE_PATH.format(mime)

    def write(self, data: bytes):
        self.conn.write(data)
        return self.conn.flush()

    def read(self, buffer_size: int) -> bytes:
        return self.conn.read(buffer_size)
    
    def close(self):
        self.send({}, OP.CLOSE)
        return self.conn.close()

    def __enter__(self):
        self.handshake()
        return self
    
    def __exit__(self, *args, **kwargs):
        return self.close()
    
    def recv_raw_chunk(self, n):
        while n:
            content = self.read(n)
            yield content        
            n -= len(content)

    def recv_content_header(self):
        return struct.unpack("<II", b''.join(self.recv_raw_chunk(8)))    

    def recv(self):
        op_code, size = self.recv_content_header()
        return op_code, json.loads(b''.join(self.recv_raw_chunk(size)))

    def send(self, data, op_code):
        raw = json.dumps(data).encode('utf-8')
        self.write(struct.pack('<II', op_code, len(raw)))
        return self.write(raw)

    def handshake(self):
        self.send({'v': 1, 'client_id': self.client_id}, op_code=OP.HANDSHAKE)
        op_code, data = self.recv()

        if (op_code, data["cmd"], data["evt"]) == (OP.FRAME, 'DISPATCH', 'READY'):
            return True
        
        if op_code == OP.CLOSE:
            self.close()
        
        raise Exception("Could not validate handshake response: {}".format(data))
    
    def set(self, activity):
        return self.send(
            {
                'cmd': 'SET_ACTIVITY',
                'args': {'pid': os.getpid(), 'activity': activity},
                'nonce': str(uuid.uuid4())
            },
            OP.FRAME
        )

class AnimDLRPC(DiscordRichPresence):
    """
    animdl Rich Presence Client
    """
    def __init__(self):
        self.previous_rpc_event = 0
        super().__init__('897850955373105222')

    def set(self, timeout, *args, **kwargs):
        if (time.time() - self.previous_rpc_event) < timeout:
            return
        self.previous_rpc_event = time.time()
        return super().set(*args, **kwargs)


    def activate(self, provider: str, anime, episode_state, *, conditional_predicate=lambda: True, rpc_timeout=50):
        self.previous_rpc_event = 0
        
        main_thread = threading.main_thread()
        
        while conditional_predicate() and main_thread.is_alive():
            self.set(
                rpc_timeout,
                {
                    'details': "{}: {}".format(provider.title(), anime),
                    'state': episode_state,
                    'assets': {
                        'large_image': 'animdl',
                        'large_text': 'Streaming using animdl'
                    },
                    'buttons': [
                        {'label': 'justfoolingaround/animdl', 'url': 'https://github.com/justfoolingaround/animdl'}
                    ]
                }
            )
    
    def threaded_activation(self, *args, **kwargs):
        return threading.Thread(target=self.activate, args=args, kwargs=kwargs)
