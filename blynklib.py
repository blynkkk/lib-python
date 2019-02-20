# Copyright (c) 2015-2019 Volodymyr Shymanskyy. See the file LICENSE for copying permission.
# Copyright (c) 2019 Anton Morozenko
import sys

VERSION = '0.2.2'

# todo change globally logging
# todo separate in log re-connect
# todo print list of registered events
# todo add to examples config call with logger
# todo notification event
# todo tweet call
# todo notify call
# todo MSG_REDIRECT = 41 ??
# todo MSG_DBG_PRINT = 55 ??
# todo add debug response statuses parse operation

# todo think about why this is needed
# MPY_SUPPORT_INSTRUCTION_1 = 'import machine'
# for itm in [MPY_SUPPORT_INSTRUCTION_1]:
#     try:
#         exec itm
#     except ImportError:
#         continue
#     except AttributeError:
#         pass

# micropython compatibility
try:
    import socket
    import time
    import struct
    import select
except ImportError:
    import usocket as socket
    import utime as time
    import ustruct as struct
    import uselect as select


def ticks_ms():
    return getattr(time, 'ticks_ms', lambda: int(time.time() * 1000))()


def sleep_ms(m_sec):
    return getattr(time, 'sleep_ms', lambda x: time.sleep(x // 1000))(m_sec)


LOGO = """
        ___  __          __
       / _ )/ /_ _____  / /__
      / _  / / // / _ \\/  '_/
     /____/_/\\_, /_//_/_/\\_\\
            /___/ for Python v""" + VERSION + "\n"


class BlynkException(Exception):
    pass


class Protocol(object):
    # todo const should be added according
    # https: // docs.micropython.org / en / latest / reference / constrained.html  # execution-phase
    MSG_RSP = 0
    MSG_LOGIN = 2
    MSG_PING = 6
    MSG_TWEET = 12
    MSG_EMAIL = 13
    MSG_NOTIFY = 14
    MSG_BRIDGE = 15
    MSG_HW_SYNC = 16
    MSG_INTERNAL = 17
    MSG_PROPERTY = 19
    MSG_HW = 20
    MSG_EVENT_LOG = 64

    MSG_HEAD_LEN = 5
    STATUS_SUCCESS = 200
    HEARTBEAT_PERIOD = 10
    MAX_CMD_BUFFER = 1024
    VIRTUAL_PIN_MAX_NUM = 32

    _msg_id = 1

    @staticmethod
    def _parse_msg_body(msg_body):
        return [itm.decode('ascii') for itm in msg_body.split(b'\0')]

    def _get_msg_id(self):
        self._msg_id += 1
        return self._msg_id if self._msg_id <= 0xFFFF else 1

    def _pack_msg(self, msg_type, *args):
        data = ('\0'.join([str(curr_arg) for curr_arg in args])).encode('ascii')
        return struct.pack('!BHH', msg_type, self._get_msg_id(), len(data)) + data

    def parse_response(self, rsp_data, expected_msg_type=None):
        msg_args = []
        msg_type, msg_id, h_data = struct.unpack('!BHH', rsp_data[:self.MSG_HEAD_LEN])
        if msg_id == 0:
            raise BlynkException('invalid msg_id == 0')
        elif h_data >= self.MAX_CMD_BUFFER:
            raise BlynkException('Command too long. Length = {}'.format(h_data))
        elif expected_msg_type is not None and msg_type != expected_msg_type:
            raise BlynkException('Not expected msg_type={} captured'.format(msg_type))
        elif msg_type in (self.MSG_RSP, self.MSG_PING, self.MSG_INTERNAL):
            pass
        elif msg_type in (self.MSG_HW, self.MSG_BRIDGE):
            msg_args = self._parse_msg_body(rsp_data[self.MSG_HEAD_LEN: self.MSG_HEAD_LEN + h_data])
        else:
            raise BlynkException('Unknown message type received "{}"'.format(msg_type))
        return msg_type, msg_id, h_data, msg_args

    def heartbeat_msg(self):
        return self._pack_msg(self.MSG_INTERNAL, 'ver', VERSION, 'buff-in', self.MAX_CMD_BUFFER, 'h-beat',
                              self.HEARTBEAT_PERIOD, 'dev', sys.platform + '-py')

    def login_msg(self, token):
        return self._pack_msg(self.MSG_LOGIN, token)

    def ping_reply_msg(self, msg_id, status):
        return self._pack_msg(self.MSG_RSP, msg_id, status)

    def virtual_write_msg(self, v_pin, *val):
        return self._pack_msg(self.MSG_HW, 'vw', v_pin, *val)

    # todo check multiple values support
    def virtual_sync_msg(self, *pins):
        return self._pack_msg(self.MSG_HW_SYNC, 'vr', *pins)

    def email_msg(self, to, subject, body):
        return self._pack_msg(self.MSG_EMAIL, to, subject, body)

    def notify_msg(self, msg):
        return self._pack_msg(self.MSG_NOTIFY, msg)


class Connection(Protocol):
    SOCK_MAX_TIMEOUT = 5  # 5 seconds, must be < self.HEARTBEAT_PERIOD
    SOCK_CONNECTION_TIMEOUT = 0.05
    SOCK_RECONNECT_DELAY = 1  # 1 second
    ERR_EAGAIN = 11
    ERR_ETIMEDOUT = 60
    STATE_DISCONNECTED = 0
    STATE_CONNECTING = 1
    STATE_AUTHENTICATING = 2
    STATE_AUTHENTICATED = 3

    RETRIES_TX_DELAY = 2
    RETRIES_TX_MAX_NUM = 3
    TASK_PERIOD_RES = 50  # 50ms

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
        while curr_retry_num <= self.RETRIES_TX_MAX_NUM:
            try:
                curr_retry_num += 1
                self._last_send_time = ticks_ms()
                return self.socket.send(data)
            except OSError as os_err:
                # todo add other errors handling aka subclass of socket err
                sleep_ms(self.RETRIES_TX_DELAY)

    # todo think about error handling
    def receive(self, length, timeout=0.0):
        try:
            rcv_buffer = b''
            self._set_socket_timeout(timeout)
            rcv_buffer += self.socket.recv(length)
            if len(rcv_buffer) >= length:
                rcv_buffer = rcv_buffer[:length]
            return rcv_buffer
        except OSError as os_err:
            # todo add as constant
            if str(os_err) == 'timed out':
                return b''
            if isinstance(os_err, int):
                # todo we need prove this socket_timeout value from poller?
                # todo remove
                print("OSError value = {}".format(int(os_err)))
                if int(os_err) in (self.ERR_EAGAIN, self.ERR_ETIMEDOUT):
                    return b''
            raise

    def is_server_alive(self):
        now = ticks_ms()
        heartbeat_ms = self.HEARTBEAT_PERIOD * 1000
        receive_delta = now - self._last_receive_time
        ping_delta = now - self._last_ping_time
        send_delta = now - self._last_send_time
        if receive_delta > heartbeat_ms * 1.5:
            return False
        if (ping_delta > heartbeat_ms / 10) and (send_delta > heartbeat_ms or receive_delta > heartbeat_ms):
            self.send(self.ping_reply_msg(self._get_msg_id(), 0))
            # todo remove
            print('Heartbeat time: {}'.format(now))
            self._last_ping_time = now
        return True

    def _get_socket(self, ssl_flag):
        try:
            self.state = self.STATE_CONNECTING
            self.socket = socket.socket()
            if ssl_flag:
                # todo add ssl support
                raise NotImplementedError
            self.socket.connect(socket.getaddrinfo(self.server, self.port)[0][4])
            self._set_socket_timeout(self.SOCK_CONNECTION_TIMEOUT)
            print('Blynk connection socket created')
        except Exception as g_exc:
            raise BlynkException('Connection with the Blynk servers failed: {}'.format(g_exc))

    # todo add invalid auth token STA_INVALID_TOKEN =(9)
    def _authenticate(self):
        print('Authenticating device...')
        self.state = self.STATE_AUTHENTICATING
        self.send(self.login_msg(self.token))
        rsp_data = self.receive(self.MAX_CMD_BUFFER, timeout=self.SOCK_MAX_TIMEOUT)
        if not rsp_data:
            raise BlynkException('Blynk authentication timed out')
        _, _, status, _ = self.parse_response(rsp_data, expected_msg_type=self.MSG_RSP)
        if status != self.STATUS_SUCCESS:
            raise BlynkException('Blynk authentication failed')
        self.state = self.STATE_AUTHENTICATED
        print('Access granted.')

    def _set_heartbeat(self):
        self.send(self.heartbeat_msg())
        rsp_data = self.receive(self.MAX_CMD_BUFFER, timeout=self.SOCK_MAX_TIMEOUT)
        if not rsp_data:
            raise BlynkException('Heartbeat reply timeout')
        _, _, status, _ = self.parse_response(rsp_data, expected_msg_type=self.MSG_RSP)
        if status != self.STATUS_SUCCESS:
            raise BlynkException('Heartbeat operation status= {}'.format(status))
        print("Heartbeat period = {} seconds. Happy Blynking!\n".format(self.HEARTBEAT_PERIOD))

    def connected(self):
        """
        Returns true when hardware is connected to Blynk Server, false if there is no active connection to Blynk server.
        @return: Boolean
        """
        return True if self.state == self.STATE_AUTHENTICATED else False


class Blynk(Connection):
    BLYNK_SERVER = "blynk-cloud.com"
    BLYNK_HTTP_PORT = 80
    CONNECT_CALL_TIMEOUT = 30  # 30sec

    VPIN_WILDCARD = '*'
    READ_VPIN_EVENT_BASENAME = 'read V'
    WRITE_VPIN_EVENT_BASENAME = 'write V'
    INTERNAL_EVENT_BASENAME = 'internal_'
    CONNECT_EVENT = 'connect'
    DISCONNECT_EVENT = 'disconnect'
    READ_ALL_VPIN_EVENT = READ_VPIN_EVENT_BASENAME + VPIN_WILDCARD
    WRITE_ALL_VPIN_EVENT = WRITE_VPIN_EVENT_BASENAME + VPIN_WILDCARD

    def __init__(self, token, server=BLYNK_SERVER, port=BLYNK_HTTP_PORT, ssl=True):
        self.token = token
        self.server = server
        self.port = port
        self.ssl = ssl
        self.state = self.STATE_DISCONNECTED
        self._start_time = ticks_ms()
        self._last_receive_time = self._start_time
        self._last_send_time = self._start_time
        self._last_ping_time = self._start_time
        self.events = {}
        print(LOGO)

    def config(self, token, server=BLYNK_SERVER, port=BLYNK_HTTP_PORT, ssl=False):
        """
        Allows you to manage network connection.
        @param token: auth token
        @param server: blynk server
        @param port: blynk port
        @param ssl: use ssl flag
        @return:
        """
        self.token = token
        self.server = server
        self.port = port
        self.ssl = ssl

    def connect(self, timeout=CONNECT_CALL_TIMEOUT):
        """
        Function will continue trying to connect to Blynk server.
        @param timeout: global function retry timeout. Default value = 30 seconds
        @return: connection status
        """
        end_time = time.time() + timeout
        while not self.connected():
            try:
                if self.state == self.STATE_DISCONNECTED:
                    self._get_socket(self.ssl_flag)
                    self._authenticate()
                    self._set_heartbeat()
                    self.call_handler(self.CONNECT_EVENT)
                    return True
            except BlynkException as b_exc:
                self.disconnect(b_exc)
                sleep_ms(self.TASK_PERIOD_RES)
            finally:
                if time.time() >= end_time:
                    return False

    def disconnect(self, err_msg=None):
        """
        Disconnects hardware from Blynk server
        @param err_msg: error message to print. Optional parameter
        @return: None
        """
        if self.socket is not None:
            self.socket.close()
        self.state = self.STATE_DISCONNECTED
        if err_msg:
            print('Error: {}. Connection closed'.format(err_msg))
        time.sleep(self.SOCK_RECONNECT_DELAY)
        self.call_handler(self.DISCONNECT_EVENT)

    def virtual_write(self, v_pin, *val):
        """
        Write data to virtual pin
        @param v_pin: pin number: Integer
        @param val: values to write
        @return: Returns the number of bytes sent
        """
        return self.send(self.virtual_write_msg(v_pin, *val))

    def virtual_sync(self, *v_pin):
        """
        Sync virtual pin/pins to get actual data.
        @param v_pin: single pin or multiple pins number
        @return: Returns the number of bytes sent
        """
        return self.send(self.virtual_sync_msg(*v_pin))

    def email(self, to, subject, body):
        """
        Send email from your hardware to any address.
        @param to: destination email address
        @param subject: email subject
        @param body: email body
        @return: Returns the number of bytes sent
        """
        return self.send(self.email_msg(to, subject, body))

    def handle_event(blynk, event_name):
        class Decorator(object):
            def __init__(self, func):
                self.func = func
                # wildcard 'read V*' and 'write V*' events handling
                if str(event_name) in (blynk.READ_ALL_VPIN_EVENT, blynk.WRITE_ALL_VPIN_EVENT):
                    event_base_name = str(event_name).split(blynk.VPIN_WILDCARD)[0]
                    for i in range(1, blynk.VIRTUAL_PIN_MAX_NUM + 1):
                        blynk.events['{}{}'.format(event_base_name, i)] = func
                        print('Registered {}{}'.format(event_base_name, i))
                else:
                    blynk.events[str(event_name)] = func

            def __call__(self):
                return self.func()

        return Decorator

    def call_handler(self, event, *args, **kwargs):
        print("Event: ['{}'] -> {}".format(event, args))
        if event in self.events.keys():
            self.events[event](*args, **kwargs)

    def process(self, msg_type, msg_id, msg_len, msg_args):
        if msg_type == self.MSG_RSP:
            # todo add status handling maybe
            print(msg_len)
        elif msg_type == self.MSG_PING:
            self.send(self.ping_reply_msg(msg_id, self.STATUS_SUCCESS))
        elif msg_type in (self.MSG_HW, self.MSG_BRIDGE):
            if len(msg_args) >= 2:
                if msg_args[0] == 'vw':
                    self.call_handler("{}{}".format(self.WRITE_VPIN_EVENT_BASENAME, msg_args[1]), msg_args[1],
                                      msg_args[2:])
                elif msg_args[0] == 'vr':
                    self.call_handler("{}{}".format(self.READ_VPIN_EVENT_BASENAME, msg_args[1]), msg_args[1])
        elif msg_type == self.MSG_INTERNAL:
            if len(msg_args) >= 2:
                self.call_handler("{}{}".format(self.INTERNAL_EVENT_BASENAME, msg_args[1]), msg_args[2:])

    # todo KeyboardInterrupt handle on all layers?
    def run(self):
        """
        This function should be called frequently to process incoming commands
        and perform housekeeping of Blynk connection.
        @return: None
        """
        if not self.connected():
            self.connect()
        else:
            try:
                rsp_data = self.receive(self.MAX_CMD_BUFFER, self.SOCK_CONNECTION_TIMEOUT)
                self._last_receive_time = ticks_ms()
                if rsp_data:
                    msg_type, msg_id, h_data, msg_args = self.parse_response(rsp_data)
                    self.process(msg_type, msg_id, h_data, msg_args)
                if not self.is_server_alive():
                    self.disconnect('Blynk server is offline')
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt: process terminated by user")
                sys.exit(0)
            except Exception as g_exc:
                print(g_exc)
                self.disconnect(g_exc)
