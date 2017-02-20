Personal finance and investment portal.

# The Web Application

[Live demo](http://murphytalk.vicp.net/finance_demo/) with randomly generated instruments and positions.

## DB schema

The DB backend is SQLite. This [SQL script](src/finance/common/db.sql) defines all DB objects and is also being used by the [Live demo](http://murphytalk.vicp.net/finance_demo/) to populate random data in a in-momory DB.

## Configuration

Configurations are defined as uppercase variables in [module finance](src/finance/__init__.py).

 1. `DATABASE` the full path to the sqlite3 db file. It would try environment variable `FINANCE_DB` first, if that does not exist then use the value defined there. The final value will be tested as a valid file path, if successful a `Dao` object is created to load data from it, otherwise a `FakeDao` object will be created to generate random static and market data.
 2. `DEBUG` False if is being deployed on production server.

## RESTful API

RESTful APIs are available for query and manipulate the data. Thanks for [Swagger UI](http://swagger.io/swagger-ui/) there is visual and interactive documentation. It works so intuitively, I just left all CRUD tasks to the API doc page instead of building UI for them.  See the [API live demo](http://murphytalk.vicp.net/finance_demo/api/).


# The Common Python Scripts

In `common` folder, most of them can be launched individually, they accept the following common parameters:

 1. `-f/full/path/to/sqlite/file` Path to the DB file.
 1. `-sYYYYMMDD` start date, default is 2014-01-01
 1. `-eYYYYMMDD` end date, default is 

I have a private project [finance_scraper](https://gitlab.com/murphytalk/finance_scraper) (private repository) that scrapes market data from public sites (yahoo financial etc.), transactions and performance from my brokers' web pages. That project depdends on some of the common scripts here. The scraper uses the RESTful API to submit data. 

# Deployment

## Use Nginx as proxy

The idea is to run nginx at the front, and dispatch all requests to URL under `/finance` to the standalone Finance application,  ngnix needs to be [configured](conf/nginx.conf) to do this . More details can be found on [ngnix wiki](https://www.nginx.com/resources/wiki/start/topics/examples/javaservers/).

ngnix's authentication is used to strict the access to URL `/finance`. The access from outside to the Finance application can be blocked too: 

```bash
sudo iptables -A INPUT -p tcp -i venet0 --dport 8080 -j REJECT --reject-with tcp-reset
```

