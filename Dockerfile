# Docker file for MyBinder / running example notebooks.
#
# Last tested with afscgap 1.0.0
#
# Thanks https://github.com/binder-examples/minimal-dockerfile
# Used under the unlimited license.

FROM ubuntu:jammy-20230301

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y python-is-python3

# install the notebook package
RUN pip install --no-cache --upgrade pip

# create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

COPY notebooks/requirements.txt /requirements.txt

RUN apt-get -y install libgeos-dev
RUN pip install -r /requirements.txt

ARG NB_USER=nbuser
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
WORKDIR ${HOME}
USER ${USER}

USER root
COPY notebooks/cod.ipynb ${HOME}/index.ipynb
RUN chown -R ${NB_UID} ${HOME}
RUN chgrp -R ${NB_UID} ${HOME}
USER ${NB_USER}
