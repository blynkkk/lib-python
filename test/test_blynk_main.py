# -*- coding: utf-8 -*-
from __future__ import print_function
import socket
import pytest
import blynklib


class TestBlynk:
    @pytest.fixture
    def bl(self):
        blynk = blynklib.Blynk('1234', log=print)
        yield blynk

    def test_connect(self, bl, mocker):
        mocker.patch.object(bl, 'connected', return_value=False)
        mocker.patch.object(bl, '_get_socket', return_value=None)
        mocker.patch.object(bl, '_authenticate', return_value=None)
        mocker.patch.object(bl, '_set_heartbeat', return_value=None)
        mocker.patch.object(bl, 'call_handler', return_value=None)
        mocker.patch.object(blynklib, 'ticks_ms', return_value=42)
        result = bl.connect()
        assert result is True
        assert bl._last_rcv_time == 42

    def test_connect_exception(self, bl, mocker):
        mocker.patch.object(bl, 'connected', return_value=False)
        mocker.patch.object(bl, '_get_socket', return_value=None)
        mocker.patch.object(bl, '_authenticate', side_effect=blynklib.BlynkError())
        mocker.patch.object(bl, 'disconnect', return_value=None)
        mocker.patch('time.sleep', return_value=None)
        mocker.spy(bl, 'disconnect')
        result = bl.connect(0.001)
        assert result is False
        assert bl.disconnect.call_count > 1

    def test_connect_redirect_exception(self, bl, mocker):
        mocker.patch.object(bl, 'connected', return_value=False)
        mocker.patch.object(bl, '_get_socket', return_value=None)
        mocker.patch.object(bl, '_authenticate', side_effect=blynklib.RedirectError('127.0.0.1', 4444))
        mocker.patch.object(bl, 'disconnect', return_value=None)
        mocker.patch('time.sleep', return_value=None)
        mocker.spy(bl, 'disconnect')
        result = bl.connect(0.001)
        assert result is False
        assert bl.disconnect.call_count > 1
        assert bl.server == '127.0.0.1'
        assert bl.port == 4444

    def test_connect_timeout(self, bl, mocker):
        bl._state = bl.CONNECTING
        mocker.patch.object(bl, 'connected', return_value=False)
        result = bl.connect(0.001)
        assert result is False

    def test_disconnect(self, bl, mocker):
        bl._socket = socket.socket()
        mocker.patch('time.sleep', return_value=None)
        bl.disconnect('123')

    def test_virtual_write(self, bl, mocker):
        mocker.patch.object(bl, 'send', return_value=10)
        result = bl.virtual_write(20, 'va1', 'val2')
        assert result == 10

    def test_virtual_sync(self, bl, mocker):
        mocker.patch.object(bl, 'send', return_value=20)
        result = bl.virtual_sync(20, 22)
        assert result == 20

    def test_email(self, bl, mocker):
        mocker.patch.object(bl, 'send', return_value=30)
        result = bl.email('1', '2', '3')
        assert result == 30

    def test_tweet(self, bl, mocker):
        mocker.patch.object(bl, 'send', return_value=40)
        result = bl.tweet('123')
        assert result == 40

    def test_notify(self, bl, mocker):
        mocker.patch.object(bl, 'send', return_value=50)
        result = bl.notify('123')
        assert result == 50

    def test_set_property(self, bl, mocker):
        mocker.patch.object(bl, 'send', return_value=60)
        result = bl.set_property(1, '2', '3')
        assert result == 60

    def test_internal(self, bl, mocker):
        mocker.patch.object(bl, 'send', return_value=70)
        result = bl.internal('rtc', 'sync')
        assert result == 70

    def test_hadle_event(self, bl):
        bl._events = {}

        @bl.handle_event('connect')
        def connect_handler():
            pass

        @bl.handle_event('disconnect')
        def disconnect_handler():
            pass

        assert 'connect' in bl._events.keys()
        assert 'disconnect' in bl._events.keys()

    def test_read_wildcard_event(self, bl):
        bl._events = {}

        @bl.handle_event('read v*')
        def read_pin_handler():
            pass

        assert 'read v10' in bl._events.keys()
        assert len(bl._events.keys()) == bl.VPIN_MAX_NUM + 1

    def test_write_wildcard_event(self, bl):
        bl._events = {}

        @bl.handle_event('write v*')
        def write_pin_handler():
            pass

        assert 'write v5' in bl._events.keys()
        assert len(bl._events.keys()) == bl.VPIN_MAX_NUM + 1

    def test_call_handler(self, bl):
        bl._events = {}

        @bl.handle_event('write v2')
        def write_pin_handler(arg1, kwarg1=None):
            bl._state = 'TEST{}{}'.format(arg1, kwarg1)

        bl.call_handler('write v2', 12, kwarg1='34')
        assert bl._state == 'TEST1234'

    def test_process_rsp(self, bl, mocker):
        mocker.spy(bl, 'log')
        bl.process(bl.MSG_RSP, 100, 200, [])
        assert bl.log.call_count == 1

    def test_process_ping(self, bl, mocker):
        mocker.patch.object(bl, 'send', return_value=None)
        mocker.spy(bl, 'send')
        bl.process(bl.MSG_PING, 100, 200, [])
        assert bl.send.call_count == 1

    def test_process_internal(self, bl, mocker):
        bl._events = {}

        @bl.handle_event('internal_xyz')
        def internal_handler(*args):
            bl._status = 'INTERNAL TEST {}'.format(*args)

        mocker.patch.object(bl, 'send', return_value=None)
        bl.process(bl.MSG_INTERNAL, 100, 20, ['xyz', 'add', 2])
        assert bl._status == "INTERNAL TEST ['add', 2]"

    def test_process_write(self, bl, mocker):
        bl._events = {}

        @bl.handle_event('write V4')
        def write_handler(pin, *values):
            bl._status = 'WRITE TEST{}'.format(*values)

        mocker.patch.object(bl, 'send', return_value=None)
        bl.process(bl.MSG_HW, 100, 200, ['vw', 4, 1, 2])
        assert bl._status == 'WRITE TEST[1, 2]'

    def test_process_read(self, bl, mocker):
        bl._events = {}

        @bl.handle_event('read V7')
        def read_handler(pin):
            bl._status = 'READ TEST{}'.format(pin)

        mocker.patch.object(bl, 'send', return_value=None)
        bl.process(bl.MSG_HW, 100, 200, ['vr', 7])
        assert bl._status == 'READ TEST7'
