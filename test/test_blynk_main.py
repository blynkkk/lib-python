# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest
from blynklib import Blynk, BlynkException


class TestBlynk:
    @pytest.fixture
    def bl(self):
        blynk = Blynk('1234', log=print)
        yield blynk

    def test_notify(self, bl, mocker):
        with mocker.patch.object(bl, 'send', return_value=10):
            result = bl.notify('123')
            assert result == 10

    def test_email(self, bl, mocker):
        with mocker.patch.object(bl, 'send', return_value=20):
            result = bl.email('1', '2', '3')
            assert result == 20

    def test_set_property(self, bl, mocker):
        with mocker.patch.object(bl, 'send', return_value=30):
            result = bl.set_property(1, '2', '3')
            assert result == 30

    def test_tweet(self, bl, mocker):
        with mocker.patch.object(bl, 'send', return_value=40):
            result = bl.tweet('123')
            assert result == 40

    def test_virtual_sync(self, bl, mocker):
        with mocker.patch.object(bl, 'send', return_value=50):
            result = bl.virtual_sync(20, 22)
            assert result == 50

    def test_virtual_write(self, bl, mocker):
        with mocker.patch.object(bl, 'send', return_value=60):
            result = bl.virtual_write(20, 'va1', 'val2')
            assert result == 60
