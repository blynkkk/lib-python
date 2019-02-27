# Copyright (c) 2015-2019 Volodymyr Shymanskyy. See the file LICENSE for copying permission.
# Copyright (c) 2019 Anton Morozenko
VERSION = '0.2.2'

try:
    import usocket as socket
    import utime as time
    import ustruct as struct
    import uselect as select
    from micropython import const

    ticks_ms = time.ticks_ms
    sleep_ms = time.sleep_ms

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
    MSG_RSP = const(0)
    MSG_LOGIN = const(2)
    MSG_PING = const(6)
    MSG_TWEET = const(12)
    MSG_EMAIL = const(13)
    MSG_NOTIFY = const(14)
    MSG_BRIDGE = const(15)
    MSG_HW_SYNC = const(16)
    MSG_INTERNAL = const(17)
    MSG_PROPERTY = const(19)
    MSG_HW = const(20)
    MSG_HEAD_LEN = const(5)

    STATUS_INVALID_TOKEN = const(9)
    STATUS_SUCCESS = const(200)
    VIRTUAL_PIN_MAX_NUM = const(32)

    _msg_id = 1

    def _get_msg_id(self):
        self._msg_id += 1
        return self._msg_id if self._msg_id <= 0xFFFF else 1

    def _pack_msg(self, msg_type, *args, **kwargs):
        msg_id = kwargs['msg_id'] if 'msg_id' in kwargs else self._get_msg_id()
        data = ('\0'.join([str(curr_arg) for curr_arg in args])).encode('utf8')
        return struct.pack('!BHH', msg_type, msg_id, len(data)) + data

    def parse_response(self, rsp_data, msg_buffer):
        msg_args = []
        msg_type, msg_id, h_data = struct.unpack('!BHH', rsp_data[:self.MSG_HEAD_LEN])
        if msg_id == 0:
            raise BlynkException('invalid msg_id == 0')
        elif h_data >= msg_buffer:
            raise BlynkException('Command too long. Length = {}'.format(h_data))
        elif msg_type in (self.MSG_RSP, self.MSG_PING, self.MSG_INTERNAL):
            pass
        elif msg_type in (self.MSG_HW, self.MSG_BRIDGE):
            msg_body = rsp_data[self.MSG_HEAD_LEN: self.MSG_HEAD_LEN + h_data]
            msg_args = [itm.decode('utf-8') for itm in msg_body.split(b'\0')]
        else:
            raise BlynkException("Unknown message type: '{}'".format(msg_type))
        return msg_type, msg_id, h_data, msg_args

    def heartbeat_msg(self, heartbeat, max_msg_buffer):
        return self._pack_msg(self.MSG_INTERNAL, 'ver', VERSION, 'buff-in', max_msg_buffer, 'h-beat', heartbeat,
                              'dev', 'python')

    def login_msg(self, token):
        return self._pack_msg(self.MSG_LOGIN, token)

    def ping_msg(self):
        return self._pack_msg(self.MSG_PING)

    def response_msg(self, *args, **kwargs):
        return self._pack_msg(self.MSG_RSP, *args, **kwargs)

    def virtual_write_msg(self, v_pin, *val):
        return self._pack_msg(self.MSG_HW, 'vw', v_pin, *val)

    def virtual_sync_msg(self, *pins):
        return self._pack_msg(self.MSG_HW_SYNC, 'vr', *pins)

    def email_msg(self, to, subject, body):
        return self._pack_msg(self.MSG_EMAIL, to, subject, body)

    def notify_msg(self, msg):
        return self._pack_msg(self.MSG_NOTIFY, msg)

    def set_property_msg(self, pin, prop, *val):
        return self._pack_msg(self.MSG_PROPERTY, pin, prop, *val)


