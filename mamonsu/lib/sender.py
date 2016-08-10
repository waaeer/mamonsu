# -*- coding: utf-8 -*-
import json
import time
from mamonsu.lib.plugin import Plugin


class Sender():

    def __init__(self):
        self._senders = []
        self._last_values = {}

    def update_senders(self, senders=[]):
        self._senders = senders

    def send(self, key, value, delta=None, host=None, clock=None):

        if clock is None:
            clock = int(time.time())

        if delta is not None:
            if isinstance(value, float) or isinstance(value, int):
                hash_key = '{0}.{1}'.format(host, key)
                if hash_key not in self._last_values:
                    self._last_values[hash_key] = (value, clock)
                    return
                else:
                    last_value = self._last_values[hash_key][0]
                    last_time = self._last_values[hash_key][1]
                    self._last_values[hash_key] = (value, clock)
                    if delta == Plugin.DELTA.speed_per_second:
                        value = float(value - last_value)/(clock - last_time)
                    if delta == Plugin.DELTA.simple_change:
                        value = float(value - last_value)

        for sender in self._senders:
            sender.send(key, value, host, clock)

    # helpers
    def json(self, val):
        return json.dumps(val)