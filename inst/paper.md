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
The Groundfish Assessment Program within NOAA's Alaska Fisheries Science Center produces longitudinal catch data for the region [@afscgap]. Supporting ocean health research and fisheries management, these "hauls" report where marine species are found during bottom trawl surveys and in what quantities [@example]. Increasing data usability for communities of diverse programming experience, Pyafscgap.org offers not just friendlier REST API operation for this economically and scientifically important dataset but query language compliation, memory-efficient algorithms for "zero-catch" inference, and interactive visual analytics. Altogether, this research toolset supports investigatory tasks not easily executable using the API service alone and broadens access through game and information design.

# Statement of need
Pyafscgap.org reduces barriers for use of NOAA AFSC RACE GAP^[Groundfish Assessment Program in the Resource Assessment and Conservation Engineering Division of the National Oceanic and Atmospheric Administration's Alaska Fisheries Science Center] data, offering:

 - Improved developer usability.
 - Memory-efficient algorithms for analysis requiring zero catch inference.
 - Tools for those with less developer experience.

Altogether, these open source tools extend the dataset's reach and approachability.

## Developer usability
Working with these data requires knowledge of tools ouside the Python "standard toolset" like the closed-source Oracle REST Data Services (ORDS) [@ords]. The `afscgap` package offers easier access to the official REST service with automated pagination, ORDS compilation, and documented types. Together, these tools enable Python developers to use familiar patterns to interact with these data: type checking, standard documentation, and compatability with common Python data-related libraries.

## Record inference
The API struggles supporting some investigations as it provides "presence-only" data [@inport]. For example, the API may readily yield total mass of Pacific cod but not its geohash-aggregated catch per unit effort [@geohash].

$$CPUE_{species} = \frac{m_{species}}{A_{swept}}$$

Knowing CPUE (kg/ha) must also include "absence data" or hauls in which the speices was not recorded, this package can efficiently infer those hauls not easily returned from the API service [@notebook].

## Broad accessibility
Though the `afscgap` Python package makes GAP catch data more accessible, the size and complexity of this dataset complicates comparative analysis between species, years, and/or geographic areas [@notebook]. Without deep developer experience, it may still be difficult to get started even with scientific background. To address a broader audience, this project also offers a no-code visualization tool sitting on top of `afscgap` with CSV and Python code export as a bridge to further analysis.

# Functions
This project aims to improve accessibility of GAP catch data and offer approachable tools to kickstart analysis.

## Lazy querying facade
The `afscgap` library manages significant complexity to offer a simple familiar interface to Python developers:

 - Lazy "generator iterables" increase accessibility by encapsulating logic for memory-efficient pagination and "data munging" behind Python-standard iterators [@lazy].
 - To support zero catch data, decorators adapt diverse structures to common interfaces, offering polymorphism [@decorators].
 - Offering a single object entry-point into the library, a "facade" frees users from needing deep understanding of the library's types, a goal furthered by compilation of "standard" Python types to Oracle REST Data Service queries [@facade].

![Diagram of afscgap.\label{fig:library}](library.png)

## Zero catch inference
"Zero catch" inference enables a broader range of analysis with the following algorithm:

 - Paginate while records remain available from the API service.
   - Record species and hauls observed from API-returned results.
   - Return records as available.
 - Generate inferred records after API exhaustion.
   - For each species observed in API results, check if it had a record for each haul in a hauls flat file [@flatfile].
   - For any hauls without the species, produce a record from the iterator.

This library offers Python-emulation of ORDS filters for inferred records.

## Visualization
This complex dataset requires technical sophistication to navigate and, to further increase accessibility, visualization tools help start temporal, spatial, and species comparisons with deep linking, coordinated highlighting, separated color channels, summary statistics, and side-by-side display [@few]. To support learning this UI, an optional introduction sequence tutorializes a "real" analysis via Hayashida^[Uses Mark Brown's formalization [@brown].] level design [@hayashida; @brown]:

 - **Introduction**: The tool shows information about Pacific cod with pre-filled controls used to achieve that analysis gradually fading in, asking the user for minor modifications.
 - **Development**: Using the mechanics introduced moments prior, the tool invites the user to change the analysis to compare different regions.
 - **Twist**: Enabling overlays on the same display, the user leverages mechanics they just exercised in a now more complex interface.
 - **Conclusion**: The visualization invites the user to demonstrate skills acquired in a new problem.

Note that this visualization also serves as a starting point for continued analysis by generating either CSV or Python code to take work into other tools.

![Visualization screenshot.\label{fig:viz}](viz.png)

In addition to graduate classroom use, five individuals with relevant background offered detailed feedback on this open source visualization. Though sometimes aided by a think-aloud prompt, feedback was limited to needs assessment / quality improvement specific to this publicly accessible web service [@thinkaloud].

## Limitations
As further documented in the repository [@readme], these tools:

 - Run single-threaded and synchoronous.
 - Represents hauls as points not areas in visualization aggregation due to dataset limitation.
 - Must exclude any hauls also excluded by NOAA from their dataset.

# Acknowledgements
Thanks to:

 - Runtime dependencies: ColorBrewer, D3, Flask, Geolib, Requests, Toolz, and Papa Parse [@colorbrewer; @d3; @flask; @geolib; @requests; @toolz; @papa].
 - Library advice: Carl Boettiger, Fernando Perez, and PyOpenSci reviewers.
 - Visualization advice: Lewis Barnett, Magali de Bruyn, Brookie Guzder-Williams, Angela Hayes, David Joy, Emily Markowitz, and Maya Weltman-Fahs.
 - Ciera Martinez for general guidance.
 - Draw.io for diagrams [@diagrams].

Project of The Eric and Wendy Schmidt Center for Data Science and the Environment at UC Berkeley.

# References
