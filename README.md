# AFSC GAP for Python
Python tool chain for working with the public bottom trawl surveys data from the [NOAA AFSC GAP](https://www.fisheries.noaa.gov/contact/groundfish-assessment-program).

| Group | Badges |
|-------|--------|
| Status | ![build workflow status](https://github.com/SchmidtDSE/afscgap/actions/workflows/build.yml/badge.svg?branch=main) ![docs workflow status](https://github.com/SchmidtDSE/afscgap/actions/workflows/docs.yml/badge.svg?branch=main) [![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) |
| Usage | [![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Pypi Badge](https://img.shields.io/pypi/v/afscgap)](https://pypi.org/project/afscgap/) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) |
| Publication | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb) |

See [webpage](https://pyafscgap.org), [project Github](https://github.com/SchmidtDSE/afscgap), and [example notebook](https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb).

<br>
<br>

## Installation
This open source library is available for install via Pypi / Pip:

```
$ pip install afscgap
```

Note that its only dependency is [requests](https://docs.python-requests.org/en/latest/index.html) and [Pandas / numpy are not expected but supported](#pandas).

<br>
<br>

## Purpose
Unofficial Python tool set for interacting with [bottom trawl surveys](https://www.fisheries.noaa.gov/alaska/commercial-fishing/alaska-groundfish-bottom-trawl-survey-data) from the [Ground Fish Assessment Program (GAP)](https://www.fisheries.noaa.gov/contact/groundfish-assessment-program). It offers:

 - Pythonic access to the official [NOAA AFSC GAP API service](https://www.fisheries.noaa.gov/foss/f?p=215%3A28).
 - Tools for inference of the "negative" observations not provided by the API service.

Note that GAP is a dataset produced by the [Resource Assessment and Conservation Engineering (RACE) Division](https://www.fisheries.noaa.gov/about/resource-assessment-and-conservation-engineering-division) of the [Alaska Fisheries Science Center (AFSC)](https://www.fisheries.noaa.gov/about/alaska-fisheries-science-center) as part of the National Oceanic and Atmospheric Administration's Fisheries organization ([NOAA Fisheries](https://www.fisheries.noaa.gov/)).

<br>

#### Needs
Scientists and developers working on ocean health have an interest in survey data from organizations like [NOAA Fisheries](https://www.fisheries.noaa.gov/). However,

 - Using the GAP API from NOAA AFSC in Python requires a lot of work: understanding a complex schema, determining how to interact with a proprietary REST data service, forming long query URLs, and navigating pagination. 
 - The official API service provides presence-only data, frustrating common types of analysis and aggregation.

These various elements together may increase the barrier for working with these data, limiting their reach within the Python community.

<br>

#### Goals
This low-dependency tool set provides the following:

 - **API access**: A type-annotated and documented Python interface to the official API service with ability to query with automated pagination, providing results in various formats compatible with different Python usage modalities (Pandas, pure-Python, etc). It adapts the HTTP-based API used by the agency with Python type hints for easy query and interface. 
 - **Contextual documentation**: Python docstrings annotate the data structures provided by the API to help users navigate the various fields available, offering contextual documentation when supported by Python IDEs.
 - **Absence inference**: Tools to infer absence or "zero catch" data as required for certain analysis and aggregation using a [supplemental hauls flat file dataset](https://pyafscgap.org/community/hauls.csv). Note that this flat file is provided by and hosted for this library's community after being created from [non-API public AFSC GAP data](https://www.fisheries.noaa.gov/foss/f?p=215%3A28).
 - **Query generation**: This library converts more common Python standard types to types usable by the API service and emulated in Python when needed, reducing the need to interact directly with [ORDS syntax](https://www.oracle.com/database/technologies/appdev/rest.html).

Though not intended to be general, this project also provides an example for working with [Oracle REST Data Services (ORDS)](https://www.oracle.com/database/technologies/appdev/rest.html) APIs in Python.

<br>
<br>

## Usage
This library provides access to the public API endpoints with optional zero catch ("absence") record inference. It offers keyword arguments for query filtering that match the column names described in the official [metadata repository](https://github.com/afsc-gap-products/metadata). Records returned by the service are parsed into plain old Python objects.

<br>

#### Basic queries
The `afscgap.query` method is the main entry point into the library. For example, this requests all records of Pasiphaea pacifica in 2021 from the Gulf of Alaska to get the median bottom temperature when they were observed:

```
import statistics

import afscgap

results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)

temperatures = [record.get_bottom_temperature_c() for record in results]
print(statistics.median(temperatures))
```

Note that `afscgap.query` returns a [Cursor](https://pyafscgap.org/devdocs/afscgap/cursor.html#Cursor). One can iterate over this `Cursor` to access [Record]https://pyafscgap.org/devdocs/afscgap/model.html#Record) objects. You can do this with list comprehensions, maps, etc or with a good old for loop like in this example which gets a histogram of haul temperatures:

```
count_by_temperature_c = {}

results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)

for record in results:
    temp = record.get_bottom_temperature_c()
    temp_rounded = round(temp)
    count = count_by_temperature_c.get(temp_rounded, 0) + 1
    count_by_temperature_c[temp_rounded] = count

print(count_by_temperature_c)
```

See [data structure section](#data-structure). Using an iterator will have the library negotiate pagination behind the scenes so this operation will cause multiple HTTP requests while the iterator runs.

<br>

#### Enable absence data
One of the major limitations of the official API is that it only provides presence data. However, this library can optionally infer absence or "zero catch" records using a separate static file produced by NOAA AFSC GAP. The [algorithm and details for absence inference](#absence-vs-presence-data) is further discussed below.

Absence data / "zero catch" records inference can be turned on by setting `presence_only` to false in `query`. To demonstrate, this example finds total area swept and total weight for Gadus macrocephalus from the Aleutian Islands in 2021:

```
import afscgap

results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Gadus macrocephalus',
    presence_only=False
)

total_area = 0
total_weight = 0

for record in results:
    total_area += record.get_area_swept_ha()
    total_weight += record.get_weight()

template = '%.2f kg / hectare swept (%.1f kg, %.1f hectares'
weight_per_area = total_weight / total_area
message = template % (weight_per_area, total_weight, total_area)

print(message)
```

For more [details on the zero catch record feature](#absence-vs-presence-data), please see below.

<br>

#### Serialization
Users may request a dictionary representation:

```
results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)

# Get dictionary from individual record
for record in results:
    dict_representation = record.to_dict()
    print(dict_representation['bottom_temperature_c'])

results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)

# Get dictionary for all records
results_dicts = results.to_dicts()

for record in results_dicts:
    print(record['bottom_temperature_c'])
```

Note `to_dicts` returns an iterator by default, but it can be realized as a full list using the `list()` command.

<br>

#### Pandas
The dictionary form of the data can be used to create a Pandas dataframe:

```
import pandas

import afscgap

results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)

pandas.DataFrame(results.to_dicts())
```

Note that Pandas is not required to use this library.

<br>

#### Advanced filtering
You can provide range queries which translate to ORDS or Python emulated filters. For example, the following requests before and including 2019:

```
results = afscgap.query(
    year=(None, 2019),
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)
```

The following requests data after and including 2019:

```
results = afscgap.query(
    year=(2019, None),
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)
```

Finally, the following requests data between 2015 and 2019 (includes 2015 and 2019):

```
results = afscgap.query(
    year=(2015, 2019),
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)
```

For more advanced filters, please see manual filtering below.

<br>

#### Manual filtering
Users may provide advanced queries using Oracle's REST API query parameters. For example, this queries for 2021 records with haul from the Gulf of Alaska in a specific geographic area:

```
import afscgap

results = afscgap.query(
    year=2021,
    latitude_dd={'$between': [56, 57]},
    longitude_dd={'$between': [-161, -160]}
)

count_by_common_name = {}

for record in results:
    common_name = record.get_common_name()
    new_count = record.get_count()
    count = count_by_common_name.get(common_name, 0) + new_count
    count_by_common_name[common_name] = count
```

For more info about the options available, consider the [Oracle docs](https://docs.oracle.com/en/database/oracle/oracle-rest-data-services/19.2/aelig/developing-REST-applications.html#GUID-F0A4D4F9-443B-4EB9-A1D3-1CDE0A8BAFF2) or a helpful unaffiliated [getting started tutorial from Jeff Smith](https://www.thatjeffsmith.com/archive/2019/09/some-query-filtering-examples-in-ords/).

<br>

#### Manual pagination
By default, the library will iterate through all results and handle pagination behind the scenes. However, one can also request an individual page:

```
results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Pasiphaea pacifica'
)

results_for_page = results.get_page(offset=20, limit=100)
print(len(results_for_page))  # Will print 32 (results contains 52 records)
```

Client code can also change the pagination behavior used when iterating:

```
results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Pasiphaea pacifica',
    start_offset=10,
    limit=200
)

for record in results:
    print(record.get_bottom_temperature_c())
```

Note that records are only requested once during iteration and only after the prior page has been returned via the iterator ("lazy" loading).

<br>
<br>

## Data structure
The schema drives the getters and filters available on in the library. Note that data structures are defined in the [model submodule](https://pyafscgap.org/devdocs/afscgap/model.html) but client code generally only needs to interact with [Record](https://pyafscgap.org/devdocs/afscgap/model.html#Record) objects.

<br>

#### Schema

A Python-typed description of the fields is provided below.

| **Field**             | **Python Type** | **Description** |
|-----------------------|-----------------|-----------------|
| year                  | float           | Year for the survey in which this observation was made. |
| srvy                  | str             | The name of the survey in which this observation was made. NBS (N Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea Slope), or GOA (Gulf of Alaska) |
| survey                | str             | Long form description of the survey in which the observation was made. |
| survey_id             | float           | Unique numeric ID for the survey. |
| cruise                | float           | An ID uniquely identifying the cruise in which the observation was made. Multiple cruises in a survey. |
| haul                  | float           | An ID uniquely identifying the haul in which this observation was made. Multiple hauls per cruise. |
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
| tsn                   | Optional[int]   | Taxonomic information system species code. |
| ak_survey_id          | int             | AK identifier for the survey. |

For more information on the schema, see the [metadata](https://github.com/afsc-gap-products/metadata) repository but note that the fields may be slightly different in the Python library per what is actually returned by the API.

<br>

#### Filters and getters

These fields are available as getters on `afscgap.model.Record` (`result.get_srvy()`) and may be used as optional filters on the query `asfcgagp.query(srvy='GOA')`. Fields which are `Optional` have two getters. First, the "regular" getter (`result.get_count()`) will assert that the field is not None before returning a non-optional. The second "maybe" getter (`result.get_count_maybe()`) will return None if the value was not provided or could not be parsed.

| **Filter keyword**    | **Regular Getter**                   | **Maybe Getter**                                     |
|-----------------------|--------------------------------------|------------------------------------------------------|
| year                  | get_year() -> float                  |                                                      |
| srvy                  | get_srvy() -> str                    |                                                      |
| survey                | get_survey() -> str                  |                                                      |
| survey_id             | get_survey_id() -> float             |                                                      |
| cruise                | get_cruise() -> float                |                                                      |
| haul                  | get_haul() -> float                  |                                                      |
| stratum               | get_stratum() -> float               |                                                      |
| station               | get_station() -> str                 |                                                      |
| vessel_name           | get_vessel_name() -> str             |                                                      |
| vessel_id             | get_vessel_id() -> float             |                                                      |
| date_time             | get_date_time() -> str               |                                                      |
| latitude_dd           | get_latitude_dd() -> float           |                                                      |
| longitude_dd          | get_longitude_dd() -> float          |                                                      |
| species_code          | get_species_code() -> float          |                                                      |
| common_name           | get_common_name() -> str             |                                                      |
| scientific_name       | get_scientific_name() -> str         |                                                      |
| taxon_confidence      | get_taxon_confidence() -> str        |                                                      |
| cpue_kgha             | get_cpue_kgha() -> float             | get_cpue_kgha_maybe() -> Optional[float]             |
| cpue_kgkm2            | get_cpue_kgkm2() -> float            | get_cpue_kgkm2_maybe() -> Optional[float]            |
| cpue_kg1000km2        | get_cpue_kg1000km2() -> float        | get_cpue_kg1000km2_maybe() -> Optional[float]        |
| cpue_noha             | get_cpue_noha() -> float             | get_cpue_noha_maybe() -> Optional[float]             |
| cpue_nokm2            | get_cpue_nokm2() -> float            | get_cpue_nokm2_maybe() -> Optional[float]            |
| cpue_no1000km2        | get_cpue_no1000km2() -> float        | get_cpue_no1000km2_maybe() -> Optional[float]        |
| weight_kg             | get_weight_kg() -> float             | get_weight_kg_maybe() -> Optional[float]             |
| count                 | get_count() -> float                 | get_count_maybe() -> Optional[float]                 |
| bottom_temperature_c  | get_bottom_temperature_c() -> float  | get_bottom_temperature_c_maybe() -> Optional[float]  |
| surface_temperature_c | get_surface_temperature_c() -> float | get_surface_temperature_c_maybe() -> Optional[float] |
| depth_m               | get_depth_m() -> float               |                                                      |
| distance_fished_km    | get_distance_fished_km() -> float    |                                                      |
| net_width_m           | get_net_width_m() -> float           | get_net_width_m_maybe() -> Optional[float]           |
| net_height_m          | get_net_height_m() -> float          | get_net_height_m_maybe() -> Optional[float]          |
| area_swept_ha         | get_area_swept_ha() -> float         |                                                      |
| duration_hr           | get_duration_hr() -> float           |                                                      |
| tsn                   | get_tsn() -> int                     | get_tsn_maybe() -> Optional[int]                     |
| ak_survey_id          | get_ak_survey_id() -> int            |                                                      |

`Record` objects also have a `is_complete` method which returns true if all the fields with an `Optional` type are non-None and the `date_time` could be parsed and made into an ISO 8601 string.

<br>
<br>

## Absence vs presence data
The API itself provides access to presence only data. This means that records are only given for when a species was found. This can cause issues if trying to aggregate data like, for example, to determine the weight of the species in a region in terms of catch weight per hectare. The AFSC GAP API on its own would not necessarily provide the total nubmer of hecatres surveyed in that region because hauls without the species present would be excluded. That in mind, this library provides a method for inferring absence data.

<br>

#### Example of absence data in aggregation
Here is a practical memory efficient example using [geolib](https://pypi.org/project/geolib/) and [toolz](https://github.com/pytoolz/toolz) to aggregate catch data by 5 character geohash.

```
import afscgap
import geolib.geohash
import toolz.itertoolz

import afscgap

results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Gadus macrocephalus',
    presence_only=False
)

def simplify_record(full_record):
    latitude = full_record.get_latitude_dd()
    longitude = full_record.get_longitude_dd()
    geohash = geolib.geohash.encode(latitude, longitude, 5)
    
    return {
        'geohash': geohash,
        'area': full_record.get_area_swept_ha(),
        'weight': full_record.get_weight_kg()
    }

def combine_record(a, b):
    assert a['geohash'] == b['geohash']
    return {
        'geohash': a['geohash'],
        'area': a['area'] + b['area'],
        'weight': a['weight'] + b['weight']
    }

simplified_records = map(simplify_record, results)
totals_by_geohash = toolz.reduceby(
    'geohash',
    combine_record,
    simplified_records
)
weight_by_area_tuples = map(
    lambda x: (x['geohash'], x['weight'] / x['area']),
    totals_by_geohash.values()
)
weight_by_area_by_geohash = dict(weight_by_area_tuples)
```

For more details see the [Python functional programming guide](https://docs.python.org/3/howto/functional.html). All that said, for some queries, the use of Pandas may lead to very heavy memory usage.

<br>

#### Absence inference algorithm
Though it is not possible to resolve this issue using the AFSC GAP API service alone, this library can infer those missing records using a separate static flat file provided by NOAA and the following algorithm:


 - Record the set of species observed from API service returned results.
 - Record the set of hauls observed from API service returned results.
 - Return records normally while records remain available from the API service.
 - Upon exhaustion of the API service results, [download the ~10M hauls flat file](https://pyafscgap.org/community/hauls.csv) from this library's community.
 - For each species observed in the API returned results, check if that species had a record for each haul reported in the flat file.
 - For any hauls without the species record, yield an 0 catch record from the iterator for that query.

This procedure is disabled by default. However, it can be enabled through the `presence_only` keyword in `query` like so: `asfcgap.query(presence_only=False)`.

<br>

#### Memory efficiency of absence inference
Note that `presence_only=False` will return a lot of records. Indeed, in some queries, this may stretch to many millions. As described in [community guidelines](#community), a goal of this project is provide those data in a memory-efficient way and, specifically, these "zero catch" records are generated by the library's iterator as requested but never all held in memory at the same time. It is recommened that client code also take care in memory efficiency. This can be as simple as aggregating via `for` loops which only hold one record in memory at a time. Similarly, consider using `map`, `filter`, `reduce`, [itertools](https://docs.python.org/3/library/itertools.html), etc.

<br>

#### Manual pagination of zero catch records
The goal of `Cursor.get_page` is to pull results from a page returned for a query as it appears in the NOAA API service. Note that `get_page` will not return zero catch records even with `presence_only=False` because the "page" requested does not technically exist in the API service. In order to use the negative records inference feature, please use the iterator option instead.

<br>

#### Filtering absence data
Note that the library will emulate filtering in Python so that haul records are filtered just as presence records are filtered by the API service. This works for "basic" and "advanced" filtering. However, at time of writing, "manual filtering" as described below using ORDS syntax is not supported when `presence_data=False`. Also, by default, a warning will be emitted when using this feature to help new users be aware of potential memory issues. This can be suppressed by including `suppress_large_warning=True` in the call to query.

<br>
<br>

## Data quality and completeness
There are a few caveats for working with these data that are important for researchers to understand.

<br>

#### Incomplete or invalid records
Metadata fields such as `year` are always required to make a `Record` whereas others such as catch weight `cpue_kgkm2` are not present on all records returned by the API and are optional. See the [data structure section](#data-structure) for additional details. For fields with optional values:

 - A maybe getter (like `get_cpue_kgkm2_maybe`) is provided which will return None without error if the value is not provided or could not be parsed.
 - A regular getter (like `get_cpue_kgkm2`) is provided which asserts the value is not None before it is returned.

`Record` objects also have an `is_complete` method which returns true if both all optional fields on the `Record` are non-None and the `date_time` field on the `Record` is a valid ISO 8601 string. By default, records for which `is_complete` are false are returned when iterating or through `get_page` but this can be overridden by with the `filter_incomplete` keyword argument like so:

```
results = afscgap.query(
    year=2021,
    srvy='GOA',
    scientific_name='Pasiphaea pacifica',
    filter_incomplete=True
)

for result in results:
    assert result.is_complete()
```

Results returned by the API for which non-Optional fields could not be parsed (like missing `year`) are considered "invalid" and always excluded during iteration when those raw unreadable records are kept in a `queue.Queue[dict]` that can be accessed via `get_invalid` like so:

```
results = afscgap.query(year=2021, srvy='GOA')
valid = list(results)

invalid_queue = results.get_invalid()
percent_invalid = invalid_queue.qsize() / len(valid) * 100
print('Percent invalid: %%%.2f' % percent_invalid)

complete = filter(lambda x: x.is_complete(), valid)
num_complete = sum(map(lambda x: 1, complete))
percent_complete = num_complete / len(valid) * 100
print('Percent complete: %%%.2f' % percent_complete)
```

Note that this queue is filled during iteration (like `for result in results` or `list(results)`) and not `get_page` whose invalid record handling behavior can be specified via the `ignore_invalid` keyword.

<br>

#### Longitude
Though not officially mentioned by the NOAA API, the authors of this library observe some positive longitudes in returned data where negative longitudes of the same magnitude would be expected. Users of the library should be careful to determine how to handle these records (inferring they should have been the same magnitude of longitude but negative or excluded). Publications should be careful to document their decision.

<br>
<br>

## License
We are happy to make this library available under the BSD 3-Clause license. See LICENSE for more details. (c) 2023 Regents of University of California. See the [Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley](https://dse.berkeley.edu).

<br>
<br>

## Community
Thanks for your support! Pull requests and issues very welcome.

<br>

#### Contribution guidelines
We invite contributions via [our project Github](https://github.com/SchmidtDSE/afscgap). Please read the [CONTRIBUTING.md](https://github.com/SchmidtDSE/afscgap/blob/main/CONTRIBUTING.md) file for more information.

<br>

#### Debugging
While participating in the community, you may need to debug URL generation. Therefore, for investigating issues or evaluating the underlying operations, you can also request a full URL for a query:

```
results = afscgap.query(
    year=2021,
    latitude_dd={'$between': [56, 57]},
    longitude_dd={'$between': [-161, -160]}
)

print(results.get_page_url(limit=10, offset=0))
```

The query can be executed by making an HTTP GET request at the provided location.

<br>

#### Contacts
[Sam Pottinger](https://github.com/sampottinger) is the primary contact. Thanks to [Giulia Zarpellon](https://github.com/gizarp) and [Carl Boettiger](https://github.com/cboettig) for their contributions. This is a project of the [The Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley](https://dse.berkeley.edu). Please contact us via dse@berkeley.edu.

<br>
<br>

## Open Source
We are happy to be part of the open source community.

At this time, the only open source dependency used by this microlibrary is [Requests](https://docs.python-requests.org/en/latest/index.html) which is available under the [Apache v2 License](https://github.com/psf/requests/blob/main/LICENSE) from [Kenneth Reitz and other contributors](https://github.com/psf/requests/graphs/contributors). Our build and documentation systems also use the following but are not distributed with or linked to the project itself:

 - [mypy](https://github.com/python/mypy) under the [MIT License](https://github.com/python/mypy/blob/master/LICENSE) from Jukka Lehtosalo, Dropbox, and other contributors.
 - [nose2](https://docs.nose2.io/en/latest/index.html) under a [BSD license](https://github.com/nose-devs/nose2/blob/main/license.txt) from Jason Pellerin and other contributors.
 - [pdoc](https://github.com/mitmproxy/pdoc) under the [Unlicense license](https://github.com/mitmproxy/pdoc/blob/main/LICENSE) from [Andrew Gallant](https://github.com/BurntSushi) and [Maximilian Hils](https://github.com/mhils).
 - [pycodestyle](https://pycodestyle.pycqa.org/en/latest/) under the [Expat License](https://github.com/PyCQA/pycodestyle/blob/main/LICENSE) from Johann C. Rocholl, Florent Xicluna, and Ian Lee.
 - [pyflakes](https://github.com/PyCQA/pyflakes) under the [MIT License](https://github.com/PyCQA/pyflakes/blob/main/LICENSE) from Divmod, Florent Xicluna, and other contributors.

Thank you to all of these projects for their contribution.

<br>
<br>

## Version history
Annotated version history:

 - `0.0.5`: Changes to documentation.
 - `0.0.4`: Negative / zero catch inference.
 - `0.0.3`: Minor updates in documentation.
 - `0.0.2`: License under BSD.
 - `0.0.1`: Initial release.
