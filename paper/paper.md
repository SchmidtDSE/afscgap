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
 - name: University of California, Berkeley, California, United States of America
   index: 1
institute:
  - ucberkeley: University of California Berkeley, California, United States of America
date: 2 June 2023
bibliography: paper.bib
---

# Summary
NOAA AFSC's Groundfish Assessment Program produces longitudinal catch data which support ocean health research and fisheries management [@afscgap]. These "hauls" report in what quantities and locations bottom trawl surveys find different marine species along with environmental conditions at the time and place of observation [@example]. Increasing usability for communities of diverse programming experience, Pyafscgap.org offers query language compilation, memory-efficient algorithms for "zero-catch" inference, and interactive visual analytics for these economically and scientifically important GAP datasets. Altogether, this research toolset supports investigatory tasks across survey programs' locations and broadens access through game and information design.

# Statement of need
Pyafscgap.org reduces barriers for use of NOAA AFSC RACE GAP^[Groundfish Assessment Program in the Resource Assessment and Conservation Engineering Division of the National Oceanic and Atmospheric Administration's Alaska Fisheries Science Center] data, offering:

 - Improved developer usability.
 - Memory-efficient algorithms for zero catch inference.
 - Zero-code visualization tools.

Altogether, these open source tools extend the reach and approachability of GAP's multiple survey programs to support analysis like longitudinal catch per unit effort (CPUE) in context of environmental changes [@notebook].

## Developer usability
Working with these data requires knowledge of tools outside the Python "standard toolset" like closed-source ORDS query language [@ords]. While the `afscgap` package offers easier access to the official REST service, it also crucially offers ORDS compilation, documented types, and lazy access to these large datasets. Together, these tools enable Python developers to efficiently use familiar patterns to interact with these data: type checking, standard documentation, and compatibility with common Python data-related libraries.

## Record inference
Surveys on their own within the API struggle supporting some investigations as they provide "presence-only" data [@inport]. For example, the API may readily yield total mass of Pacific cod but not its geohash-aggregated CPUE [@geohash].

$$CPUE_{species} = \frac{m_{species}}{A_{swept}}$$

Metrics like CPUE need "absence data" or hauls in which the species was not recorded. This package can efficiently infer those results [@notebook].

## Broad accessibility
Though the `afscgap` Python package makes GAP catch information more accessible, the data's size and complexity complicates comparative analysis between species, years, and/or geographic areas [@notebook]. Without deep developer experience, it may still be difficult to get started even with scientific background. To address a broader audience, this project offers visualization on top of `afscgap` with CSV and Python code export as a bridge to further analysis.

# Functions
This project improves accessibility of GAP data and offers approachable tools to kickstart analysis.

## Efficient facade
The `afscgap` library manages significant complexity to offer a simple familiar interface to Python developers:

 - Lazy "generator iterables" increase accessibility by encapsulating logic for memory-efficient pagination and "data munging" behind Python-standard iterators [@lazy].
 - Decorators adapt diverse structures to common interfaces in zero catch data, offering polymorphism that helps to reduce the complexity of code using the library [@decorators].
 - Providing a single object entry-point into the library, a "facade" frees users from needing deep understanding of the library's types and transparently compiles "standard" Python types to Oracle REST Data Service queries [@facade].

![Diagram of afscgap.\label{fig:library}](library.png)

## Zero catch inference
"Zero catch" inference enables a broader range of analysis with the following algorithm:

 - Lazily paginate while records remain available from the API service.
   - Record species and hauls observed from API-returned results.
   - Return records as available.
 - Lazily generate inferred records after API exhaustion.
   - For each species observed in API results, check if it had a record for each haul in a hauls flat file [@flatfile].
   - For any hauls without the species, produce a record from the iterator.

Note `afscgap` performs Python-emulation of ORDS filters on inferred records.

## Visualization
These complex data require technical sophistication to navigate and, to increase accessibility, visualization tools help start temporal, spatial, and species comparisons with deep linking, coordinated highlighting, separated color channels, summary statistics, and side-by-side display [@few].

![Visualization screenshot.\label{fig:viz}](viz.png)

To support learning this UI, an optional introduction sequence tutorializes a "real" analysis via Hayashida design [@hayashida; @brown]:

 - **Introduction**: The tool shows information about Pacific cod with pre-filled controls used to achieve that analysis gradually fading in, asking the user for minor modifications.
 - **Development**: Using the mechanics introduced moments prior, the tool invites the user to change the analysis to compare different regions.
 - **Twist**: Enabling overlays on the same display, the user leverages mechanics they just exercised in a now more complex interface.
 - **Conclusion**: The visualization invites the user to demonstrate skills acquired in a new problem.

This visualization also serves as a starting point for continued analysis by generating either CSV or Python code to take work into other tools.

In addition to use in a graduate classroom setting, five individuals with relevant background offered feedback on this open source visualization with four aided by a think-aloud prompt^[Discussion limited to tool-specific needs assessment / quality improvement, collecting information about the tool and not individuals. IRB questionnaire on file finds "project does not constitute human subjects research" and review is not required.] [@thinkaloud].

## Limitations
As further documented in the repository [@readme], these tools:

 - Run single-threaded and synchronous.
 - Aggregate hauls as points in visualization due to data limitation.
 - Ignore hauls if entirely excluded by NOAA.

# Acknowledgments
Thanks to:

 - Runtime dependencies: ColorBrewer, D3, Flask, Geolib, Requests, Toolz, and Papa Parse [@colorbrewer; @d3; @flask; @geolib; @requests; @toolz; @papa].
 - Library advice: Carl Boettiger, Fernando Perez, and PyOpenSci reviewers.
 - Visualization advice: Magali de Bruyn, Brookie Guzder-Williams, Angela Hayes, David Joy, and Maya Weltman-Fahs.
 - Lewis Barnett, Emily Markowitz, and Ciera Martinez for general guidance.
 - Draw.io for diagrams [@diagrams].

Project of The Eric and Wendy Schmidt Center for Data Science and the Environment at UC Berkeley.

# References
