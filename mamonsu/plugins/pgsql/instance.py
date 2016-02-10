# -*- coding: utf-8 -*-

from mamonsu.lib.plugin import Plugin
from ._pool import Pooler


class Instance(Plugin):

    Items = [
        # key, zbx_key, description,
        #    ('graph name', color, side), units, delta

        ('xact_commit', 'transactions[total]', 'transactions: total',
            ('PostgreSQL instance: rate', '0000CC', 1), None, 1),
        ('blks_hit', 'blocks[hit]', 'blocks: hit',
            ('PostgreSQL instance: rate', '00CC00', 0), None, 1),
        ('blks_read', 'blocks[read]', 'blocks: read',
            ('PostgreSQL instance: rate', 'CC0000', 0), None, 1),

        ('conflicts', 'events[conflicts]', 'event: conflicts',
            ('PostgreSQL instance: events', '0000CC', 0), None, 2),
        ('deadlocks', 'events[deadlocks]', 'event: deadlocks',
            ('PostgreSQL instance: events', '000000', 0), None, 2),
        ('xact_rollback', 'events[xact_rollback]', 'event: rollbacks',
            ('PostgreSQL instance: events', 'CC0000', 0), None, 2),

        ('temp_bytes', 'temp[bytes]', 'temp: bytes written',
            ('PostgreSQL instance: temp files', 'CC0000', 0), 'b', 2),
        ('temp_files', 'temp[files]', 'temp: files created',
            ('PostgreSQL instance: temp files', '0000CC', 1), None, 2),

        # stacked
        ('tup_deleted', 'tuples[deleted]', 'tuples: deleted',
            ('PostgreSQL instance: tuples', '000000', 0), None, 1),
        ('tup_fetched', 'tuples[fetched]', 'tuples: fetched',
            ('PostgreSQL instance: tuples', '0000CC', 1), None, 1),
        ('tup_inserted', 'tuples[inserted]', 'tuples: inserted',
            ('PostgreSQL instance: tuples', '00CC00', 0), None, 1),
        ('tup_returned', 'tuples[returned]', 'tuples: returned',
            ('PostgreSQL instance: tuples', 'CC00CC', 0), None, 1),
        ('tup_updated', 'tuples[updated]', 'tuples: updated',
            ('PostgreSQL instance: tuples', 'CC0000', 0), None, 1),
    ]

    def run(self, zbx):
        params = ['sum({0}) as {0}'.format(x[0]) for x in self.Items]
        result = Pooler.query('select {0} from pg_stat_database'.format(
            ', '.join(params)))
        for idx, val in enumerate(result[0]):
            key, val = 'pgsql.{0}'.format(
                self.Items[idx][1]), int(val)
            zbx.send(key, val)
        del params, result

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': 'pgsql.{0}'.format(item[1]),
                'name': 'PostgreSQL {0}'.format(item[2]),
                'value_type': 3,
                'units': item[4],
                'delta': item[5]
            })
        return result

    def graphs(self, template):
        graphs_name = [
            'PostgreSQL instance: rate',
            'PostgreSQL instance: events',
            'PostgreSQL instance: temp files',
            'PostgreSQL instance: tuples']
        result = ''
        for name in graphs_name:
            items = []
            for item in self.Items:
                if item[3][0] == name:
                    items.append({
                        'key': 'pgsql.{0}'.format(item[1]),
                        'color': item[3][1],
                        'yaxisside': item[3][2]
                    })
            graph = {'name': name, 'items': items}
            result += template.graph(graph)

        return result
