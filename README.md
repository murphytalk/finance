Personal finance and investment portal.

# The Web Application

## Configuration

Configurations are defined as uppercase variables in [module fiance](src/web/finance/__init__.py).

 1. `DATABASE` the full path to the sqlite3 db file. It would try environment variable `FINANCE_DB` first, if that does not exist then use the value defined there. The final value will be tested as a valid file path, if succesful a `Dao` object is created to load data from it, otherwise a `FakeDao` object will be created to generate random static and market data.

# The Common Python Scripts

In `common` folder, most of them can be launched individually, they accept the following common parameters:

 1. `-f/full/path/to/sqlite/file` Path to the DB file.
 1. `-sYYYYMMDD` start date, default is 2014-01-01
 1. `-eYYYYMMDD` end date, default is 

Project [finance_scraper](https://bitbucket.org/murphytalk/finance_scraper) (private repository hosted on butbucket.com) depdends on some of the common scripts here.

# Deployment

## Use Nginx as proxy

The idea is to run nginx at the front, and dispatch relative traffic to the Java application server,  ngnix needs to be [configured](conf/nginx.conf) to do this . More details can be found on [ngnix wiki](https://www.nginx.com/resources/wiki/start/topics/examples/javaservers/).

Then the access from outside to the Java Application server can be blocked: 

```bash
sudo iptables -A INPUT -p tcp -i venet0 --dport 8080 -j REJECT --reject-with tcp-reset
```

