# Objectives
This document describes the project's scope and objectives in further detail.

<br>
<br>

## Developer needs
Scientists and developers working on ocean health have an interest in survey data from organizations like [NOAA Fisheries](https://www.fisheries.noaa.gov/). However,

 - Using the GAP API from NOAA AFSC in Python can sometimes require a lot of work: understanding a complex schema, determining how to interact with a proprietary REST data service, forming long query URLs, and navigating pagination. 
 - The official API service provides presence-only data, complicating some common types of analysis and aggregation.
 - Limited public tooling exists for visualizing within and, especially, creating comparisons between subsets of the AFSC GAP dataset which are useful for some types of investigation.

These various elements together may increase the barrier for working with these data, limiting their reach within some communities including the Python community.

<br>

## Goals
This tool set aims to provide the following from the start to finish of an investigation:

 - **Visual analytics**: Visualization tools for quickly exploring AFSC GAP, helping users start their investigations by finding and comparing subsets of interest within the broader dataset.
 - **API access**: A type-annotated and documented Python interface to the official API service with ability to query with automated pagination, providing results in various formats compatible with different Python usage modalities (Pandas, pure-Python, etc). It adapts the HTTP-based API used by the agency with Python type hints for easy query and interface. 
 - **Contextual documentation**: Python docstrings annotate the data structures provided by the API to help users navigate the various fields available, offering contextual documentation when supported by Python IDEs.
 - **Absence inference**: Tools to infer absence or "zero catch" data as required for certain analysis and aggregation using a [supplemental hauls flat file dataset](https://pyafscgap.org/community/hauls.csv). Note that this flat file is provided by and hosted for this library's community after being created from [non-API public AFSC GAP data](https://www.fisheries.noaa.gov/foss/f?p=215%3A28). It is updated yearly.
 - **Query generation**: This library converts more common Python standard types to types usable by the API service and emulated in Python when needed, reducing the need to interact directly with [ORDS syntax](https://www.oracle.com/database/technologies/appdev/rest.html).
 - **Accelerate specialized analysis**: Affordances in code and non-code tools for both programmers and non-programmers to continue their investigation easily, including in tools outside this tool set.
 - **Inclusive design**: Users of any skillset should be able to get something from this project.

Though not intended to be general, this project also provides an example for working with [Oracle REST Data Services (ORDS)](https://www.oracle.com/database/technologies/appdev/rest.html) APIs in Python.