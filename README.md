Personal finance and investment portal.


# The Web Application

# The Python Scripts

Python scripts are used to scrape broker's web site to download performance data.

 1. [scraper.py](src/main/python/scraper.py) does the actual scraping. It reads login credentials from a ini file, which is defined in [config.py](src/main/python/config.py). It can be launched along, with multiple parameters (broker's name) nor no parameter (all brokers),  it outputs results to standard output. 
 1. [adapter.py](src/main/python/adapter.py) defines adapters to be used to output results.
 1. [scrap_to_db.py](src/main/python/scrap_to_db.py) is the one to be scheduled to run daily. It outputs result to a sqlite database. It takes whatever parameters [scraper.py](src/main/python/scraper.py) can handle, plus one more : `-f/full/path/to/sqlite/file`.


# Local Development Workflow


To compile the entire project, run `mvn install`.
To run the application, run `mvn jetty:run` and open [http://localhost:8080/](http://localhost:8080/) .

To develop the theme, simply update the relevant theme files and reload the application.
Pre-compiling a theme eliminates automatic theme updates at runtime - see below for more information.

Debugging client side code
  - run `mvn vaadin:run-codeserver` on a separate console while the application is running
  - activate Super Dev Mode in the debug window of the application

To produce a deployable production mode WAR:
- change productionMode to true in the servlet class configuration (nested in the UI class)
- run `mvn clean vaadin:compile-theme package`
  - See below for more information. Running `mvn clean` removes the pre-compiled theme.
- test with "mvn jetty:run-war

## Using a precompiled theme


When developing the application, Vaadin can compile the theme on the fly when needed,
or the theme can be precompiled to speed up page loads.

To precompile the theme run `mvn vaadin:compile-theme`. Note, though, that once
the theme has been precompiled, any theme changes will not be visible until the
next theme compilation or running the `mvn clean` target.

When developing the theme, running the application in the "run" mode (rather than
in "debug") in the IDE can speed up consecutive on-the-fly theme compilations
significantly.

# Deployment

## Deploy to Java application server  ([Jetty](http://www.eclipse.org/jetty/documentation/current/quickstart-running-jetty.html))

Create a Jetty base folder (assign the full path to environment variable `$JETTY_BASE`), run the following command to create a base directory structure:

```bash
java -jar $JETTY_HOME/start.jar --add-to-startd=http,deploy,jsp

```

Then copy the WAR file to  `webapps` folder as `ROOT.war`.

This application needs a Java property `property.dir` to be defined, which points to the folder where [finance.properties](conf/finance.properties) is being deployed.  To let Jetty picks up the java property definition, define the following environment variable :

```bash
export JAVA_OPTIONS=-Dproperty.dir=/folder/to/finance.properties
```

# Use Nginx as proxy

The idea is to run nginx at the front, and dispatch relative traffic to the Java application server,  ngnix needs to be [configured](conf/nginx.conf) to do this . More details can be found on [ngnix wiki](https://www.nginx.com/resources/wiki/start/topics/examples/javaservers/).

Then the access from outside to the Java Application server can be blocked: 

```bash
sudo iptables -A INPUT -p tcp -i venet0 --dport 8080 -j REJECT --reject-with tcp-reset
```


