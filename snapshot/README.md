# Snapshot Updater
Scripts to update the community Avro flat files as described at [data.pyafscgap.org](https://data.pyafscgap.org/).

## Purpose
Due to API limitations that prevent filtering joined data prior to downloading locally, community flat files in [Avro format](https://avro.apache.org/) offer pre-joined data with indicies which can be used by `pyafscgap` to avoid downloading all catch data or specifying individual hauls. This directory contains scripts used to update those resources which are availble at [data.pyafscgap.org](https://data.pyafscgap.org/).

## Usage
The updater can be executed with individual scripts or in its entirety through bash. Note that some of these steps use environment variables specified in local setup.

### Python library
These community files are used by default when interacting with the `pyafscgap` library. See [pyafscgap.org](https://pyafscgap.org/) for instructions. These Avro files will be requested and iterated by the client without the user needing to understand the underlying file format. Only the `pyafscgap` interface is intended to be maintained across major versions for backwards compatibility.

### Prebulit payloads
Prebuilt Avro files are avialable via HTTPS through [data.pyafscgap.org](https://data.pyafscgap.org/). There are two subdirectories of files.

First, [index](https://data.pyafscgap.org/index) contains "index data files" which indicate where catch data can be found. These indicies include filename that can be found in `joined`. Each file maps from a value for the filename's variable to a set of joined flat files with those data can be found. Each value refers to a specific haul where floating point values are rounded to two decimal places. Note that, due to this rounding, more precise filters will have to further sub-filter after collecting relevant data from the `joined` subdirectory.

Second, [joined](https://data.pyafscgap.org/joined) includes all catch data joined against the species list and hauls table to create a single "flat" file which fully describes all information available for each catch. Each record is a single catch and each file is a single haul where a haul takes place within a specific year and survey.

Note that, while provided as a service to the community, these Avro files and directory structure may be changed in the future. These files exist to serve the `pyafscgap` functionality as the NOAA APIs change over time. Therefore, for a long term stable interface with documentation and further type annotation, please consider using the `pyafscgap` library isntead.

### Manual execution
In order to build the Avro files yourself by requesting, joining, and indexing original upstream API data, you can simply execute `bash execute_all.sh` after local setup. These will build these files on S3 but they may be deployed to an SFTP server trivially.

## Local setup
Local environment setup varies depending on how these files are used.

### Python library setup
Simply install `pyafscgap` normally to have the library automatically use the flat files for queries.

### Prebuilt payloads environment
These files may be used by any programming language or environment supporting Avro. For more information, see the official [Avro documentation](https://avro.apache.org/docs/) though [fastavro](https://fastavro.readthedocs.io/en/latest/) is recommended for use in Python.

### Environment for manual execution
To perform manual execution, these scripts expect to use [AWS S3](https://aws.amazon.com/s3/) prior to deployment to a simple SFTP server. In order to use these scripts, the following envrionment variables need to be set after installing dependencies (optionally within a virtual environment) via `pip install -r requirements.txt`:

 - `AWS_ACCESS_KEY`: This is the access key used to upload completed payloads to AWS S3 or to request those data as part of distributed indexing and processing.
 - `AWS_ACCESS_SECRET`: This is the secret associated with the access key used to upload completed payloads to AWS S3 or to request those data as part of distributed indexing and processing.
 - `BUCKET_NAME`: This is the name of the bucket where completed uploads should be uploaded or requested within S3.

These may be set within `.bashrc` files or similar through `EXPORT` commands. Finally, these scripts expect [Coiled](https://www.coiled.io/) to perform distributed tasks.

## Testing
Unit tests can be executed by running `nose2` within the `snapshot` directory.

## Deployment
Files generated in S3 can be trivially deployed to an SFTP server or accessed directly from AWS.

## Development
These scripts follow the same development guidelines as the overall `pyafscgap` project. Note that style and type checks are enforced though CI / CD systems. See [contributors documentation](https://github.com/SchmidtDSE/afscgap/blob/main/CONTRIBUTING.md).

## Open source
The snapshots updater uses the following open source packages:

 - [bokeh](https://docs.bokeh.org/en/latest/) from Bokah Contributors and NumFocus under the [BSD License](https://github.com/bokeh/demo.bokeh.org/blob/main/LICENSE.txt).
 - [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) under the [Apache v2 License](https://github.com/boto/boto3/blob/develop/LICENSE).
 - [dask](https://www.dask.org/) from Anaconda and Contributors under the [BSD License](https://github.com/dask/dask/blob/main/LICENSE.txt).
 - [fastavro](https://fastavro.readthedocs.io/en/latest/) by Miki Tebeka and Contributors under the [MIT License](https://github.com/fastavro/fastavro/blob/master/LICENSE).
 - [requests](https://docs.python-requests.org/en/latest/index.html) which is available under the [Apache v2 License](https://github.com/psf/requests/blob/main/LICENSE) from [Kenneth Reitz and other contributors](https://github.com/psf/requests/graphs/contributors).
 - [toolz](https://toolz.readthedocs.io/en/latest/) under a [BSD License](https://github.com/pytoolz/toolz/blob/master/LICENSE.txt).

We thank these projects for their contribution. Note that we also use [coiled](https://www.coiled.io/).

## License
Code to generate these flat files is released alongside the rest of the pyafscgap project under the [BSD License](https://github.com/SchmidtDSE/afscgap/blob/main/LICENSE.md). See [data.pyafscgap.org](https://data.pyafscgap.org/) for further license details regarding prebuilt files.
