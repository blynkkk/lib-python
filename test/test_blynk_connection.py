# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import pytest
import socket
from blynklib import Connection


class TestBlynkConnection:
    @pytest.fixture
    def cb(self):
        connection = Connection('1234', log=print)
        yield connection

    def test_set_socket_timeout_positive(self, cb):
        in_timeout = 10
        cb._socket = socket.socket()
        cb._set_socket_timeout(in_timeout)
        timeout = cb._socket.gettimeout()
        assert timeout == in_timeout

    def test_set_socket_timeout_via_poll(self, cb):
        in_timeout = 10
        cb._socket = 2222
        cb._set_socket_timeout(in_timeout)

    def test_send(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch('socket.socket.send', return_value=5):
            result = cb.send('1234')
            assert result == 5

    def test_send_ioerror(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch('socket.socket.send', side_effect=IOError('IO')):
            result = cb.send('1234')
            assert result is None

    def test_send_oserror(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch('socket.socket.send', side_effect=OSError('OS')):
            result = cb.send('1234')
            assert result is None

    # todo spy modify - AttributeError: 'socket' object attribute 'send' is read-only
    # def test_send_error_retry_count(self, cb, mocker):
    #     cb._socket = socket.socket()
    #     with mocker.patch('socket.socket.send', side_effect=OSError('OS')):
    #         mocker.spy(cb._socket, 'send')
    #         cb.send('1234')
    #         assert cb._socket.send.call_count == 3

    def test_receive(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
            with mocker.patch('socket.socket.recv', return_value=b'12345'):
                result = cb.receive(10, 1)
                assert result == b'12345'

    def test_receive_timeout(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
            with mocker.patch('socket.socket.recv', side_effect=OSError('timed out')):
                result = cb.receive(10, 1)
                assert result == b''

    def test_receive_eagain(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
            # with mocker.patch.object(cb._socket, 'recv', side_effect=IOError('[Errno 11]')):
            with mocker.patch('socket.socket.recv', side_effect=IOError('[Errno 11]')):
                result = cb.receive(10, 1)
                assert result == b''

    def test_receive_etimeout(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
            # with mocker.patch.object(cb._socket, 'recv', side_effect=OSError('[Errno 60]')):
            with mocker.patch('socket.socket.recv', side_effect=OSError('[Errno 60]')):
                result = cb.receive(10, 1)
                assert result == b''

    def test_receive_raise_other_oserror(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
            # with mocker.patch.object(cb._socket, 'recv', side_effect=OSError('[Errno 13]')):
            with mocker.patch('socket.socket.recv', side_effect=OSError('[Errno 13]')):
                with pytest.raises(OSError) as os_err:
                    cb.receive(10, 1)
                assert '[Errno 13]' in str(os_err)

    def test_is_server_alive_negative(self, cb):
        result = cb.is_server_alive()
        assert result is False

    def test_is_server_alive_positive_ping(self, cb, mocker):
        cb._last_rcv_time = int(time.time() * 1000)
        with mocker.patch.object(cb, 'send', return_value=None):
            result = cb.is_server_alive()
            assert result is True

    def test_is_server_alive_positive_no_ping_1(self, cb):
        cb._last_rcv_time = int(time.time() * 1000)
        cb._last_ping_time = int(time.time() * 1000)
        result = cb.is_server_alive()
        assert result is True

    def test_is_server_alive_positive_no_ping_2(self, cb):
        cb._last_rcv_time = int(time.time() * 1000)
        cb._last_send_time = int(time.time() * 1000)
        result = cb.is_server_alive()
        assert result is True
