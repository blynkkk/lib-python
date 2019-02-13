# Copyright (c) 2015-2019 Volodymyr Shymanskyy. See the file LICENSE for copying permission.
# Copyright (c) 2019 Anton Morozenko
import socket
import struct
import time
import sys

VERSION = '0.2.1'
# todo change globally logging

for itm in ('from machine import idle', 'getattr(time, "ticks_ms")'):
    try:
        exec itm
    except ImportError:
        idle = lambda: 0
        continue
    except AttributeError:
        ticks_ms = lambda: int(time.time() * 1000)
        sleep_ms = lambda x: time.sleep(x // 1000)
        ticks_diff = lambda x, y: y - x

# def time_ms():
#     return getattr(time, 'ticks_ms', lambda: int(time.time() * 1000))()
#
#
# def sleep_ms(ms):
#     return getattr(time, 'sleep_ms', lambda x: time.sleep(x // 1000))(ms)
#
#
# def time_diff_ms(start_t, end_t):
#     return getattr(time, 'ticks_diff', lambda x, y: y - x)(start_t, end_t)


LOGO = """
        ___  __          __
       / _ )/ /_ _____  / /__
      / _  / / // / _ \\/  '_/
     /____/_/\\_, /_//_/_/\\_\\
            /___/ for Python v""" + VERSION + "\n"


class BlynkException(Exception):
    pass


class VrPin:
    def __init__(self, read=None, write=None):
        self.read = read
        self.write = write


class Protocol(object):
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
    # MSG_REDIRECT = 41  # TODO: not implemented
    # MSG_DBG_PRINT = 55  # TODO: not implemented
    MSG_HEAD_LEN = 5
    STATUS_SUCCESS = 200
    HEARTBEAT_PERIOD = 10
    MAX_CMD_BUFFER = 1024

    _vr_pins = {}
    _msg_id = 1

    def _get_msg_id(self):
        self._msg_id += 1
        return self._msg_id if self._msg_id <= 0xFFFF else 1

    def _pack_msg(self, msg_type, *args):
        data = ('\0'.join([str(curr_arg) for curr_arg in args])).encode('ascii')
        return struct.pack('!BHH', msg_type, self._get_msg_id(), len(data)) + data

    def parse_response(self, rsp_data, expected_msg_type=None):
        msg_type, msg_id, h_data = struct.unpack('!BHH', rsp_data[:self.MSG_HEAD_LEN])
        if msg_id == 0:
            raise BlynkException('invalid msg_id == 0')
        elif h_data >= self.MAX_CMD_BUFFER:
            raise BlynkException('Command too long. Length = {}'.format(h_data))
        elif expected_msg_type is not None and msg_type != expected_msg_type:
            raise BlynkException('Not expected msg_type={} captured'.format(msg_type))
        elif msg_type in (self.MSG_RSP, self.MSG_PING, self.MSG_HW, self.MSG_BRIDGE, self.MSG_INTERNAL):
            pass
        else:
            raise BlynkException('Unknown message type received "{}"'.format(msg_type))
        extra_data = rsp_data[self.MSG_HEAD_LEN: self.MSG_HEAD_LEN + h_data]
        return msg_type, msg_id, h_data, extra_data

    def heartbeat_msg(self):
        return self._pack_msg(self.MSG_INTERNAL, 'ver', VERSION, 'buff-in', self.MAX_CMD_BUFFER, 'h-beat',
                              self.HEARTBEAT_PERIOD, 'dev', sys.platform + '-py')

    def login_msg(self, token):
        return self._pack_msg(self.MSG_LOGIN, token)

    def virtual_write_msg(self, v_pin, *val):
        return self._pack_msg(self.MSG_HW, 'vw', v_pin, *val)

    def virtual_read_msg(self, v_pin):
        return self._pack_msg(self.MSG_HW, 'vr', v_pin)

    def ping_reply_msg(self, msg_id, status):
        return self._pack_msg(self.MSG_RSP, msg_id, status)

    # todo review
    # def VIRTUAL_READ(blynk, pin):
    #     class Decorator:
    #         def __init__(self, func):
    #             self.func = func
    #             blynk._vr_pins[pin] = VrPin(func, None)
    #
    #         def __call__(self):
    #             return self.func()
    #
    #     return Decorator

    # todo review
    # def VIRTUAL_WRITE(blynk, pin):
    #     class Decorator:
    #         def __init__(self, func):
    #             self.func = func
    #             blynk._vr_pins[pin] = VrPin(None, func)
    #
    #         def __call__(self):
    #             return self.func()
    #
    #     return Decorator


class Connection(Protocol):
    SOCK_MIN_TIMEOUT = 1  # 1 second
    SOCK_MAX_TIMEOUT = 5  # 5 seconds, must be < self.HEARTBEAT_PERIOD
    SOCK_NON_BLOCK_TIMEOUT = 0
    SOCK_RECONNECT_DELAY = 1  # 1 second
    SOCK_EAGAIN = 11
    STATE_DISCONNECTED = 0
    STATE_CONNECTING = 1
    STATE_AUTHENTICATING = 2
    STATE_AUTHENTICATED = 3
    CONNECTION_TIMEOUT = 0.05
    RETRIES_TX_DELAY = 2
    RETRIES_TX_MAX_NUM = 3
    IDLE_TIME_MS = 20
    TASK_PERIOD_RES = 50  # 50ms
    CONNECT_CALL_TIMEOUT = 30  # 30sec

    token = None
    server = None
    port = None
    state = None
    socket = None
    ssl_flag = False
    _last_receive_time = 0
    _last_ping_time = 0
    _last_send_time = 0

    # todo maybe add Blynk Error or some other return 0?
    def send(self, data):
        curr_retry_num = 0
        while curr_retry_num <= self.RETRIES_TX_MAX_NUM:
            try:
                self._last_send_time = ticks_ms()
                return self.socket.send(data)
            except (socket.error, socket.timeout):
                sleep_ms(self.RETRIES_TX_DELAY)
                curr_retry_num += 1

    # todo think about error handling
    def receive(self, length, timeout=0):
        try:
            rcv_buffer = b''
            self.socket.settimeout(timeout)
            rcv_buffer += self.socket.recv(length)
            if len(rcv_buffer) >= length:
                rcv_buffer = rcv_buffer[:length]
            return rcv_buffer
        except socket.timeout:
            return b''
        except socket.error as s_err:
            if s_err.args[0] == self.SOCK_EAGAIN:
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
            print('Ping {}-{}'.format(now, self._last_ping_time))
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
            self.socket.settimeout(self.CONNECTION_TIMEOUT)
            print('Blynk connection socket created')
        except Exception as g_exc:
            raise BlynkException('Connection with the Blynk servers failed: {}'.format(g_exc))

    # todo maybe remove
    def wait(self, start_time, delay):
        while ticks_diff(start_time, ticks_ms()) < delay:
            #sleep_ms(self.IDLE_TIME_MS)
            idle()
        return start_time + delay

    # todo add invalid auth token STA_INVALID_TOKEN =(9)
    def _authenticate(self):
        print('Authenticating device...')
        self.state = self.STATE_AUTHENTICATING
        self.send(self.login_msg(self.token))
        rsp_data = self.receive(self.MAX_CMD_BUFFER, timeout=self.SOCK_MAX_TIMEOUT)
        if not rsp_data:
            raise BlynkException('Blynk authentication timed out')
        msg_type, msg_id, status, _ = self.parse_response(rsp_data, expected_msg_type=self.MSG_RSP)
        if status != self.STATUS_SUCCESS:
            raise BlynkException('Blynk authentication failed')
        self.state = self.STATE_AUTHENTICATED
        print('Access granted.')

    def _set_heartbeat(self):
        self.send(self.heartbeat_msg())
        rsp_data = self.receive(self.MAX_CMD_BUFFER, timeout=self.SOCK_MAX_TIMEOUT)
        if not rsp_data:
            raise BlynkException('Heartbeat reply timeout')
        msg_type, msg_id, status, _ = self.parse_response(rsp_data, expected_msg_type=self.MSG_RSP)
        if status != self.STATUS_SUCCESS:
            raise BlynkException('Heartbeat operation status= {}'.format(status))
        print("Heartbeat period = {} seconds. Happy Blynking!".format(self.HEARTBEAT_PERIOD))

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
        if type(self.socket) == socket.socket:
            self.socket.close()
        self.state = self.STATE_DISCONNECTED
        if err_msg:
            print('Error: {}. Connection closed'.format(err_msg))
        time.sleep(self.SOCK_RECONNECT_DELAY)

    def connected(self):
        """
        Returns true when hardware is connected to Blynk Server, false if there is no active connection to Blynk server.
        @return: Boolean
        """
        return True if self.state == self.STATE_AUTHENTICATED else False


class Blynk(Connection):
    BLYNK_SERVER = "blynk-cloud.com"
    BLYNK_HTTP_PORT = 80

    def __init__(self, token, server=BLYNK_SERVER, port=BLYNK_HTTP_PORT, ssl=True):
        self.token = token
        self.server = server
        self.port = port
        self.ssl = ssl
        self.state = self.STATE_DISCONNECTED
        self._start_time = 0
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

    def virtual_write(self, v_pin, *val):
        """
        Write data to virtual pin
        @param v_pin: pin number: Integer
        @param val: values to write
        @return: Returns the number of bytes sent
        """
        return self.send(self.virtual_write_msg(v_pin, *val))

    # todo hmm maybe here some trick with parse response
    def virtual_read(self, v_pin):
        """
        Read data from virtual pin
        @param v_pin: pin number: Integer
        @return: Returns the number of bytes sent
        """
        return self.send(self.virtual_read_msg(v_pin))

    # todo think about name
    def process(self, msg_type, msg_id, msg_len, extra_data):
        if msg_type == self.MSG_RSP:
            # todo add status handling maybe
            print(msg_len)
        elif msg_type == self.MSG_PING:
            self.send(self.ping_reply_msg(msg_id, self.STATUS_SUCCESS))
        elif msg_type in (self.MSG_HW, self.MSG_BRIDGE):
            if extra_data:
                # todo here put real logic
                print('Captured data {}'.format(extra_data))
                # self._handle_hw(rsp_data)
        elif msg_type == self.MSG_INTERNAL:
            pass

    # todo remove this description for run
    # Blynk.run()
    #
    # This function should be called frequently to process incoming commands
    # and perform housekeeping of Blynk connection. It is usually called in void loop() {}.

    def run(self):
        self._start_time = ticks_ms()
        self._last_receive_time = self._start_time
        self._last_send_time = self._start_time
        self._last_ping_time = self._start_time
        # todo out queue and input queues
        # todo add keyboard interrupt
        while True:
            self.connect()
            while self.connected():
                try:
                    rsp_data = self.receive(self.MSG_HEAD_LEN, self.SOCK_NON_BLOCK_TIMEOUT)
                    self._last_receive_time = ticks_ms()
                    if rsp_data:
                        msg_type, msg_id, h_data, extra_data = self.parse_response(rsp_data)
                        self.process(msg_type, msg_id, h_data, extra_data)
                    else:
                        #time.sleep(self.IDLE_TIME_MS//1000)
                        #sleep_ms(self.IDLE_TIME_MS)
                        #self._start_time = self._start_time + self.IDLE_TIME_MS
                        self._start_time = self.wait(self._start_time, self.IDLE_TIME_MS)
                    if not self.is_server_alive():
                        self.disconnect('Blynk server is offline')
                        break
                except Exception as g_exc:
                    print(g_exc)
                    self.disconnect(g_exc)


# todo remove this test block after all
if __name__ == "__main__":
    with open('TOKEN.txt') as t_file:
        auth_t = t_file.readline().strip()
    BLYNK = Blynk(auth_t, port=80, ssl=False)
    BLYNK.config(auth_t, server="blynk-cloud.com", port=80, ssl=False)
    # BLYNK.connect(timeout=10)
    # print(BLYNK.connected())
    # BLYNK.disconnect('Testing disconnect')
    # print(BLYNK.connected())
    BLYNK.run()
