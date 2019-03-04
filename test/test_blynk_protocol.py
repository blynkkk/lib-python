import pytest
from blynklib import Protocol


class TestBlynkProtocol:
    def test_get_msg_id(self):
        p = Protocol()
        p._msg_id = 4
        msg_id = p._get_msg_id()
        assert msg_id == 5
