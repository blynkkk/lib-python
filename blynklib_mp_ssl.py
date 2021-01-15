# Copyright (c) 2020 François Gervais
# See the file LICENSE for copying permission.

import time
import ussl as ssl

from blynklib_mp import Connection, BlynkError, IOError


class SslConnection(Connection):
    SOCK_SSL_TIMEOUT = const(1)

    def send(self, data):
        retries = self.RETRIES_TX_MAX_NUM
        while retries > 0:
            try:
                retries -= 1
                self._last_send_time = time.ticks_ms()
                return self._socket.write(data)
            except (IOError, OSError):
                sleep_ms(self.RETRIES_TX_DELAY)

    def receive(self, length, timeout):
        d_buff = b""
        try:
            self._set_socket_timeout(timeout)
            timeout = self.SOCK_SSL_TIMEOUT
            while not d_buff and timeout > 0:
                ret = self._socket.read(length)
                if ret:
                    d_buff += ret
                timeout -= self.SOCK_TIMEOUT
                time.sleep(self.SOCK_TIMEOUT)
            if len(d_buff) >= length:
                d_buff = d_buff[:length]
            return d_buff
        except (IOError, OSError) as err:
            if str(err) == "timed out":
                return b""
            if str(self.EAGAIN) in str(err) or str(self.ETIMEDOUT) in str(err):
                return b""
            raise

    def _get_socket(self):
        try:
            super()._get_socket()
            self.log("Using SSL socket...")
            self._socket = ssl.wrap_socket(self._socket)
            self._socket.setblocking(False)
        except Exception as g_exc:
            raise BlynkError("Server connection failed: {}".format(g_exc))
