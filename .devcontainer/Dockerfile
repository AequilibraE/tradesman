# https://mcr.microsoft.com/en-us/artifact/mar/devcontainers/python/tags

# Python version
FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye

# Install additional OS packages.
RUN apt update -y && apt install -y libsqlite3-mod-spatialite libspatialite-dev pandoc

RUN pip3 install spatialite

RUN ln -s /usr/lib/x86_64-linux-gnu/mod_spatialite.so /usr/lib/x86_64-linux-gnu/mod_spatialite
