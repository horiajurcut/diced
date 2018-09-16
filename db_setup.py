import logging

log = logging.getLogger()
log.setLevel('DEBUG')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
log.addHandler(handler)

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

KEYSPACE = "diced"


def main():
    cluster = Cluster(['10.7.108.10'])
    session = cluster.connect()

    log.info('Creating keyspace...')
    session.execute("""
        CREATE KEYSPACE %s
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
        """ % KEYSPACE)

    log.info('Setting keyspace...')
    session.set_keyspace(KEYSPACE)

    log.info('Shutting down cluster...')
    cluster.shutdown()


if __name__ == '__main__':
    main()
