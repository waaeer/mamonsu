import mamonsu.lib.platform as platform
from distutils.version import LooseVersion
from ._connection import Connection, ConnectionInfo


class Pool(ConnectionInfo):

    ExcludeDBs = ['template0', 'template1', 'postgres']

    SQL = {
        # query type: ( 'if_not_installed', 'if_installed' )
        'replication_lag_master_query': (
            'select 1 as replication_lag_master_query',
            'select public.mamonsu_timestamp_master_update()'
        ),
        'replication_lag_slave_query': (
            'select extract(epoch from now()-pg_last_xact_replay_timestamp())',
            'select public.mamonsu_timestamp_get()'
        ),
        'count_xlog_files': (
            "select count(*) from pg_catalog.pg_ls_dir('pg_xlog')",
            'select public.mamonsu_count_xlog_files()'
        ),
        'count_autovacuum': (
            """select count(*) from pg_catalog.pg_stat_activity where
query like '%%autovacuum%%' and state <> 'idle'
and pid <> pg_catalog.pg_backend_pid()
        """,
            'select public.mamonsu_count_autovacuum()'
        ),
        'buffer_cache': (
            """select
sum(1) * 8 * 1024 as size,
sum(case when usagecount > 1 then 1 else 0 end) * 8 * 1024 as twice_used,
sum(case isdirty when true then 1 else 0 end) * 8 * 1024 as dirty
from public.pg_buffercache""",
            'select size, twice_used, dirty from public.mamonsu_buffer_cache()'
        ),
    }

    def __init__(self):
        super(Pool, self).__init__()
        self.all_connections = {}
        self._cache = {
            'server_version': {'storage': {}},
            'bootstrap': {'storage': {}, 'counter': 0, 'cache': 10},
            'recovery': {'storage': {}, 'counter': 0, 'cache': 10},
            'pgpro': {'storage': {}},
            'pgproee': {'storage': {}}
        }

    def connection_string(self, db=None):
        self._init_connection(db)
        return self.all_connections[db].conn_str()

    def query(self, query, db=None):
        if db is None:
            db = self.db
        self._init_connection(db)
        return self.all_connections[db].query(query)

    def server_version(self, db=None):
        if db in self._cache['server_version']['storage']:
            return self._cache['server_version']['storage'][db]
        if platform.PY2:
            result = self.query('show server_version', db)[0][0]
        elif platform.PY3:
            result = bytes(
                self.query('show server_version', db)[0][0], 'utf-8')
        self._cache['server_version']['storage'][db] = '{0}'.format(
            result.decode('ascii'))
        return self._cache['server_version']['storage'][db]

    def server_version_greater(self, version, db=None):
        return self.server_version(db) >= LooseVersion(version)

    def server_version_less(self, version, db=None):
        return self.server_version(db) <= LooseVersion(version)

    def in_recovery(self, db=None):
        if db in self._cache['recovery']['storage']:
            if self._cache['recovery']['counter'] < self._cache['recovery']['cache']:
                self._cache['recovery']['counter'] += 1
                return self._cache['recovery']['storage'][db]
        self._cache['recovery']['counter'] = 0
        self._cache['recovery']['storage'][db] = self.query(
            "select pg_catalog.pg_is_in_recovery()")[0][0]
        return self._cache['recovery']['storage'][db]

    def is_bootstraped(self, db=None):
        if db in self._cache['bootstrap']['storage']:
            if self._cache['bootstrap']['counter'] < self._cache['bootstrap']['cache']:
                self._cache['bootstrap']['counter'] += 1
                return self._cache['bootstrap']['storage'][db]
        self._cache['bootstrap']['counter'] = 0
        sql = """select count(*) from pg_catalog.pg_class
            where relname = 'mamonsu_config'"""
        result = int(self.query(sql, db)[0][0])
        self._cache['bootstrap']['storage'][db] = (result == 1)
        if self._cache['bootstrap']['storage'][db]:
            self.all_connections[db].log.info('Found mamonsu bootstrap')
        else:
            self.all_connections[db].log.info('Can\'t found mamonsu bootstrap')
            self.all_connections[db].log.info('hint: run `mamonsu bootstrap` if you want to run without superuser rights')
        return self._cache['bootstrap']['storage'][db]

    def is_pgpro(self, db=None):
        if db in self._cache['pgpro']:
            return self._cache['pgpro'][db]
        try:
            self.query('select pgpro_version()')
            self._cache['pgpro'][db] = True
        except:
            self._cache['pgpro'][db] = False
        return self._cache['pgpro'][db]

    def is_pgpro_ee(self, db=None):
        if not self.is_pgpro(db):
            return False
        if db in self._cache['pgproee']:
            return self._cache['pgproee'][db]
        self._cache['pgproee'][db] = (
            self.query('select pgpro_edition()')[0][0].lower() == 'enterprise'
        )
        return self._cache['pgproee'][db]

    def extension_installed(self, ext, db=None):
        result = self.query('select count(*) from pg_catalog.pg_extension\
            where extname = \'{0}\''.format(ext), db)
        return (int(result[0][0])) == 1

    def databases(self):
        result, databases = self.query('select datname from \
            pg_catalog.pg_database'), []
        for row in result:
            if row[0] not in self.ExcludeDBs:
                databases.append(row[0])
        return databases

    def get_sql(self, typ, db=None):
        if typ not in self.SQL:
            raise LookupError("Unknown SQL type: '{0}'".format(typ))
        result = self.SQL[typ]
        if self.is_bootstraped(db):
            return result[1]
        else:
            return result[0]

    def run_sql_type(self, typ, db=None):
        return self.query(self.get_sql(typ, db), db)

    def _init_connection(self, db):
        if db not in self.all_connections:
            # create new connection
            info = self.info
            info['db'] = db
            self.all_connections[db] = Connection(info)
