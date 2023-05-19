# Data model
The schema drives the getters and filters available on in the library. Note that data structures are defined in the [model submodule](https://pyafscgap.org/devdocs/afscgap/model.html) but client code generally only needs to interact with [Record](https://pyafscgap.org/devdocs/afscgap/model.html#Record) objects.

<br>
<br>

## Schema

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

## Filters and getters

These fields are available as getters on `afscgap.model.Record` (`result.get_srvy()`) and may be used as optional filters on the query `asfcgagp.query(srvy='GOA')`. Fields which are `Optional` have two getters. First, the "regular" getter (`result.get_count()`) will assert that the field is not None before returning a non-optional. The second "maybe" getter (`result.get_count_maybe()`) will return None if the value was not provided or could not be parsed.

| **API Field**         | **Filter on Query**                      | **Regular Getter**                             | **Maybe Getter**                                                |
|-----------------------|------------------------------------------|------------------------------------------------|-----------------------------------------------------------------|
| year                  | filter_year()                            | get_year() -> float                            |                                                                 |
| srvy                  | filter_srvy()                            | get_srvy() -> str                              |                                                                 |
| survey                | filter_survey()                          | get_survey() -> str                            |                                                                 |
| survey_id             | filter_survey_id()                       | get_survey_id() -> float                       |                                                                 |
| cruise                | filter_cruise()                          | get_cruise() -> float                          |                                                                 |
| haul                  | filter_haul()                            | get_haul() -> float                            |                                                                 |
| stratum               | filter_stratum()                         | get_stratum() -> float                         |                                                                 |
| station               | filter_station()                         | get_station() -> str                           |                                                                 |
| vessel_name           | filter_vessel_name()                     | get_vessel_name() -> str                       |                                                                 |
| vessel_id             | filter_vessel_id()                       | get_vessel_id() -> float                       |                                                                 |
| date_time             | filter_date_time()                       | get_date_time() -> str                         |                                                                 |
| latitude_dd           | filter_latitude(units='dd')              | get_latitude(units='dd') -> float              |                                                                 |
| longitude_dd          | filter_longitude(units='dd')             | get_longitude(units='dd') -> float             |                                                                 |
| species_code          | filter_species_code()                    | get_species_code() -> float                    |                                                                 |
| common_name           | filter_common_name()                     | get_common_name() -> str                       |                                                                 |
| scientific_name       | filter_scientific_name()                 | get_scientific_name() -> str                   |                                                                 |
| taxon_confidence      | filter_taxon_confidence()                | get_taxon_confidence() -> str                  |                                                                 |
| cpue_kgha             | filter_cpue_weight(units='kg/ha')        | get_cpue_weight(units='kg/ha') -> float        | get_cpue_weight_maybe(units='kg/ha') -> Optional[float]         |
| cpue_kgkm2            | filter_cpue_weight(units='kg/km2')       | get_cpue_weight(units='kg/km2') -> float       | get_cpue_weight_maybe(units='kg/km2') -> Optional[float]        |
| cpue_kg1000km2        | filter_cpue_weight(units='kg1000/km2')   | get_cpue_weight(units='kg1000/km2') -> float   | get_cpue_weight_maybe(units='kg1000/km2') -> Optional[float]    |
| cpue_noha             | filter_cpue_count(units='count/ha')      | get_cpue_count(units='count/ha') -> float      | get_cpue_count_maybe(units='count/ha') -> Optional[float]       |
| cpue_nokm2            | filter_cpue_count(units='count/km2')     | get_cpue_count(units='count/km2') -> float     | get_cpue_count_maybe(units='count/km2') -> Optional[float]      |
| cpue_no1000km2        | filter_cpue_count(units='count1000/km2') | get_cpue_count(units='count1000/km2') -> float | get_cpue_count_maybe(units='count1000/km2') -> Optional[float]  |
| weight_kg             | filter_weight(units='kg')                | get_weight(units='kg') -> float                | get_weight_maybe() -> Optional[float]                           |
| count                 | filter_count()                           | get_count() -> float                           | get_count_maybe() -> Optional[float]                            |
| bottom_temperature_c  | filter_bottom_temperature(units='c')     | get_bottom_temperature(units='c') -> float     | get_bottom_temperature_maybe(units='c') -> Optional[float]      |
| surface_temperature_c | filter_surface_temperature(units='c')    | get_surface_temperature(units='c') -> float    | get_surface_temperature_maybe() -> Optional[float]              |
| depth_m               | filter_depth(units='m')                  | get_depth(units='m') -> float                  |                                                                 |
| distance_fished_km    | filter_distance_fished(units='km')       | get_distance_fished(units='km') -> float       |                                                                 |
| net_width_m           | filter_net_width(units='m')              | get_net_width(units='m') -> float              | get_net_width(units='m') -> Optional[float]                     |
| net_height_m          | filter_net_height(units='m')             | get_net_height(units='m') -> float             | get_net_height(units='m') -> Optional[float]                    |
| area_swept_ha         | filter_area_swept(units='ha')            | get_area_swept(units='ha') -> float            |                                                                 |
| duration_hr           | filter_duration(units='hr')              | get_duration(units='hr') -> float              |                                                                 |
| tsn                   | filter_tsn()                             | get_tsn() -> int                               | get_tsn_maybe() -> Optional[int]                                |
| ak_survey_id          | filter_ak_survey_id()                    | get_ak_survey_id() -> int                      |                                                                 |

Support for additional units are available for some fields and are calculated on the fly within the `afscgap` library when requested. `Record` objects also have a `is_complete` method which returns true if all the fields with an `Optional` type are non-None and the `date_time` could be parsed and made into an ISO 8601 string.