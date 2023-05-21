# Build docs
This document provided additional details for building the project from scratch, debugging, and getting started as a contributor.

<br>
<br>

## Local development
After installing dev dependencies (`pip install -e .[dev]`), we recommend the following local checks:

```bash
$ nose2 --start-dir=afscgap
$ mypy afscgap/*.py
$ pyflakes afscgap/*.py
$ pycodestyle afscgap/*.py
```

Note these checks are run by CI / CD. Also, `afscgapviz` has separate tests as described in the [visualization readme](https://github.com/SchmidtDSE/afscgap/blob/main/afscgapviz/README.md).

<br>
<br>

## Community
Thanks for your support! Pull requests and issues very welcome. We invite contributions via [our project Github](https://github.com/SchmidtDSE/afscgap). Please read the [CONTRIBUTING.md](https://github.com/SchmidtDSE/afscgap/blob/main/CONTRIBUTING.md) file for more information.

<br>
<br>

## Debugging
While participating in the community, you may need to debug URL generation. Therefore, for investigating issues or evaluating the underlying operations, you can also request a full URL for a query:

```python
import afscgap

query = afscgap.Query()
query.filter_year(eq=2021)
query.filter_latitude(eq={'$between': [56, 57]})
query.filter_longitude(eq={'$between': [-161, -160]})
results = query.execute()

print(results.get_page_url(limit=10, offset=0))
```

The query can be executed by making an HTTP GET request at the provided location.
