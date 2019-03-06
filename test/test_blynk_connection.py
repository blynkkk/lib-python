# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import pytest
import socket
from blynklib import Connection, BlynkException


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

    # todo python 3 issue investigate
    # TypeError: descriptor '__getattribute__' requires a '_socket.socket' object but received a 'type'
    # def test_send_error_retry_count(self, cb, mocker):
    #     cb._socket = socket.socket()
    #     with mocker.patch('socket.socket.send', side_effect=OSError('OS')):
    #         mocker.spy(socket.socket, 'send')
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
            with mocker.patch('socket.socket.recv', side_effect=IOError('[Errno 11]')):
                result = cb.receive(10, 1)
                assert result == b''

    def test_receive_etimeout(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
            with mocker.patch('socket.socket.recv', side_effect=OSError('[Errno 60]')):
                result = cb.receive(10, 1)
                assert result == b''

    def test_receive_raise_other_oserror(self, cb, mocker):
        cb._socket = socket.socket()
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
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

    def test_get_socket(self, cb, mocker):
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
            with mocker.patch('socket.socket.connect', return_value=None):
                cb._get_socket()
                assert cb._state == cb.CONNECTING

    def test_get_socket_exception(self, cb, mocker):
        with mocker.patch.object(cb, '_set_socket_timeout', return_value=None):
            with mocker.patch('socket.socket.connect', side_effect=BlynkException('BE')):
                with pytest.raises(BlynkException) as b_exc:
                    cb._get_socket()
                assert 'Connection with the Blynk server failed: BE' in str(b_exc)

    def test_authenticate(self, cb, mocker):
        with mocker.patch.object(cb, 'send', return_value=None):
            with mocker.patch.object(cb, 'receive', return_value=b'\x00\x00\x02\x00\xc8'):
                cb._authenticate()
                assert cb._state == cb.AUTHENTICATED

    def test_authenticate_invalid_auth_token(self, cb, mocker):
        with mocker.patch.object(cb, 'send', return_value=None):
            with mocker.patch.object(cb, 'receive', return_value=b'\x00\x00\x02\x00\x09'):
                with pytest.raises(BlynkException) as b_exc:
                    cb._authenticate()
                assert 'Invalid Auth Token' in str(b_exc)

    def test_authenticate_not_ok_status(self, cb, mocker):
        with mocker.patch.object(cb, 'send', return_value=None):
            with mocker.patch.object(cb, 'receive', return_value=b'\x00\x00\x02\x00\x19'):
                with pytest.raises(BlynkException) as b_exc:
                    cb._authenticate()
                assert 'Auth stage failed. Status=25' in str(b_exc)

    def test_authenticate_timeout(self, cb, mocker):
        with mocker.patch.object(cb, 'send', return_value=None):
            with mocker.patch.object(cb, 'receive', return_value=None):
                with pytest.raises(BlynkException) as b_exc:
                    cb._authenticate()
                assert 'Auth stage timeout' in str(b_exc)

    def test_set_heartbeat_timeout(self, cb, mocker):
        with mocker.patch.object(cb, 'send', return_value=None):
            with mocker.patch.object(cb, 'receive', return_value=None):
                with pytest.raises(BlynkException) as b_exc:
                    cb._set_heartbeat()
                assert 'Heartbeat stage timeout' in str(b_exc)

    def test_set_heartbeat_error_status(self, cb, mocker):
        with mocker.patch.object(cb, 'send', return_value=None):
            with mocker.patch.object(cb, 'receive', return_value=b'\x00\x00\x02\x00\x0e'):
                with pytest.raises(BlynkException) as b_exc:
                    cb._set_heartbeat()
                assert 'Set heartbeat returned code=14' in str(b_exc)

    def test_set_heartbeat_positive(self, cb, mocker):
        with mocker.patch.object(cb, 'send', return_value=None):
            with mocker.patch.object(cb, 'receive', return_value=b'\x00\x00\x02\x00\xc8'):
                cb._set_heartbeat()

    def test_connected_false(self, cb):
        result = cb.connected()
        assert result is False

    def test_connected_true(self, cb):
        cb._state = cb.AUTHENTICATED
        result = cb.connected()
        assert result is True
