Personal finance and investment portal.


# The Web Application

# The Python Scripts

Python scripts are used to scrape broker's web site to download performance data.

Common parameters:

 1. `-f/full/path/to/sqlite/file` Path to the DB file.
 1. `-sYYYYMMDD` start date, default is 2014-01-01
 1. `-eYYYYMMDD` end date, default is 

Scripts:

 1. [scraper.py](src/main/python/scraper.py) does the actual scraping. It reads login credentials from an encrypted ini file, the path to the file defined in [config.py](src/main/python/config.py). It can be launched alone, with multiple parameters (broker's type) nor no parameter (all brokers),  by default it outputs results to standard output, but if command line argument `-f/full/path/to/sqlite/file` is specified, the data will be written into the specified DB.
 1. [financial_data.py](src/main/python/financial_data.py) is used to download public available financial data, including currency exchange rate and stock quotes. Apart from the `-f` argument, `-sYYYYMMDD` and `-eYYYYMMDD` can also be used to specify the start date and the end date respectively, current date will be used if it is omitted. Other supported argments are `Xccy`(to download currency exchange rate) or any valid stock symbol(on Yahoo finance). If none of these arguments are specified, it will download exchange rate and all stocks found in transaction table.  
 1. [adapter.py](src/main/python/adapter.py) defines adapters to be used to output results.


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
significantly. Note this won't happen if the `productionMode` is set to `true`, if you get error like _Request for /VAADIN/themes/mytheme/styles.css not handled by sass compiler while in production mode_, run `mvn vaadin:compile-theme`. 

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


