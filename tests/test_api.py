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


async def test_dice_url_invalid(client):
    url_to_dice = {
        "url": "1"
    }
    response = await client.post('/dice', json=url_to_dice)

    assert response.status == 400
    assert (await response.text()) == "URL is not valid"


async def test_dice_existing_url(client):
    url_to_dice = {
        "url": "https://google.com"
    }
    response = await client.post('/dice', json=url_to_dice)
    data = await response.json()

    assert "short_url" in data and len(data["short_url"])
    existing_short_url = data["short_url"]

    response = await client.post('/dice', json=url_to_dice)
    data = await response.json()

    assert data["short_url"] == existing_short_url


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

    assert str(response.url) == long_url


async def test_redirect_url_not_found(client):
    # Short URL code is not in the database
    response = await client.get("/4-0-4")

    assert response.status == 400
    assert (await response.text()) == "Short URL was not found"
