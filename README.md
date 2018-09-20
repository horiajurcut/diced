# dice.it
The Fancy URL Shortener

## Proposed Solution

Creating a scalable **URL Shortener** is not a trivial task. More so if the expectation is to scale it beyond one machine. The ***storage layer*** is a crucial component. If we try using a classic **RDBMS** (eg. Postgres, MySQL) we immediately run into the problem of `write performance`. These systems use a single master database where information is written (one of the requirements is *high availability*).

***NOTE:*** Worth mentioning that **2ndQuadrant** is making progress in offering multi-master replication solutions (see [Postgres-BDR](https://www.2ndquadrant.com/en/resources/postgres-bdr-2ndquadrant/) for details).

For now, we assume ***NoSQL*** is a better fit. First challenge is to find a good way to convert a long URL into a short code. We want to keep the size of the code small (*maximum of 6-7 characters*). Let's examine a few options:
- We can use a hashing algorithm to hash the long URL (eg. `md5`, `murmurHash`) - hash algorithms usually produce a longer string. If we use a substring of the resulting hash (eg. the first 6 characters of ***2fc492****c6b0e12f721bece9099baa6070*) we will have to deal with too many collisions (different long URLs have the same code).
- Every distinct long URL gets a unique ID, an `autoincrement` value - we encode that value in **base62** (assuming the alphabet is [A-Za-z0-9]). If we stop for a second to look at the problem domain, if we use 6 character codes only, we have 62<sup>6</sup> possible values (~ 56 billion). To put things in perspective, if we have 100 distinct URLs every second, we could keep the service up and running for 18 years.

## Set-up

This project uses `docker-compose` to set-up a development environment. The `docker-compose.yaml` file defines two services:
- **cassandra** - NoSQL database used to store the mapping between short and long URLs 
- **web** - python3 asynchronous REST API used to create and lookup URLs

To start ***dice.it***, simply run `docker-compose up --build -d` and start brewing a cup of coffee (it might take a few minutes to install everything).

The build process goes through three different stages (see [setup.sh](setup.sh) for details):

1. Wait for the Cassandra cluster to be up and running
2. Runs the unit and integration tests as part of the build (see [/tests](/tests) for details)
3. Runs the database setup script (see [db_setup.py](db_setup.py) for details) - this drops the `keyspace` every time, in production this would be replaced with a migration script

The last step is to run the API service - `python3 -m api`

## API Reference

### Create

To create a new short url you can use the following `curl` command:
```
curl -H "Content-Type: application/json" --request POST --data '{"url": "https://news.google.com/?hl=en-US&gl=US&ceid=US:en"}' http://localhost:8080/dice
```
***NOTE:*** If you are running `docker` on Windows together with `VirtualBox` you will need to use the ip of the machine the containers are running on. You can easily find it out by running `docker-machine ip`.

Expected response is:
```
{"short_url_code": "4", "short_url": "https://dice.it/4"}
```
We will use the `short_url_code` in combination with the following endpoint to redirect to the long URL. We could just repond with `short_url` if this was deployed on a specific domain (eg. `dice.it`)

### Lookup

To lookup and redirect to the long URL, simply go to your web browser to the following address:
```
http://localhost/<short_url_code>
```

If the `short_url_code` exists, the API will find the corresponding long URL and redirect to it.

## Possible Improvements
