# AFSC GAP Viz
Visual analytics web application for AFSC GAP data that can be used without writing code. It uses the `afscgap` library underneath and enables users to continue in code or through a spreadsheet export.

<br>
<br>

## Quickstart
No install required! The application is hosted for the public at [https://app.pyafscgap.org](https://app.pyafscgap.org) but may be run locally as described below as well.

<br>
<br>

## Installation
This application can be self-hosted or run locally. Due to the high disk usage required for this tool to operate efficiently (about 1GB local disk storage), it is not installed by default when running `pip install afscgap`. To install:

```
$ git clone https://github.com/SchmidtDSE/afscgap.git
$ cd afscgap/afscgapviz
$ pip install -r requirements.txt
$ bash load_deps.sh
```

Note that this application still requires a dataset as described below. For ease of development, webpack is not required.

<br>
<br>

## Usage
This application is a [Flask](https://flask.palletsprojects.com/) application that requires access to a database in order to work correctly.

<br>

#### Creating a sqlite database
The default usage leverages a sqlite database which is read only when used by the application. A pre-built database can be downloaded into the `afscgap/afscgapviz` directory like so:

```
$ cd afscgap/afscgapviz
$ wget https://pyafscgap.org/community/geohashes.zip
$ unzip geohashes.zip
$ rm goehashes.zip
```

If you want to build the dataset yourself, run the `build_database` script like so:

```
$ cd afscgap/afscgapviz
$ bash build_database.sh
```

<br>

#### Starting the application
Once the database is in place, one can start the web application with `python afscgapviz.py`. If you need to create a Flask app manually, it can be done like so:

```
import flask

import afscgapviz

app = flask.Flask(__name__)

afscgapviz.build_app(app)
```

This may be useful when running outside a development server.

<br>

#### Using a non-sqlite database
Any [DB API 2.0](https://peps.python.org/pep-0249/) compliant database library may be used. For example, [pg8000](https://github.com/tlocke/pg8000) can be used to leverage Postgres instead of sqlite like so:

```
import contextlib
import threading

import flask
import pg8000

import afscgapviz

pg8000.dbapi.paramstyle = 'qmark'

app = flask.Flask(__name__)


def get_connection_no_cache():
    return pg8000.dbapi.connect()


def build_get_connection():
    lock = threading.Lock()
    cache = {'cache': None}

    def get_connection():
        connection = cache['cache']

        # Test connection
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                cursor.close()
            except:
                connection = None

        # Make connection if needed
        if connection is None:
            connection = get_connection_no_cache()

        # Save for next time
        cache['cache'] = connection

        return connection

    @contextlib.contextmanager
    def get_connection_wrapped():
        lock.acquire()
        try:
            yield get_connection()
        finally:
            lock.release()

    return get_connection_wrapped


afscgapviz.build_app(
    app,
    conn_generator_builder=build_get_connection
)
```

Note that the development of the tool is focused on sqlite. Pull requests are welcome for fixes for other backends but changes to SQL must be compatible with sqlite.

<br>
<br>

## Data quality
Invalid data are excluded and only data with area swept in hectares, catch (count and weight in kg), and temperatures (both bottom and surface) are retained. No effort is made to try to "fix" records with incorrect data. Information is used as provided by the AFSC GAP API service.

<br>
<br>

## License
Like the rest of the the project, we are happy to make this library available under the BSD 3-Clause license. See LICENSE for more details. (c) 2023 Regents of University of California. See the [Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley](https://dse.berkeley.edu).

<br>
<br>

## Local development
After installing dev dependencies (`pip install -r requirements.txt`), we recommend the following local checks:

```
$ nose2
$ mypy *.py
$ pyflakes *.py
$ pycodestyle *.py
```

Note these checks are run by CI / CD. Furthermore, JS tests can be run via grunt from the root directory or by:

```
$ python -m http.server
```

Then, direct your browser to [http://0.0.0.0:8000/static/test/test.html](http://0.0.0.0:8000/static/test/test.html).

<br>
<br>

## Contributing
We invite contributions via [our project Github](https://github.com/SchmidtDSE/afscgap). Please read the [CONTRIBUTING.md](https://github.com/SchmidtDSE/afscgap/blob/main/CONTRIBUTING.md) file for more information.

<br>
<br>

## Open source
In addition to using the `afscgap` library elsewhere in this repository, the following open source tools are used:

 - [D3.js](https://d3js.org/) under the [ISC License](https://github.com/d3/d3/blob/main/LICENSE) from Mike Bostock.
 - [Flask](https://flask.palletsprojects.com/en/2.2.x/) under the [BSD License](https://github.com/pallets/flask/blob/main/LICENSE.rst) from Pallets.
 - [Geolib](https://github.com/joyanujoy/geolib) under the [MIT License](https://github.com/joyanujoy/geolib/blob/master/LICENSE) from Anu Joy.
 - [Papa Parse](https://www.papaparse.com/) under the [MIT License](https://github.com/mholt/PapaParse/blob/master/LICENSE) from Matthew Holt.
 - [Toolz](https://github.com/pytoolz/toolz/) under the [BSD License](https://github.com/pytoolz/toolz/blob/master/LICENSE.txt) from Matthew Rocklin.

In CI / CD, this project also uses [QUnit](https://qunitjs.com/) under the [MIT License](https://github.com/qunitjs/qunit/blob/main/LICENSE.txt) from OpenJS Foundation and other contributors as well as [Grunt](https://gruntjs.com/) under an [MIT-like License](https://github.com/gruntjs/grunt/blob/main/LICENSE) from jQuery Foundation and other contributors.

Thank you to all of these projects for their contribution. Note that CDNs are not used for privacy reasons.

<br>
<br>

## Citations
The following are citations specifically for the visual analytics tool not covered in the open source section:

 - "AFSC Groundfish and Crab Assessment Program Bottom Trawl Surveys." AFSC Gap Survey, NOAA Fisheries, https://www.fisheries.noaa.gov/foss/f?p=215%3A28. 
 - Brewer, Cynthia, and Mark Harrower. "Colorbrewer 2.0." ColorBrewer, The Pennsylvania State University, 3 May 2021, https://colorbrewer2.org/#type=sequential&amp;scheme=BuGn&amp;n=3. 
 - Brown, Mark. "Super Mario 3D World's 4 Step Level Design." Game Maker's Toolkit, YouTube, 16 Mar. 2015, https://www.youtube.com/watch?v=dBmIkEvEBtA.
 - George, Kavitha. "Alaska Cod Fishery Closes and Industry Braces for Ripple Effect." NPR, NPR, 8 Dec. 2019, https://www.npr.org/2019/12/08/785634169/alaska-cod-fishery-closes-and-industry-braces-for-ripple-effect. 
 - Laurel, Benjamin J., and Lauren A. Rogers. "Loss of Spawning Habitat and Prerecruits of Pacific Cod during a Gulf of Alaska Heatwave." Canadian Journal of Fisheries and Aquatic Sciences, vol. 77, no. 4, 23 Jan. 2020, pp. 644–650., https://doi.org/10.1139/cjfas-2019-0238. 
 - Nutt, Christian. "The Structure of Fun: Learning from Super Mario 3D Land's Director." Game Developer, Informa PLC Informa UK, 13 Apr. 2012, https://www.gamedeveloper.com/design/the-structure-of-fun-learning-from-i-super-mario-3d-land-i-s-director.
 - Yang, Qiong, et al. "How 'The Blob' Affected Groundfish Distributions in the Gulf of Alaska." Fisheries Oceanography, 6 Feb. 2019, https://doi.org/10.1111/fog.12422. 
