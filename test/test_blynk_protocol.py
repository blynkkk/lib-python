# -*- coding: utf-8 -*-
import sys
import pytest
from blynklib import Protocol, BlynkError


class TestBlynkProtocol:
    @pytest.fixture
    def pb(self):
        protocol = Protocol()
        yield protocol

    def test_get_msg_id(self, pb):
        pb._msg_id = 4
        msg_id = pb._get_msg_id()
        assert msg_id == 5

    def test_get_msg_id_before_loop(self, pb):
        pb._msg_id = 0xFFFE
        msg_id = pb._get_msg_id()
        assert msg_id == 0xFFFF

    def test_get_msg_id_after_loop(self, pb):
        pb._msg_id = 0xFFFF
        msg_id = pb._get_msg_id()
        assert msg_id == 0

    def test_get_msg_id_defined(self, pb):
        pb._msg_id = 0xFFFF
        msg_id = pb._get_msg_id(msg_id=17)
        assert msg_id == 17

    def test_pack_msg(self, pb):
        msg_type = 20
        args = ['test', 1234, 745, 'abcde']
        result = pb._pack_msg(msg_type, *args)
        assert result == b'\x14\x00\x01\x00\x13test\x001234\x00745\x00abcde'

    def test_pack_msg_no_args(self, pb):
        msg_type = 15
        args = []
        result = pb._pack_msg(msg_type, *args)
        assert result == b'\x0f\x00\x01\x00\x00'

    def test_pack_msg_unicode(self, pb):
        if sys.version_info[0] == 2:
            pytest.skip('Python2 unicode compatibility issue')

        msg_type = 20
        args = ['ёж']
        result = pb._pack_msg(msg_type, *args)
        assert result == b'\x14\x00\x01\x00\x04\xd1\x91\xd0\xb6'

    def test_parse_response_msg_hw(self, pb):
        data = b'\x14\x00\x02\x00\x13test\x001234\x00745\x00abcde'
        msg_buffer = 1024
        result = pb.parse_response(data, msg_buffer)
        assert result == (20, 2, 19, [u'test', u'1234', u'745', u'abcde'])

    def test_parse_response_msg_id_0(self, pb):
        data = b'\x14\x00\x00\x00\x13test\x001234\x00745\x00abcde'
        msg_buffer = 100
        with pytest.raises(BlynkError) as b_err:
            pb.parse_response(data, msg_buffer)
        assert 'invalid msg_id == 0' == str(b_err.value)

    def test_parse_response_more_data_than_buffer(self, pb):
        data = b'\x14\x00\x02\x00\x13test\x001234\x00745\x00abcde'
        msg_buffer = 10
        with pytest.raises(BlynkError) as b_err:
            pb.parse_response(data, msg_buffer)
        assert 'Command too long' in str(b_err.value)

    def test_parse_response_msg_ping(self, pb):
        data = b'\x06\x00\x04\x00\x13test\x001234\x00745\x00abcde'
        msg_buffer = 100
        result = pb.parse_response(data, msg_buffer)
        assert result == (6, 4, 19, [])

    def test_parse_response_corrupted_data(self, pb):
        data = b'\xd1\x91\xd0\xb6'
        msg_buffer = 100
        with pytest.raises(Exception) as exc:
            pb.parse_response(data, msg_buffer)
        assert 'Message parse error:' in str(exc.value)

    def test_parse_response_wrong_msg_type(self, pb):
        data = b'\x86\x00\x04\x00\x13test\x001234\x00745\x00abcde'
        msg_buffer = 100
        with pytest.raises(BlynkError) as b_err:
            pb.parse_response(data, msg_buffer)
        assert "Unknown message type: '134'" in str(b_err.value)

    def test_parse_response_msg_hw_unicode(self, pb):
        data = b'\x14\x00\x02\x00\x04\xd1\x91\xd0\xb6'
        msg_buffer = 1024
        result = pb.parse_response(data, msg_buffer)
        assert result == (20, 2, 4, [u'ёж'])

    def test_heartbeat_msg(self, pb):
        result = pb.heartbeat_msg(20, 2048)
        assert result == b'\x11\x00\x01\x00+ver\x000.2.6\x00buff-in\x002048\x00h-beat\x0020\x00dev\x00python'

    def test_login_msg(self, pb):
        result = pb.login_msg('1234')
        assert result == b'\x02\x00\x01\x00\x041234'

    def test_ping_msg(self, pb):
        result = pb.ping_msg()
        assert result == b'\x06\x00\x01\x00\x00'

    def test_response_msg(self, pb):
        result = pb.response_msg(202)
        assert result == b'\x00\x00\x01\x00\x03202'

    def test_virtual_write_msg(self, pb):
        result = pb.virtual_write_msg(127, 'abc', 123)
        assert result == b'\x14\x00\x01\x00\x0evw\x00127\x00abc\x00123'

    def test_virtual_sync_msg(self, pb):
        result = pb.virtual_sync_msg(1, 24)
        assert result == b'\x10\x00\x01\x00\x07vr\x001\x0024'

    def test_email_msg(self, pb):
        result = pb.email_msg('a@b.com', 'Test', 'MSG')
        assert result == b'\r\x00\x01\x00\x10a@b.com\x00Test\x00MSG'

    def test_tweet_msg(self, pb):
        result = pb.tweet_msg('tweet_msg_test')
        assert result == b'\x0c\x00\x01\x00\x0etweet_msg_test'

    def test_notify_msg(self, pb):
        result = pb.notify_msg('app_msg_test')
        assert result == b'\x0e\x00\x01\x00\x0capp_msg_test'

    def test_set_property_msg(self, pb):
        result = pb.set_property_msg(10, 'color', '#FF00EE')
        assert result == b'\x13\x00\x01\x00\x1010\x00color\x00#FF00EE'

    def test_internal_msg(self, pb):
        result = pb.internal_msg('rtc', 'sync')
        assert result == b'\x11\x00\x01\x00\x08rtc\x00sync'
