async def test_index_endpoint(client):
    response = await client.get('/')

    # Assert index route is accessible
    assert response.status == 200


async def test_dice_url(client):
    url_to_dice = {
        "url": "https://google.com"
    }
    response = await client.post('/dice', json=url_to_dice)
    data = await response.json()

    assert "short_url" in data and len(data["short_url"])


async def test_redirect(client):
    # Long URL
    long_url = "https://www.facebook.com/"

    # First we need to shorten the URL
    url_to_dice = {
        "url": long_url
    }
    response = await client.post('/dice', json=url_to_dice)
    data = await response.json()

    assert "short_url" in data and len(data["short_url"])

    # Check if we correctly redirect to the long URL
    response = await client.get("/" + data["short_url"].replace("https://dice.it/", ""))

    assert str(response.url) is long_url
