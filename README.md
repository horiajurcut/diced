# dice.it
The Fancy URL Shortener

## Proposed Solution

Creating a scalable **URL Shortener** is not a trivial task. More so if the expectation is to scale it beyond one machine. The ***storage layer*** is a crucial component. If we try using a classic **RDBMS** (eg. Postgres, MySQL) we immediately run into the problem of `write performance`. These systems use a single master database where information is written (one of the requirements is *high availability*).

***NOTE:*** Worth mentioning that **2ndQuadrant** is making progress in offering multi-master replication solutions (see [Postgres-BDR](https://www.2ndquadrant.com/en/resources/postgres-bdr-2ndquadrant/) for details).

For now, we assume ***NoSQL*** is a better fit. First challenge is to find a good way to convert a long URL into a short code. We want to keep the size of the code small (*maximum of 6-7 characters*). Let's examine a few options:
- We can use a hashing algorithm to hash the long URL (eg. `md5`, `murmurHash`) - hash algorithms usually produce a longer string. If we use a substring of the resulting hash (eg. the first 6 characters of ***2fc492****c6b0e12f721bece9099baa6070*) we will have to deal with too many collisions (different long URLs have the same code).
- Every distinct long URL gets a unique ID, an `autoincrement` value - we encode that value in **base62** (assuming the alphabet is **[A-Za-z0-9]**). If we stop for a second to look at the problem domain, if we use 6 character codes only, we have **62<sup>6</sup>** possible values (~ **56 billion**). To put things in perspective, if we have 100 distinct URLs every second, we could keep the service up and running for **18 years**.

***Cassandra*** doesn't really provide us with a good way to create an `AUTOINCREMENT PRIMARY KEY` (to be expected, since we are dealing with an eventually consistent database system). What we need is a global distributed counter that generates a new increment every time a distinct URL appears. For simplicity's sake, we can implement the counter in Cassandra by taking advantage of the **Consistency Levels** (dropping high availability in favour of consistency as much as we can afford it). For other ideas on implementing a global distributed counter check the **Possible Improvements** section below.

To be able to do fast look-ups (check if the short or long URL exists in the database) one method is to keep to separate tables with the columns in reversed order (see [db_setup.py](db_setup.py) for details). The trick is to play with the ***Consistency Levels*** deciding the ratio between **high availability** and **high consistency** (read more [here](https://docs.datastax.com/en/cql/3.3/cql/cql_reference/cqlshConsistency.html) and look at the implementation in [/api/db_store.py](/api/db_store.py)).

***NOTE:*** When picking ***high availability*** over ***high consistency*** some of the same long URLs could have different codes. The benefit is that we can scale the entire system beyond one machine.

## Set-up

This project uses `docker-compose` to set-up a development environment. The `docker-compose.yaml` file defines two services:
- **cassandra** - NoSQL database used to store the mapping between short and long URLs 
- **web** - python3 asynchronous REST API used to create and lookup URLs

To start ***dice.it***, simply run `docker-compose up --build -d` and start brewing a cup of coffee (it might take a few minutes to install everything).

The build process goes through three different stages (see [setup.sh](setup.sh) for details):

1. Wait for the Cassandra cluster to be up and running
2. Runs the unit and integration tests as part of the build (see [/tests](/tests) for details) - ***the tests are currently running against the same Cassandra cluster for simplicity's sake***
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

To create a global distributed counter we could use ***Apache Zookeper*** to maintain a server which enables highly reliable distributed coordination. This way we could have a set of machines each responsible for generating the next increment in a given range (eg. ***Machine M1*** counts the values between *1 and 1 million*, ***Machine M2*** counts the values between *1 million and 2 million* and so on).
