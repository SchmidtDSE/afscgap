# AFSC GAP for Python
Microlibrary for pythonic interaction with the public bottom trawl surveys data from the [NOAA AFSC GAP](https://www.fisheries.noaa.gov/contact/groundfish-assessment-program).

<br>

## Purpose
Unofficial microlibrary for interacting with the API for [bottom trawl surveys](https://www.fisheries.noaa.gov/alaska/commercial-fishing/alaska-groundfish-bottom-trawl-survey-data) from the [Ground Fish Assessment Program (GAP)](https://www.fisheries.noaa.gov/contact/groundfish-assessment-program), a dataset produced by the [Resource Assessment and Conservation Engineering (RACE) Division](https://www.fisheries.noaa.gov/about/resource-assessment-and-conservation-engineering-division) of the [Alaska Fisheries Science Center (AFSC)](https://www.fisheries.noaa.gov/about/alaska-fisheries-science-center) as part of the National Oceanic and Atmospheric Administration ([NOAA Fisheries](https://www.fisheries.noaa.gov/)).

This low-dependency library provides a Python interface to these data with ability to query with filters and pagination, providing results in various formats compatible with different Python usage modalities (Pandas, pure-Python, etc). It adapts the [Oracle REST Data Service](https://www.oracle.com/database/technologies/appdev/rest.html) used by the agency with Python type hints for easy query and interface.

Though not intended to be general, this project also provides an example for working with [Oracle REST Data Services (ORDS)](https://www.oracle.com/database/technologies/appdev/rest.html) APIs in Python.

<br>

## Installation
This open source library is available for install via Pypi / Pip:

```
$ pip install afscgap
```

Note that its only dependency is [requests](https://docs.python-requests.org/en/latest/index.html) and Pandas / numpy are not expected.

<br>

## Usage
This library provides access to the public API endpoints with query keywords matching the column names described in the official [metadata repository](https://github.com/afsc-gap-products/metadata). Records are parsed into plain old Python objects with optional access to a dictionary representation.

### Basic Usage
For example, this requests all records in 2021 from the Gulf of Alaska:

```
import afscgap

result = afscgap.query(year=2021, srvy='BSS')
```

Using an iterator will have the library negotiate pagination behind the scenes:

```
count_by_common_name = {}

for record in result:
    common_name = record.get_common_name()
    count = count_by_common_name.get(common_name, 0) + 1
    count_by_common_name[common_name] = count
```

Note that this operation will cause multiple HTTP requests while the iterator runs.

### Pagination
By default, the library will iterate through all results and handle pagination behind the scenes. However, one can also request an individual page:

```
results_for_page = result.get_page(offset=100, limit=123)
print(len(results_for_page))  # Will print 123
```

Client code can also change the pagination behavior used when iterating:

```
results = afscgap.query(year=2021, srvy='BSS', offset=100, limit_per_page=200)

for record in results:
    print(record.get_common_name())
```

Note that records are only requested once per page after the prior page has been returned via the iterator ("lazy" loading).

### Serialization
Users may request a dictionary representation:

```
# Get dictionary from individual record
for record in result:
    common_name = record.to_dict()

# Get dictionary for all records
results_dicts = result.to_dicts()
print(results_dicts[0]['common_name'])
```

This returns an iterator by default but it can be realized as a full list using the `list()` command.

### Pandas
The dictionary form of the data can be used to create a Pandas dataframe:

```
import pandas

pandas.DataFrame(results.to_dicts())
```

Note that Pandas is not required to use this library.

### Advanced Filtering
Finally, users may provide advanced queries using Oracle's REST API query parameters. For example, this queries for 2021 records with haul from the Gulf of Alaska roughly near [geohash](https://en.wikipedia.org/wiki/Geohash) bf1s7:

```
import afscgap.query

results = afscgap.query(
    year=2021,
    latitude_dd={'$gte': 56.99, '$lte': 57.04},
    longitude_dd={'$gte': -143.96, '$lte': -144.01}
)
```

For more info about the options available, consider a helpful unaffiliated [getting started tutorial from Jeff Smith](https://www.thatjeffsmith.com/archive/2019/09/some-query-filtering-examples-in-ords/).

### Debugging
For investigating issues or evaluating the underlying operations, you can also request a full URL for a query:

```
result = afscgap.query(
    year=2021,
    latitude_dd={'$gt': 56.99, '$lt': 57.04},
    longitude_dd={'$gt': -143.96, '$lt': -144.01}
)

# Will print something like https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey/?q={"year":2021,"latitude_dd":{"$gt":56.99,"$lt": 57.04},"longitude_dd":{"$gt":-143.96,"$lt":-144.01}}&limit=10&offset=0
print(result.get_page_url(limit=10, offset=0))
```

The query can be executed by making an HTTP GET request at the provided location.

<br>

## Schema
A Python-typed description of the fields is provided from `afscgap.model.Record`:

| **Field**             | **Python Type** | **Description* |
|-----------------------|-----------------|----------------|
| year                  | float           | Year for the survey in which this observation was made. |
| srvy                  | str             | The name of the survey in which this observation was made. NBS (N Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea Slope), or GOA (Gulf of Alaska) |
| survey                | str             | Long form description of the survey in which the observation was made. |
| survey_id             | float           | Unique numeric ID for the survey. |
| cruise                | float           | An ID uniquely identifying the cruise in which the observation was made. Multiple cruises in a survey. |
| haul                  | float           | An ID uniquely identifying the haul in which this observation was made. Multiple hauls per cruises. |
| stratum               | float           | Unique ID for statistical area / survey combination as described in the metadata or 0 if an experimental tow. |
| station               | str             | Station associated with the survey. |
| vessel_name           | str             | Unique ID describing the vessel that made this observation. This is left as a string but, in practice, is likely numeric. |
| vessel_id             | float           | Name of the vessel at the time the observation was made with multiple names potentially associated with a vessel ID. |
| date_time             | str             | The date and time of the haul which has been attempted to be transformed to an ISO 8601 string without timezone info. If it couldn’t be transformed, the original string is reported. |
| latitude_dd           | float           | Latitude in decimal degrees associated with the haul. |
| longitude_dd          | float           | Longitude in decimal degrees associated with the haul. |
| species_code          | float           | Unique ID associated with the species observed. |
| common_name           | str             | The “common name” associated with the species observed. Example: Pacific glass shrimp  |
| scientific_name       | str             | The “scientific name” associated with the species observed. Example: Pasiphaea pacifica  |
| taxon_confidence      | str             | Confidence flag regarding ability to identify species (High, Moderate, Low). In practice, this can also be Unassessed. |
| cpue_kgha             | Optional[float] | Catch weight divided by net area (kg / hectares) if available. See metadata. None if could not interpret as a float. |
| cpue_kgkm2            | Optional[float] | Catch weight divided by net area (kg / km^2) if available. See metadata. None if could not interpret as a float. |
| cpue_kg1000km2        | Optional[float] | Catch weight divided by net area (kg / km^2 * 1000) if available. See metadata. None if could not interpret as a float. |
| cpue_noha             | Optional[float] | Catch number divided by net sweep area if available (count / hectares). See metadata. None if could not interpret as a float. |
| cpue_nokm2            | Optional[float] | Catch number divided by net sweep area if available (count / km^2). See metadata. None if could not interpret as a float. |
| cpue_no1000km2        | Optional[float] | Catch number divided by net sweep area if available (count / km^2 * 1000). See metadata. None if could not interpret as a float. |
| weight_kg             | Optional[float] | Taxon weight (kg) if available. See metadata. None if could not interpret as a float. |
| count                 | Optional[float] | Total number of organism individuals in haul. None if could not interpret as a float. |
| bottom_temperature_c  | Optional[float] | Bottom temperature associated with observation if available in Celsius. None if not given or could not interpret as a float. |
| surface_temperature_c | Optional[float] | Surface temperature associated with observation if available in Celsius. None if not given or could not interpret as a float. |
| depth_m               | float           | Depth of the bottom in meters. |
| distance_fished_km    | float           | Distance of the net fished as km. |
| net_width_m           | float           | Distance of the net fished as m. |
| net_height_m          | float           | Height of the net fished as m. |
| area_swept_ha         | float           | Area covered by the net while fishing in hectares. |
| duration_hr           | float           | Duration of the haul as number of hours. |
| tsn                   | int             | Taxonomic information system species code. |
| ak_survey_id          | int             | AK identifier for the survey. |

For more information on the schema, see the [metadata](https://github.com/afsc-gap-products/metadata) repository but note that the fields may be slightly different in the Python library per what is actually returned by the API.

<br>

## License
We are happy to make this library available under the LGPL v3 License (LGPL-3.0-or-later). See LICENSE for more details. (c) 2023 [The Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley](https://dse.berkeley.edu).

<br>

## Developing
Thanks for your support! Pull requests and issues very welcome. We have a few guidelines:

 - Please follow the Google Python Style Guide where possible for compatibility with the existing codebase.
 - Tests are encouraged and we aim for 80% coverage where feasible.
 - Type hints are encouraged and we aim for 80% coverage where feasible.
 - Docstrings are encouraged and we aim for 80% coverage.
 - Please check that you have no mypy errors when contributing.

Note that imports should be in alphabetical order in groups of standard library, third-party, and then first party. It is an explicit goal to provide a class with type hints for all record fields. Getters on an immutable record object are encouraged as to enable use of the type system and docstrings for understanding the data structures. Data structures have been used that could allow for threaded request but everything is currently single threaded.

<br>

## Open Source
We are happy to be part of the open source community. At this time, the only open source dependency used by this microlibrary is [Requests](https://docs.python-requests.org/en/latest/index.html) which is available under the [Apache v2 License](https://github.com/psf/requests/blob/main/LICENSE) from its [Kenneth Reitz and other contributors](https://github.com/psf/requests/graphs/contributors).
