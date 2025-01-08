# Python Tools for AFSC GAP
| Group | Badges |
|-------|--------|
| Status | ![build workflow status](https://github.com/SchmidtDSE/afscgap/actions/workflows/build.yml/badge.svg?branch=main) ![docs workflow status](https://github.com/SchmidtDSE/afscgap/actions/workflows/docs.yml/badge.svg?branch=main) [![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) |
| Usage | [![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Pypi Badge](https://img.shields.io/pypi/v/afscgap)](https://pypi.org/project/afscgap/) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb) |
| Publication | [![pyOpenSci](https://tinyurl.com/y22nb8up)](https://github.com/pyOpenSci/software-submission/issues/93) [![DOI](https://joss.theoj.org/papers/10.21105/joss.05593/status.svg)](https://doi.org/10.21105/joss.05593) |
| Archive | [![Open in Code Ocean](https://codeocean.com/codeocean-assets/badge/open-in-code-ocean.svg)](https://codeocean.com/capsule/4905407/tree/v2) [![DOI](https://zenodo.org/badge/603308264.svg)](https://zenodo.org/badge/latestdoi/603308264) |

<br>

Python-based tool chain ("Pyafscgap.org") for working with the public bottom trawl data from the [NOAA AFSC GAP](https://www.fisheries.noaa.gov/contact/groundfish-assessment-program). This provides information from multiple survey programs about where certain species were seen and when under what conditions, information useful for research in ocean health.

See [webpage](https://pyafscgap.org), [project Github](https://github.com/SchmidtDSE/afscgap), and [example notebook](https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb).

<br>
<br>

## Quickstart
Taking your first step is easy!

**Explore the data in a UI:** To learn about the datasets, try out an in-browser visual analytics app at [https://app.pyafscgap.org](https://app.pyafscgap.org) without writing any code.

**Try out a tutorial in your browser:** Learn from and modify an in-depth [tutorial notebook](https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb) in a free hosted academic environment (all without installing any local software).

**Jump into code:** Ready to build your own scripts? Here's an example querying for Pacific cod in the Gulf of Alaska for 2021:

```python
import afscgap  # install with pip install afscgap
query = afscgap.Query()
query.filter_year(eq=2021)
query.filter_srvy(eq='GOA')
query.filter_scientific_name(eq='Gadus macrocephalus')
results = query.execute()
```

Continue your exploration in the [developer docs](https://pyafscgap.org/docs/usage/).

<br>
<br>

## Installation
Ready to take it to your own machine? Install the open source tools for accessing the AFSC GAP via Pypi / Pip:

```bash
$ pip install afscgap
```

The library's only dependency is [requests](https://docs.python-requests.org/en/latest/index.html) and [Pandas / numpy are not expected but supported](https://pyafscgap.org/docs/usage/#pandas). The above will install the release version of the library. However, you can also install the development version via:

```bash
$ pip install git+https://github.com/SchmidtDSE/afscgap.git@main
```

Installing directly from the repo provides the "edge" version of the library which should be treated as pre-release.

<br>
<br>

## Purpose
Unofficial Python-based tool set for interacting with [bottom trawl surveys](https://www.fisheries.noaa.gov/alaska/commercial-fishing/alaska-groundfish-bottom-trawl-survey-data) from the [Ground Fish Assessment Program (GAP)](https://www.fisheries.noaa.gov/contact/groundfish-assessment-program). It offers:

 - Pythonic access to the [NOAA AFSC GAP](https://www.fisheries.noaa.gov/foss/f?p=215%3A28) datasets.
 - Tools for inference of the "negative" observations not provided by the API service.
 - Visualization tools for quickly exploring and creating comparisons within the datasets, including for audiences with limited programming experience.

Note that GAP are an excellent collection of datasets produced by the [Resource Assessment and Conservation Engineering (RACE) Division](https://www.fisheries.noaa.gov/about/resource-assessment-and-conservation-engineering-division) of the [Alaska Fisheries Science Center (AFSC)](https://www.fisheries.noaa.gov/about/alaska-fisheries-science-center) as part of the National Oceanic and Atmospheric Administration's Fisheries organization ([NOAA Fisheries](https://www.fisheries.noaa.gov/)).

Please see our [objectives documentation](https://pyafscgap.org/docs/objectives/) for additional information about the purpose, developer needs addressed, and goals of the project.

<br>
<br>

## Usage
This library provides access to the AFSC GAP data with optional zero catch ("absence") record inference.

<br>

### Examples / tutorial
One of the best ways to learn is through our examples / tutorials series. For more details see our [usage guide](https://pyafscgap.org/docs/usage/).

<br>

### API Docs
[Full formalized API documentation is available](https://pyafscgap.org/devdocs/afscgap.html) as generated by pdoc in CI / CD.

<br>

### Data structure
Detailed information about our data structures and their relationship to the data structures found in NOAA's upstream database is available in our [data model documentation](https://pyafscgap.org/docs/model/).

<br>

### Absence vs presence data
By default, the NOAA service will only return information on hauls matching a query. So, for example, requesting data on Pacific cod will only return information on hauls in which Pacific cod is found. This can complicate the calculation of important metrics like catch per unit effort (CPUE). That in mind, one of the most important features in `afscgap` is the ability to infer "zero catch" records as enabled by `set_presence_only(False)`. See more information in [our inference docs](https://pyafscgap.org/docs/inference/).

<br>

### Data quality and completeness
There are a few caveats for working with these data that are important for researchers to understand. These are detailed in our [limitations docs](https://pyafscgap.org/docs/limitations/).

<br>

### Community flat files
The upstream datasets have shifted starting in 2024 with one important change including decomposing the dataset into hauls, catches, and species. Without the ability to join through the API endpoint, the entire catch dataset has to be queried or catches named individually in requests in order to retrieve complete records. Therefore, starting with the `2.x` releases, this library uses pre-joined community Avro files to speed up requests, offering precomputed indicies such that, where available, hauls can be pre-filtered to reduce download payload size and running time. See [flat file documentation](https://data.pyafscgap.org/) for more details about this service.

<br>
<br>

## License
We are happy to make this library available under the BSD 3-Clause license. See LICENSE for more details. (c) 2023 Regents of University of California. See the [Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley](https://dse.berkeley.edu).

<br>
<br>

## Developing
Intersted in contributing to the project or want to bulid manually? Please see our [build docs](https://pyafscgap.org/docs/building/) for details.

<br>
<br>

## People
[Sam Pottinger](https://github.com/sampottinger) is the primary contact with additional development from [Giulia Zarpellon](https://github.com/gizarp). Additionally some acknowledgements:

 - Thank you to [Carl Boettiger](https://github.com/cboettig) and [Fernando Perez](https://github.com/fperez) for advice in the Python library.
 - Thanks also to [Maya Weltman-Fahs](https://dse.berkeley.edu/people/maya-weltman-fahs), [Brookie Guzder-Williams](https://github.com/brookisme), Angela Hayes, David Joy, and [Magali de Bruyn](https://github.com/magalidebruyn) for advice on the visual analytics tool.
 - Lewis Barnett, Emily Markowitz, and Ciera Martinez for general guidance.

This is a project of the [The Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley](https://dse.berkeley.edu) where [Kevin Koy](https://github.com/kevkoy) is Executive Director. Please contact us via dse@berkeley.edu.

<br>
<br>

## Open Source
We are happy to be part of the open source community. We use the following:

 - [Requests](https://docs.python-requests.org/en/latest/index.html) which is available under the [Apache v2 License](https://github.com/psf/requests/blob/main/LICENSE) from [Kenneth Reitz and other contributors](https://github.com/psf/requests/graphs/contributors).
 - [fastavro](https://fastavro.readthedocs.io/en/latest/) by Miki Tebeka and Contributors under the [MIT License](https://github.com/fastavro/fastavro/blob/master/LICENSE).

In addition to Github-provided [Github Actions](https://docs.github.com/en/actions), our build and documentation systems also use the following but are not distributed with or linked to the project itself:

 - [mkdocs](https://www.mkdocs.org) under the [BSD License](https://github.com/mkdocs/mkdocs/blob/master/LICENSE).
 - [mkdocs-windmill](https://github.com/gristlabs/mkdocs-windmill) under the [MIT License](https://github.com/gristlabs/mkdocs-windmill/blob/master/LICENSE).
 - [mypy](https://github.com/python/mypy) under the [MIT License](https://github.com/python/mypy/blob/master/LICENSE) from Jukka Lehtosalo, Dropbox, and other contributors.
 - [nose2](https://docs.nose2.io/en/latest/index.html) under a [BSD license](https://github.com/nose-devs/nose2/blob/main/license.txt) from Jason Pellerin and other contributors.
 - [pdoc](https://github.com/mitmproxy/pdoc) under the [Unlicense license](https://github.com/mitmproxy/pdoc/blob/main/LICENSE) from [Andrew Gallant](https://github.com/BurntSushi) and [Maximilian Hils](https://github.com/mhils).
 - [pycodestyle](https://pycodestyle.pycqa.org/en/latest/) under the [Expat License](https://github.com/PyCQA/pycodestyle/blob/main/LICENSE) from Johann C. Rocholl, Florent Xicluna, and Ian Lee.
 - [pyflakes](https://github.com/PyCQA/pyflakes) under the [MIT License](https://github.com/PyCQA/pyflakes/blob/main/LICENSE) from Divmod, Florent Xicluna, and other contributors.
 - [sftp-action](https://github.com/Creepios/sftp-action) under the [MIT License](https://github.com/Creepios/sftp-action/blob/master/LICENSE) from Niklas Creepios.
 - [ssh-action](https://github.com/appleboy/ssh-action) under the [MIT License](https://github.com/appleboy/ssh-action/blob/master/LICENSE) from Bo-Yi Wu.

Next, the visualization tool has additional dependencies as documented in the [visualization readme](https://github.com/SchmidtDSE/afscgap/blob/main/afscgapviz/README.md). Similarly, the community flat files snapshot updater has additional dependencies as documented in the [snapshot readme](https://github.com/SchmidtDSE/afscgap/blob/main/snapshot/README.md).

Finally, note that the website uses assets from [The Noun Project](thenounproject.com/) under the NounPro plan. If used outside of https://pyafscgap.org, they may be subject to a [different license](https://thenounproject.com/pricing/#icons).

Thank you to all of these projects for their contribution.

<br>
<br>

## Version history
Annotated version history:

 - `2.0.0`: Switch to support new NOAA endpoints.
 - `1.0.4`: Minor documentation fypo fix.
 - `1.0.3`: Documentation edits for journal article.
 - `1.0.2`: Minor documentation touch ups for pyopensci.
 - `1.0.1`: Minor documentation fix.
 - `1.0.0`: Release with pyopensci.
 - `0.0.9`: Fix with issue for certain import modalities and the `http` module.
 - `0.0.8`: New query syntax (builder / chaining) and units conversions.
 - `0.0.7`: Visual analytics tools.
 - `0.0.6`: Performance and size improvements.
 - `0.0.5`: Changes to documentation.
 - `0.0.4`: Negative / zero catch inference.
 - `0.0.3`: Minor updates in documentation.
 - `0.0.2`: License under BSD.
 - `0.0.1`: Initial release.

The community files were last updated on Jan 7, 2025.
