# Objectives
This document describes the project's scope and objectives in further detail.

<br>
<br>

## Developer needs
Scientists and developers working on ocean health have an interest in survey data from organizations like [NOAA Fisheries](https://www.fisheries.noaa.gov/). However,

 - Using the GAP API from NOAA AFSC in Python can sometimes require a lot of work: understanding a complex schema, determining how to interact with a proprietary REST data service, forming long query URLs, and navigating pagination. 
 - The official API service provides either presence-only data or unjoined data, complicating some common types of analysis and aggregation.
 - Some uses of the official API require resource-intensive downloading of full catch or species datasets even if filtering for a small subset.
 - Limited public tooling exists for visualizing within and, especially, creating comparisons between subsets of the AFSC GAP dataset which are useful for some types of investigation.

These various elements together may increase the barrier for working with these data, limiting their reach within some communities including the Python community.

<br>

## Goals
This tool set aims to provide the following from the start to finish of an investigation:

 - **Visual analytics**: Visualization tools for quickly exploring AFSC GAP, helping users start their investigations by finding and comparing subsets of interest within the broader dataset.
 - **Data access**: A type-annotated and documented Python interface to GAP datasets with ability to query with automated pagination, providing results in various formats compatible with different Python usage modalities (Pandas, pure-Python, etc).
 - **Contextual documentation**: Python docstrings annotate the data structures provided by the API (and / or community files) to help users navigate the various fields available, offering contextual documentation when supported by Python IDEs.
 - **Absence inference**: Tools to infer absence or "zero catch" data as required for certain analysis and aggregation.
 - **Community data***: Updated yearly, we offer [community datasets](https://data.pyafscgap.org/) which support more efficient queries.
 - **Query generation**: This library converts Python types to HTTP queries for filtering without needing to manipulate those queries direclty.
 - **Accelerate specialized analysis**: Affordances in code and non-code tools for both programmers and non-programmers to continue their investigation easily, including in tools outside this tool set.
 - **Inclusive design**: Users of any skillset should be able to get something from this project.

This project aims to provide long term API stability across major releases where permitted by the upstream data source run by NOAA.
