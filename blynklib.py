# Copyright (c) 2015-2019 Volodymyr Shymanskyy. See the file LICENSE for copying permission.
# Copyright (c) 2019 Anton Morozenko
VERSION = '0.2.2'

try:
    import usocket as socket
    import utime as time
    import ustruct as struct
    import uselect as select
    from micropython import const

    IOError = OSError
except ImportError:
    import socket
    import time
    import struct
    import select

    const = lambda x: x
    ticks_ms = lambda: int(time.time() * 1000)
    sleep_ms = lambda m_sec: time.sleep(m_sec // 1000)

LOGO = """
        ___  __          __
       / _ )/ /_ _____  / /__
      / _  / / // / _ \\/  '_/
     /____/_/\\_, /_//_/_/\\_\\
            /___/ for Python v{}\n""".format(VERSION)


class BlynkException(Exception):
    pass


class Protocol(object):
    _MSG_RSP = const(0)
    _MSG_LOGIN = const(2)
    _MSG_PING = const(6)
    _MSG_TWEET = const(12)
    _MSG_EMAIL = const(13)
    _MSG_NOTIFY = const(14)
    _MSG_BRIDGE = const(15)
    _MSG_HW_SYNC = const(16)
    _MSG_INTERNAL = const(17)
    _MSG_PROPERTY = const(19)
    _MSG_HW = const(20)

    _MSG_HEAD_LEN = const(5)
    _STATUS_INVALID_TOKEN = const(9)
    _STATUS_SUCCESS = const(200)
    _VIRTUAL_PIN_MAX_NUM = const(32)

    _msg_id = 1

    @staticmethod
    def _parse_msg_body(msg_body):
        return [itm.decode('utf-8') for itm in msg_body.split(b'\0')]

    def _get_msg_id(self):
        self._msg_id += 1
        return self._msg_id if self._msg_id <= 0xFFFF else 1

    def _pack_msg(self, msg_type, *args, **kwargs):
        msg_id = kwargs['msg_id'] if 'msg_id' in kwargs else self._get_msg_id()
        data = ('\0'.join([str(curr_arg) for curr_arg in args])).encode('utf8')
        return struct.pack('!BHH', msg_type, msg_id, len(data)) + data

    def parse_response(self, rsp_data, max_msg_buffer):
        msg_args = []
        msg_type, msg_id, h_data = struct.unpack('!BHH', rsp_data[:self._MSG_HEAD_LEN])
        if msg_id == 0:
            raise BlynkException('invalid msg_id == 0')
        elif h_data >= max_msg_buffer:
            raise BlynkException('Command too long. Length = {}'.format(h_data))
        elif msg_type in (self._MSG_RSP, self._MSG_PING, self._MSG_INTERNAL):
            pass
        elif msg_type in (self._MSG_HW, self._MSG_BRIDGE):
            msg_args = self._parse_msg_body(rsp_data[self._MSG_HEAD_LEN: self._MSG_HEAD_LEN + h_data])
        else:
            raise BlynkException("Unknown message type: '{}'".format(msg_type))
        return msg_type, msg_id, h_data, msg_args

    def heartbeat_msg(self, heartbeat, max_msg_buffer):
        return self._pack_msg(self._MSG_INTERNAL, 'ver', VERSION, 'buff-in', max_msg_buffer, 'h-beat', heartbeat,
                              'dev', 'python')

    def login_msg(self, token):
        return self._pack_msg(self._MSG_LOGIN, token)

    def ping_msg(self):
        return self._pack_msg(self._MSG_PING)

    def response_msg(self, *args, **kwargs):
        return self._pack_msg(self._MSG_RSP, *args, **kwargs)

    def virtual_write_msg(self, v_pin, *val):
        return self._pack_msg(self._MSG_HW, 'vw', v_pin, *val)

    def virtual_sync_msg(self, *pins):
        return self._pack_msg(self._MSG_HW_SYNC, 'vr', *pins)

    def email_msg(self, to, subject, body):
        return self._pack_msg(self._MSG_EMAIL, to, subject, body)

    def notify_msg(self, msg):
        return self._pack_msg(self._MSG_NOTIFY, msg)

    def set_property_msg(self, pin, prop, *val):
        return self._pack_msg(self._MSG_PROPERTY, pin, prop, *val)


class Connection(Protocol):
    _SOCK_MAX_TIMEOUT = const(5)  # 5 seconds, must be < self.HEARTBEAT_PERIOD
    _SOCK_CONNECTION_TIMEOUT = 0.05
    _SOCK_RECONNECT_DELAY = const(1)  # 1 second
    _ERR_EAGAIN = const(11)
    _ERR_ETIMEDOUT = const(60)
    _STATE_DISCONNECTED = const(0)
    _STATE_CONNECTING = const(1)
    _STATE_AUTHENTICATING = const(2)
    _STATE_AUTHENTICATED = const(3)

    _RETRIES_TX_DELAY = const(2)
    _RETRIES_TX_MAX_NUM = const(3)
    _TASK_PERIOD_RES = const(50)  # 50ms
    _SOCK_TIMEOUT_MSG = 'timed out'

    token = None
    server = None
    port = None
    state = None
    socket = None
    ssl_flag = False
    _last_receive_time = 0
    _last_ping_time = 0
    _last_send_time = 0

    def _set_socket_timeout(self, timeout):
        if getattr(self.socket, 'settimeout', None) is not None:
            self.socket.settimeout(timeout)
        else:
            poller = select.poll()
            poller.register(self.socket)
            poller.poll(int(timeout * 1000))  # time in milliseconds

    def send(self, data):
        curr_retry_num = 0
        while curr_retry_num <= self._RETRIES_TX_MAX_NUM:
            try:
                curr_retry_num += 1
                self._last_send_time = ticks_ms()
                return self.socket.send(data)
            except (IOError, OSError):
                sleep_ms(self._RETRIES_TX_DELAY)

    def receive(self, length, timeout=0.0):
        try:
            rcv_buffer = b''
            self._set_socket_timeout(timeout)
            rcv_buffer += self.socket.recv(length)
            if len(rcv_buffer) >= length:
                rcv_buffer = rcv_buffer[:length]
            return rcv_buffer
        except (IOError, OSError) as err:
            if str(err) == self._SOCK_TIMEOUT_MSG:
                return b''
            if isinstance(err, int):
                if int(err) in (self._ERR_EAGAIN, self._ERR_ETIMEDOUT):
                    return b''
            raise

    def is_server_alive(self, heartbeat):
        now = ticks_ms()
        heartbeat_ms = heartbeat * 1000
        receive_delta = now - self._last_receive_time
        ping_delta = now - self._last_ping_time
        send_delta = now - self._last_send_time
        if receive_delta > heartbeat_ms + (heartbeat_ms // 2):
            return False
        if (ping_delta > heartbeat_ms // 10) and (send_delta > heartbeat_ms or receive_delta > heartbeat_ms):
            self.send(self.ping_msg())
            print('Heartbeat time: {}'.format(now))
            self._last_ping_time = now
        return True

    def _get_socket(self, ssl_flag):
        try:
            self.state = self._STATE_CONNECTING
            self.socket = socket.socket()
            if ssl_flag:
                raise NotImplementedError
            self.socket.connect(socket.getaddrinfo(self.server, self.port)[0][4])
            self._set_socket_timeout(self._SOCK_CONNECTION_TIMEOUT)
            print('\nNew connection socket created')
        except Exception as g_exc:
            raise BlynkException('Connection with the Blynk server failed: {}'.format(g_exc))

    def _authenticate(self, max_msg_buffer):
        print('Authenticating device...')
        self.state = self._STATE_AUTHENTICATING
        self.send(self.login_msg(self.token))
        rsp_data = self.receive(max_msg_buffer, timeout=self._SOCK_MAX_TIMEOUT)
        if not rsp_data:
            raise BlynkException('Auth stage timeout')
        _, _, status, _ = self.parse_response(rsp_data, max_msg_buffer)
        if status != self._STATUS_SUCCESS:
            if status == self._STATUS_INVALID_TOKEN:
                raise BlynkException('Invalid Auth Token')
            raise BlynkException('Auth stage failed. Status={}'.format(status))
        self.state = self._STATE_AUTHENTICATED
        print('Access granted.')

    def _set_heartbeat(self, heartbeat, max_msg_buffer):
        self.send(self.heartbeat_msg(heartbeat, max_msg_buffer))
        rsp_data = self.receive(max_msg_buffer, timeout=self._SOCK_MAX_TIMEOUT)
        if not rsp_data:
            raise BlynkException('Heartbeat reply timeout')
        _, _, status, _ = self.parse_response(rsp_data, max_msg_buffer)
        if status != self._STATUS_SUCCESS:
            raise BlynkException('Set heartbeat reply code= {}'.format(status))
        print("Heartbeat = {} sec. Max cmd buffer = {} bytes.".format(heartbeat, max_msg_buffer))

    def connected(self):
        return True if self.state == self._STATE_AUTHENTICATED else False


class Blynk(Connection):
    BLYNK_SERVER = "blynk-cloud.com"
    BLYNK_HTTP_PORT = const(80)
    CONNECT_CALL_TIMEOUT = const(30)  # 30sec

    VPIN_WILDCARD = '*'
    READ_VPIN_EVENT_BASENAME = 'read v'
    WRITE_VPIN_EVENT_BASENAME = 'write v'
    INTERNAL_EVENT_BASENAME = 'internal_'
    CONNECT_EVENT = 'connect'
    DISCONNECT_EVENT = 'disconnect'
    READ_ALL_VPIN_EVENT = '{}{}'.format(READ_VPIN_EVENT_BASENAME, VPIN_WILDCARD)
    WRITE_ALL_VPIN_EVENT = '{}{}'.format(WRITE_VPIN_EVENT_BASENAME, VPIN_WILDCARD)

    def __init__(self, token, server=BLYNK_SERVER, port=BLYNK_HTTP_PORT, heartbeat=10, max_msg_buffer=1024, ssl=False):
        self.token = token
        self.server = server
        self.port = port
        self.heartbeat = heartbeat
        self.max_msg_buffer = max_msg_buffer
        self.ssl = ssl
        self.state = self._STATE_DISCONNECTED
        self._start_time = ticks_ms()
        self._last_receive_time = self._start_time
        self._last_send_time = self._start_time
        self._last_ping_time = self._start_time
        self.events = {}
        print(LOGO)

    def connect(self, timeout=CONNECT_CALL_TIMEOUT):
        end_time = time.time() + timeout
        while not self.connected():
            try:
                if self.state == self._STATE_DISCONNECTED:
                    self._get_socket(self.ssl_flag)
                    self._authenticate(self.max_msg_buffer)
                    self._set_heartbeat(self.heartbeat, self.max_msg_buffer)
                    print('Registered events:\n{}\nHappy Blynking!\n'.format(self.events.keys()))
                    self.call_handler(self.CONNECT_EVENT)
                    return True
            except BlynkException as b_exc:
                self.disconnect(b_exc)
                sleep_ms(self._TASK_PERIOD_RES)
            finally:
                if time.time() >= end_time:
                    return False

    def disconnect(self, err_msg=None):
        if self.socket is not None:
            self.socket.close()
        self.state = self._STATE_DISCONNECTED
        if err_msg:
            print('[ERROR]: {}\nConnection closed'.format(err_msg))
        time.sleep(self._SOCK_RECONNECT_DELAY)
        self.call_handler(self.DISCONNECT_EVENT)

    def virtual_write(self, v_pin, *val):
        return self.send(self.virtual_write_msg(v_pin, *val))

    def virtual_sync(self, *v_pin):
        return self.send(self.virtual_sync_msg(*v_pin))

    def email(self, to, subject, body):
        return self.send(self.email_msg(to, subject, body))

    def notify(self, msg):
        return self.send(self.notify_msg(msg))

    def set_property(self, v_pin, property_name, *val):
        return self.send(self.set_property_msg(v_pin, property_name, *val))

    def handle_event(blynk, event_name):
        class Decorator(object):
            def __init__(self, func):
                self.func = func
                # wildcard 'read V*' and 'write V*' events handling
                if str(event_name).lower() in (blynk.READ_ALL_VPIN_EVENT, blynk.WRITE_ALL_VPIN_EVENT):
                    event_base_name = str(event_name).split(blynk.VPIN_WILDCARD)[0]
                    for i in range(1, blynk._VIRTUAL_PIN_MAX_NUM + 1):
                        blynk.events['{}{}'.format(event_base_name.lower(), i)] = func
                else:
                    blynk.events[str(event_name).lower()] = func

            def __call__(self):
                return self.func()

        return Decorator

    def call_handler(self, event, *args, **kwargs):
        if event in self.events.keys():
            print("Event: ['{}'] -> {}".format(event, args))
            self.events[event](*args, **kwargs)

    def process(self, msg_type, msg_id, msg_len, msg_args):
        if msg_type == self._MSG_RSP:
            print(msg_len)
        elif msg_type == self._MSG_PING:
            self.send(self.response_msg(self._STATUS_SUCCESS, msg_id=msg_id))
        elif msg_type in (self._MSG_HW, self._MSG_BRIDGE):
            if len(msg_args) >= 2:
                if msg_args[0] == 'vw':
                    self.call_handler("{}{}".format(self.WRITE_VPIN_EVENT_BASENAME, msg_args[1]), int(msg_args[1]),
                                      msg_args[2:])
                elif msg_args[0] == 'vr':
                    self.call_handler("{}{}".format(self.READ_VPIN_EVENT_BASENAME, msg_args[1]), int(msg_args[1]))
        elif msg_type == self._MSG_INTERNAL:
            if len(msg_args) >= 2:
                self.call_handler("{}{}".format(self.INTERNAL_EVENT_BASENAME, msg_args[1]), msg_args[2:])

    def run(self):
        if not self.connected():
            self.connect()
        else:
            try:
                rsp_data = self.receive(self.max_msg_buffer, self._SOCK_CONNECTION_TIMEOUT)
                self._last_receive_time = ticks_ms()
                if rsp_data:
                    msg_type, msg_id, h_data, msg_args = self.parse_response(rsp_data, self.max_msg_buffer)
                    self.process(msg_type, msg_id, h_data, msg_args)
                if not self.is_server_alive(self.heartbeat):
                    self.disconnect('Blynk server is offline')
            except KeyboardInterrupt:
                raise
            except Exception as g_exc:
                print(g_exc)
                self.disconnect(g_exc)
