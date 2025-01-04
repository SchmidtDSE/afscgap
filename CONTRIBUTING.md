# Contributing
Thank you for your time! This quick doc will help you get started in the `afscgap` project. Looking for a place to get started? See the [bugs tracker](https://github.com/SchmidtDSE/afscgap/issues) to report an issue, ask a question, or look for something that needs help.

<br>
<br>

## Welcome
Thank you for your contribution. We appreciate the community's help in any capacity from filing an issue to opening a pull request. No matter how your contribution shows up, we are happy you are here.

<br>
<br>

## Coding guidelines
In order to ensure the conceptual integrity and readability of our code, we have a few guidelines for Python code under the `afscgap` library itself:

 - Please try to follow the conventions laid out by the project in existing code. In cases of ambiguity, please refer to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) where possible.
 - Tests are encouraged.
 - Type hints are encouraged.
 - Docstrings are encouraged. Please use the [Google-style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) to ensure that our automated documentation system can use your work.
 - Please check that you have no mypy errors when contributing.
 - Please check that you have no linting (pycodestyle, pyflakes) errors when contributing.
 - As contributors may be periodic, please do not re-write history / squash commits for ease of fast forward.
 - Imports should be in alphabetical order in groups of standard library, third-party, and then first party.
 - Imports in the form `from ... import ...` are discouraged except for type hints. They should appear in a logical grouping after other imports.

The `afscgap` library itself requires a very high rigor. For other sections including `afscgapviz`, please ensure that documentation (docstrings, jsdoc, or markdown) is included (again with an 80% target) and, for non-notebook code, Python type hints are included. Testing is encouraged where feasible but an explicit target is not set as it may not be practical for some artifacts like notebooks. That said, note that CI / CD systems run checks in some directories outside the `afscgap` library itself that should be passing for all PRs.

Of course, **do not worry if you aren't sure that you met all of our the guidelines!** We encourage pull requests and are happy to work through any necessary outstanding tasks with you.

Previous versions of this guide indicated specific coverage targets but those are removed for the `2.x` release as the codebase spans more modalities where different approaches may be more appropriate in different areas.

<br>
<br>

## Design choices
There are reasonable differences of opinion in the community about the ideal implementation. That in mind, there are a few opinionated choices we've made in the design of this project that we will maintain moving forward. We encourage folks in our community to open issues if they wish to discuss these design choices further but, at this time, we may not merge pull requests that do not conform to these choices.

<br>

#### Library
Starting with the `afscgap` library itself:

 - It is an explicit goal to provide a class that offers type hints for all record fields for the data returned. See `afscgap.model.Record`.
 - For data structures, getters on an immutable record object are encouraged as to enable use of the type system and docstrings for understanding the data structures. This is important to provide contextual information in IDEs.
 - Object attributes should be private and immutable whenever possible.
 - Object immutable attributes should be prefixed by a single underscore available via getters.
 - We wish to operate with as few dependencies as possible. At this stage, we want to limit that to only the requests library as described in the [README](https://github.com/SchmidtDSE/afscgap/blob/main/README.md).
 - We expect growth in functionality but, to maintain simplicity for end users, we request that developers prefer [composition over inheritance](https://betterprogramming.pub/prefer-composition-over-inheritance-1602d5149ea1) in the form of [decoration over inheritance](https://dzone.com/articles/is-inheritance-dead) to allow for easy addition of transparent behavior.
 - The release to pypi should be free of major static files even if a flat file, contributed application, etc are part of the project.

Please reach out if you have further questions about these guidelines.

<br>

#### Visual analytics tool
Next, for `afscgapviz`:

 - The visual analytics tool is written in vanilla JS + D3. The choice not to use a front-end framework was intentional.
 - The tool must address both programmer and non-programmer audiences.
 - A mixture of JSON and CSV endpoints are used as the later are useful for non-programmer audiences. We are not considering other wiretypes or unification of the wire types to just one of the two currently used.
 - The intro sequence employs [Hayashida-inspired level design](https://www.youtube.com/watch?v=dBmIkEvEBtA) for the intro sequence. Not changing the controls on behalf of the user was intentional.
 - We use CSS and JS which should be usable directly without transpilation or compilation. Language compilation (Elm, SASS, CoffeeScript, etc) including migration to node / npm are not being considered at this time.
 - We do not use CDNs for privacy reasons and CDN migration PRs are discouraged.
 - We are using qunit and grunt for CI / CD.
 - We are using Flask for the `afscgapviz` server.

Note that some PRs may require paired Python and JS code changes.

<br>
<br>

## Scope
There are some limitations of scope for this project that we will enforce:

 - Data structures have been used that could allow for threaded request, but our current objective is to build a solid contribution as a single threaded non-async library. Please reach out if you are interested in building an async version of the library, but it is not currently the focus of project.
 - The visual analytics tool focuses on a sqlite-based usage and, though PRs are welcome to support other backends, all SQL must remain sqlite compatible.

Please open issues with other ideas!

<br>
<br>

## Procedure
By contributing, you attest that you are legally permitted to provide code to the project and agree to release that code under the [project's license](https://github.com/SchmidtDSE/afscgap/blob/main/LICENSE.md). To make a contribution, please:

 - If one is not already open, [open an issue](https://github.com/SchmidtDSE/afscgap/issues).
 - [Open a pull request](https://github.com/SchmidtDSE/afscgap/pulls).
 - Mark the pull request as draft until you pass checks and are ready for review.
 - Indicate that your pull request closes your issue by saying "closes #" followed by your issue number in the PR description.
 - At-mention [sampottinger](https://github.com/sampottinger) in your PR to be assigned a reviewer.

If you would like to contribute code but don't have a specific issue to address, thank you! Please reach out to dse@berkeley.edu.

<br>
<br>

## Standardization
Note that, at this stage, we do not have an issue template as we let our community form its practices and norms organically. However, participants agree that a template may be added in the future. We may, however, ask you to add additional detail to your issues or PRs to ensure appropriate documentation for the community.

<br>
<br>

## Parting thoughts
Open source is an act of love. Please be kind and respectful of all contributors. For more information, please see the [CONDUCT.md](https://github.com/SchmidtDSE/afscgap/blob/main/CONDUCT.md) file for our Code of Conduct.
