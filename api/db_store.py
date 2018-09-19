from cassandra import ConsistencyLevel
from cassandra.query import BatchStatement
from cassandra.query import SimpleStatement


class DbStore:

    def __init__(self, session, config):
        self.session = session
        self.config = config

    async def get_long_url(self, short_url):
        query = """
            SELECT long_url FROM short_long WHERE short_url = '%s' LIMIT 1
        """ % short_url

        # We explicitly do not set a consistency level for high availability
        rows = await self.session.execute_future(SimpleStatement(query))

        return rows

    async def get_short_url(self, long_url):
        query = """
            SELECT short_url FROM long_short WHERE long_url = '%s' LIMIT 1
        """ % long_url

        # We explicitly do not set a consistency level for high availability
        rows = await self.session.execute_future(SimpleStatement(query))

        return rows

    async def batch_update(self, short_url, long_url):
        # A protocol-level batch of operations which are applied atomically
        # By default the batch type is BatchType.LOGGED
        batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
        # Consitency level QUORUM -> (SUM_OF_ALL_REPLICAS / 2 + 1) rounded down

        # Insert data into both tables for easy lookup
        sl_query = self.session.prepare("""
            INSERT INTO short_long (short_url, long_url) VALUES (?, ?)
        """)
        batch.add(sl_query, (short_url, long_url))

        ls_query = self.session.prepare("""
            INSERT INTO long_short (long_url, short_url) VALUES (?, ?)
        """)
        batch.add(ls_query, (long_url, short_url))

        # Execute atomic batch operation asynchronously
        await self.session.execute_future(batch)

    async def get_increment(self):
        machine_id = self.config["counter"]["machines"][0]

        # Update increment value in distributed counter
        # ConsistencyLevel.ALL provides the highest consistency and the lowest availability
        update_query = """
            UPDATE distributed_counter SET increment = increment + 1 WHERE machine_id = '%s'
        """ % machine_id
        await self.session.execute_future(
            SimpleStatement(update_query, consistency_level=ConsistencyLevel.ALL))

        # Select new increment value from distributed counter
        select_query = """
            SELECT increment FROM distributed_counter WHERE machine_id = '%s' LIMIT 1
        """ % machine_id
        rows = await self.session.execute_future(
            SimpleStatement(select_query, consistency_level=ConsistencyLevel.ALL))

        return -1 if not rows else rows[0].increment
