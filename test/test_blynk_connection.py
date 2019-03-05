# -*- coding: utf-8 -*-
from __future__ import print_function
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
