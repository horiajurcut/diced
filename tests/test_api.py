async def test_index_endpoint(client):
    resp = await client.get('/')
    
    assert resp.status == 200
