from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement


async def get_increment(session, config):
    # Update increment value in distributed counter
    # ConsistencyLevel.ALL provides the highest consistency and the lowest availability
    update_query = """
        UPDATE distributed_counter SET increment = increment + 1 WHERE machine_id = '%s'
    """ % config["counter"]["machines"][0]
    await session.execute_future(
        SimpleStatement(update_query, consistency_level=ConsistencyLevel.ALL))

    # Select new increment value from distributed counter
    select_query = """
        SELECT increment FROM distributed_counter WHERE machine_id = '%s' LIMIT 1
    """ % config["counter"]["machines"][0]
    rows = await session.execute_future(
        SimpleStatement(select_query, consistency_level=ConsistencyLevel.ALL))

    return -1 if not rows else rows[0].increment
