---
title: 'Pyafscgap.org: Open source multi-modal Python-based tools for NOAA AFSC RACE GAP'
tags:
  - Python
  - fishery
  - alaska
  - groundfish
  - biodiversity
  - food
  - visualization
authors:
  - name: A Samuel Pottinger
    orcid: 0000-0002-0458-4985
    affiliation: 1
  - name: Giulia Zarpellon
    orcid: 0000-0002-9122-4709
    affiliation: 1
author:
  - "A Samuel Pottinger":
      institute:
        - ucberkeley
      correspondence: "yes"
      email: sam.pottinger@berkeley.edu
  - "Giulia Zarpellon":
      institute:
        - ucberkeley
affiliations:
 - name: University of California, Berkeley
   index: 1
institute:
  - ucberkeley: University of California, Berkeley
date: 4 April 2023
bibliography: paper.bib
---

# Summary
The Resource Assessment and Conservation Engineering Division of the National Oceanic and Atmospheric Administration's Alaska Fisheries Science Center (NOAA AFSC RACE) runs the [Groundfish Assessment Program](https://www.fisheries.noaa.gov/contact/groundfish-assessment-program) (GAP) which produces longitudinal catch data [@afscgap]. These "hauls" report where marine species are found during bottom trawl surveys and in what quantities, empowering ocean health research and fisheries management [@example]. Increasing accessibility of these important data through tools for individuals of diverse programming experience, Pyafscgap.org offers not just easier access to the dataset's REST API through query compilation but provides both memory-efficient algorithms for "zero-catch inference" and interactive visual analytics tools [@inport]. Altogether, this toolset supports investigatory tasks not easily executable using the API service alone and, leveraging game and information design, offers these data to a broader audience.

# Statement of need
Pyafscgap.org reduces barriers for use of GAP data, offering open source solutions for addressing the dataset's use of proprietary technology, presence-only nature, and size / complexity [@inport].

## Developer accessibility
Working with these data requires knowledge of tools ouside the Python "standard toolchest" like the closed-source Oracle REST Data Services (ORDS) [@ords]. The `afscgap` package offers easier open source-based developer access to the official REST service with automated pagination, Python to ORDS syntax compilation, and documented types. Together, these tools enable Python developers to use familiar patterns to interact with these data like type checking, standard documentation, and other Python data-related libraries.

## Common analysis
Access to the API alone cannot support some investigations as the API provides "presence-only" data [@inport]. Many types of analysis require information not just about where a species was present but also where it was not. For example, consider geohash-aggregated species catch per unit effort: while the presence-only dataset may provide a total weight or count, the total area swept for a region may not necessarily be easily available but required [@geohash; @notebook]. The `afscgap` Python package can, with memory efficiency, algorithmically infer those needed "zero catch" records.

## General public accessibility
Though the `afscgap` Python package makes GAP catch data more accessible to developers, the size and complexity of this dataset requires non-trivial engineering for comparative analysis between species, years, and/or geographic areas [@notebook]. Without deep developer experience, it can be difficult to get started. To address a broader audience, this project also offers a no-code visualization tool sitting on top of `afscgap` to begin investigations with CSV and Python code export as a bridge to further analysis.

# Functions
This project aims to improve accessibility of GAP catch data, democratizing developer access and offering inclusive approachable tools to kickstart analysis.

## Lazy querying facade
The `afscgap` library manages significant data structure complexity to offer a simple familiar interface to Python developers. First, lazy "generator iterables" increase accessibility by encapsulating logic for memory-efficient pagination and "data munging" behind Python-standard iterators [@lazy]. Furthermore, to support zero catch data, decorators adapt diverse structures to common interfaces, offering polymorphism [@decorators]. Finally, offering a single object entry-point into the library, a "facade" approach allows the user to interact with these systems without requiring deep understanding of the library's types, a goal furthered by compilation of "standard" Python types to Oracle REST Data Service queries [@facade].

![Diagram of simplified afscgap operation [@diagrams].\label{fig:library}](library.png)

## Zero catch inference
"Negative" or "zero catch" inference enables scientists to conduct a broader range of analysis. To achieve this, the package uses the following algorithm:

 - Paginate while records remain available from the API service.
   - Record species and hauls observed from API-returned results.
   - Return records as available.
 - Generate inferred records after API exhaustion.
   - For each species observed in API results, check if it had a record for each haul in a hauls flat file [@flatfile].
   - For any hauls without the species, produce an 0 catch record from the iterator.

Note that, this library offers Python-emaultion of ORDS-compiled fitlers for inferred records.

## Visualization
Despite these developer-focused tools, zero catch inference's millions of records requires technical sophistication to navigate. To further increase accessibility, this project offers a visualization tool for starting temporal, spatial, and species comparisons with coordinated highlighting, separated color channels, summary statistics, and side-by-side display [@few].

![Screenshot of the visualization tool.\label{fig:viz}](viz.png)

Of course, building competency in a sophisticated interface like this presents user experience challenges and, to that end, this project interprets Hayashida level design via Mark Brown's formalization into an in-tool introduction sequence that directs the player through a "real" analysis [@hayashida; @brown]:

 - **Introduction**: The player sees information about Pacific cod with pre-filled elements used to achieve that analysis gradually fading in.
 - **Development**: Using the mechanics introduced moments prior, the tool invites the player to change the analysis to compare different regions with temperature data.
 - **Twist**: Overlays on the same display are enabled, allowing the player to leverage mechanics they just exercised in a now more complex interface.
 - **Conclusion**: End with giving the player an opportunity to demonstrate all of the skills acquired in a new problem.

While this interface uses game / information design techniques to offer an accessible on-ramp to quickly learn a sophisticated interface, it also serves as a starting point for continued analysis by generating either CSV or Python code to take work into other tools. Examined via Thinking-aloud Method [@thinkaloud].

## Limitations
Notable current limitations:

 - Single-threaded and non-asynchoronous.
 - Due to dataset limitations, hauls are represeted by points not areas in visualization aggregation [@readme].

# Acknowledgements
Thanks to the following for feedback / testing on these components:

 - Library: Carl Boettiger and Fernando Perez
 - Visualization: Maya Weltman-Fahs, Brookie Guzder-Williams, and Magali de Bruyn.

Project of the The Eric and Wendy Schmidt Center for Data Science and the Environment at University of California Berkeley. Though the README lists full library credits, thanks to runtime dependencies ColorBrewer, D3, Flask, Geolib, Requests, Toolz, and Papa Parse [@colorbrewer; @d3; @flask; @geolib; @requests; @toolz; @papa].

# References