class Connection(Protocol):
    SOCK_MAX_TIMEOUT = const(5)  # 5 seconds, must be < self.HEARTBEAT_PERIOD
    ERR_EAGAIN = const(11)
    ERR_ETIMEDOUT = const(60)
    RETRIES_TX_DELAY = const(2)
    RETRIES_TX_MAX_NUM = const(3)
    SOCK_TIMEOUT_MSG = 'timed out'
    _BLYNK_SERVER = "blynk-cloud.com"
    _BLYNK_HTTP_PORT = const(80)

    STATE_DISCONNECTED = const(0)
    STATE_CONNECTING = const(1)
    STATE_AUTHENTICATING = const(2)
    STATE_AUTHENTICATED = const(3)
    SOCK_RECONNECT_DELAY = const(1)  # 1 second
    SOCK_CONNECTION_TIMEOUT = 0.05
    TASK_PERIOD_RES = const(50)  # 50ms

    _state = None
    _socket = None
    _last_receive_time = 0
    _last_ping_time = 0
    _last_send_time = 0

    def __init__(self, token, server=_BLYNK_SERVER, port=_BLYNK_HTTP_PORT, heartbeat=10, cmd_buffer=1024):
        self.token = token
        self.server = server
        self.port = port
        self.heartbeat = heartbeat
        self.cmd_buffer = cmd_buffer

    def _set_socket_timeout(self, timeout):
        if getattr(self._socket, 'settimeout', None):
            self._socket.settimeout(timeout)
        else:
            poller = select.poll()
            poller.register(self._socket)
            poller.poll(int(timeout * 1000))  # time in milliseconds

    def send(self, data):
        curr_retry_num = 0
        while curr_retry_num <= self.RETRIES_TX_MAX_NUM:
            try:
                curr_retry_num += 1
                self._last_send_time = ticks_ms()
                return self._socket.send(data)
            except (IOError, OSError):
                sleep_ms(self.RETRIES_TX_DELAY)

    def receive(self, length, timeout=0.0):
        rcv_buffer = b''
        try:
            self._set_socket_timeout(timeout)
            rcv_buffer += self._socket.recv(length)
            if len(rcv_buffer) >= length:
                rcv_buffer = rcv_buffer[:length]
            return rcv_buffer
        except (IOError, OSError) as err:
            if str(err) == self.SOCK_TIMEOUT_MSG:
                return rcv_buffer
            if isinstance(err, int):
                if int(err) in (self.ERR_EAGAIN, self.ERR_ETIMEDOUT):
                    return rcv_buffer
            raise

    def is_server_alive(self):
        now = ticks_ms()
        heartbeat_ms = self.heartbeat * 1000
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

    def _get_socket(self):
        try:
            self._state = self.STATE_CONNECTING
            self._socket = socket.socket()
            self._socket.connect(socket.getaddrinfo(self.server, self.port)[0][4])
            self._set_socket_timeout(self.SOCK_CONNECTION_TIMEOUT)
            print('\nNew connection socket created')
        except Exception as g_exc:
            raise BlynkException('Connection with the Blynk server failed: {}'.format(g_exc))

    def _authenticate(self):
        print('Authenticating device...')
        self._state = self.STATE_AUTHENTICATING
        self.send(self.login_msg(self.token))
        rsp_data = self.receive(self.cmd_buffer, timeout=self.SOCK_MAX_TIMEOUT)
        if not rsp_data:
            raise BlynkException('Auth stage timeout')
        _, _, status, _ = self.parse_response(rsp_data, self.cmd_buffer)
        if status != self.STATUS_SUCCESS:
            if status == self.STATUS_INVALID_TOKEN:
                raise BlynkException('Invalid Auth Token')
            raise BlynkException('Auth stage failed. Status={}'.format(status))
        self._state = self.STATE_AUTHENTICATED
        print('Access granted.')

    def _set_heartbeat(self):
        self.send(self.heartbeat_msg(self.heartbeat, self.cmd_buffer))
        rsp_data = self.receive(self.cmd_buffer, timeout=self.SOCK_MAX_TIMEOUT)
        if not rsp_data:
            raise BlynkException('Heartbeat reply timeout')
        _, _, status, _ = self.parse_response(rsp_data, self.cmd_buffer)
        if status != self.STATUS_SUCCESS:
            raise BlynkException('Set heartbeat reply code= {}'.format(status))
        print("Heartbeat = {} sec. MaxCmdBuffer = {} bytes.".format(self.heartbeat, self.cmd_buffer))

    def connected(self):
        return True if self._state == self.STATE_AUTHENTICATED else False


