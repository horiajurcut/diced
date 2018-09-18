import logging

log = logging.getLogger()
log.setLevel("DEBUG")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.query import SimpleStatement

KEYSPACE = "diced"


def main():
    cluster = Cluster(
        ["cassandra"],
        load_balancing_policy=DCAwareRoundRobinPolicy(),
        port=9042)
    session = cluster.connect()

    # Check if KEYSPACE already exists and DROP it
    rows = session.execute("SELECT keyspace_name FROM system_schema.keyspaces")
    if KEYSPACE in [row[0] for row in rows]:
        log.info("Dropping existing keyspace...")
        session.execute("DROP KEYSPACE " + KEYSPACE)

    # Recreate KEYSPACE
    log.info("Creating keyspace...")
    session.execute("""
        CREATE KEYSPACE %s
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
    """ % KEYSPACE)

    log.info("Setting keyspace...")
    session.set_keyspace(KEYSPACE)

    # Create 'short_long' table
    session.execute("""
        CREATE TABLE short_long (
            short_url text,
            long_url text,
            PRIMARY KEY (short_url)
        )
    """)

    # Create 'long_short' table
    session.execute("""
        CREATE TABLE long_short (
            long_url text,
            short_url text,
            PRIMARY KEY (long_url)
        )
    """)

    # Create mock counter - placeholder for distributed counter
    session.execute("""
        CREATE TABLE distributed_counter (
            machine_id text PRIMARY KEY,
            increment counter
        )
    """)

    # Close connection to cluster
    log.info("Shutting down cluster...")
    cluster.shutdown()


if __name__ == "__main__":
    main()
