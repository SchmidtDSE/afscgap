# Data quality and completeness
There are a few caveats for working with these data that are important for researchers to understand. These are detailed in our [limitations docs](https://pyafscgap.org/docs/limitations/).

<br>
<br>

## Incomplete or invalid records
Metadata fields such as `year` are always required to make a `Record` whereas others such as catch weight `cpue_kgkm2` are not present on all records returned and are optional. See the [data structure section](https://pyafscgap.org/docs/model/) for additional details. For fields with optional values:

 - A maybe getter (like `get_cpue_weight_maybe`) is provided which will return None without error if the value is not provided or could not be parsed.
 - A regular getter (like `get_cpue_weight`) is provided which asserts the value is not None before it is returned.

`Record` objects also have an `is_complete` method which returns true if both all optional fields on the `Record` are non-None and the `date_time` field on the `Record` is a valid ISO 8601 string. By default, records for which `is_complete` are false are returned when iterating or through `get_page` but this can be overridden by with the `filter_incomplete` keyword argument like so:

```python
import afscgap

query = afscgap.Query()
query.filter_year(eq=2021)
query.filter_srvy(eq='GOA')
query.filter_scientific_name(eq='Pasiphaea pacifica')
query.set_filter_incomplete(True)
results = query.execute()

for result in results:
    assert result.is_complete()
```

Results returned for which non-Optional fields could not be parsed (like missing `year`) are considered "invalid" and always excluded during iteration when those raw unreadable records are kept in a `queue.Queue[dict]` that can be accessed via `get_invalid` like so:

```python
import afscgap

query = afscgap.Query()
query.filter_year(eq=2021)
query.filter_srvy(eq='GOA')
query.filter_scientific_name(eq='Pasiphaea pacifica')
results = query.execute()

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

## Longitude
Though not officially mentioned by the NOAA API, the authors of this library observe some positive longitudes in returned data where negative longitudes of the same magnitude would be expected. Users of the library should be careful to determine how to handle these records (inferring they should have been the same magnitude of longitude but negative or excluded). Publications should be careful to document their decision.

<br>

## Fully empty hauls
We've been made aware that some historical surveys from NOAA may not report hauls in the hauls flat file if no specimens were captured. This is a limitation of upstream data and may cause some approximation in CPUE calculations depending on one's definition of effort (should hauls which did not get any specimens be considered a "successful" haul and should they be included as effort?). Note that this inclusion decision is decided by NOAA and not this project. Instead this package uses any hauls reported by NOAA in zero catch inference. One can use an alternative inclusion criteria by providing a static hauls file via `set_hauls_prefetch`.