class Blynk(Connection):
    _CONNECT_CALL_TIMEOUT = const(30)  # 30sec
    _VPIN_WILDCARD = '*'
    _READ_VPIN_EVENT = 'read v'
    _WRITE_VPIN_EVENT = 'write v'
    _INTERNAL_EVENT = 'internal_'
    _CONNECT_EVENT = 'connect'
    _DISCONNECT_EVENT = 'disconnect'
    _READ_ALL_VPIN_EVENT = '{}{}'.format(_READ_VPIN_EVENT, _VPIN_WILDCARD)
    _WRITE_ALL_VPIN_EVENT = '{}{}'.format(_WRITE_VPIN_EVENT, _VPIN_WILDCARD)
    _events = {}

    def __init__(self, token, **kwargs):
        Connection.__init__(self, token, **kwargs)
        self._start_time = ticks_ms()
        self._last_receive_time = self._start_time
        self._last_send_time = self._start_time
        self._last_ping_time = self._start_time
        self._state = self.STATE_DISCONNECTED
        print(LOGO)

    def connect(self, timeout=_CONNECT_CALL_TIMEOUT):
        end_time = time.time() + timeout
        while not self.connected():
            if self._state == self.STATE_DISCONNECTED:
                try:
                    self._get_socket()
                    self._authenticate()
                    self._set_heartbeat()
                    print('Registered events: {}\nHappy Blynking!\n'.format(list(self._events.keys())))
                    self.call_handler(self._CONNECT_EVENT)
                    return True
                except BlynkException as b_exc:
                    self.disconnect(b_exc)
                    sleep_ms(self.TASK_PERIOD_RES)
            if time.time() >= end_time:
                return False

    def disconnect(self, err_msg=None):
        if self._socket:
            self._socket.close()
        self._state = self.STATE_DISCONNECTED
        if err_msg:
            print('[ERROR]: {}\nConnection closed'.format(err_msg))
        time.sleep(self.SOCK_RECONNECT_DELAY)
        self.call_handler(self._DISCONNECT_EVENT)

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
                if str(event_name).lower() in (blynk._READ_ALL_VPIN_EVENT, blynk._WRITE_ALL_VPIN_EVENT):
                    event_base_name = str(event_name).split(blynk._VPIN_WILDCARD)[0]
                    for i in range(1, blynk.VIRTUAL_PIN_MAX_NUM + 1):
                        blynk._events['{}{}'.format(event_base_name.lower(), i)] = func
                else:
                    blynk._events[str(event_name).lower()] = func

            def __call__(self):
                return self.func()

        return Decorator

    def call_handler(self, event, *args, **kwargs):
        if event in self._events.keys():
            print("Event: ['{}'] -> {}".format(event, args))
            self._events[event](*args, **kwargs)

    def process(self, msg_type, msg_id, msg_len, msg_args):
        if msg_type == self.MSG_RSP:
            print(msg_len)
        elif msg_type == self.MSG_PING:
            self.send(self.response_msg(self.STATUS_SUCCESS, msg_id=msg_id))
        elif msg_type in (self.MSG_HW, self.MSG_BRIDGE, self.MSG_INTERNAL):
            if msg_type == self.MSG_INTERNAL and len(msg_args) >= const(3):
                self.call_handler("{}{}".format(self._INTERNAL_EVENT, msg_args[1]), msg_args[2:])
            elif len(msg_args) >= const(3) and msg_args[0] == 'vw':
                self.call_handler("{}{}".format(self._WRITE_VPIN_EVENT, msg_args[1]), int(msg_args[1]), msg_args[2:])
            elif len(msg_args) == const(2) and msg_args[0] == 'vr':
                self.call_handler("{}{}".format(self._READ_VPIN_EVENT, msg_args[1]), int(msg_args[1]))

    def run(self):
        if not self.connected():
            self.connect()
        else:
            try:
                rsp_data = self.receive(self.cmd_buffer, self.SOCK_CONNECTION_TIMEOUT)
                self._last_receive_time = ticks_ms()
                if rsp_data:
                    msg_type, msg_id, h_data, msg_args = self.parse_response(rsp_data, self.cmd_buffer)
                    self.process(msg_type, msg_id, h_data, msg_args)
                if not self.is_server_alive():
                    self.disconnect('Blynk server is offline')
            except KeyboardInterrupt:
                raise
            except Exception as g_exc:
                print(g_exc)
                self.disconnect(g_exc)
