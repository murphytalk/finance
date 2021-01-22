# https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile
ARG BASE_CONTAINER=jupyter
FROM $BASE_CONTAINER

LABEL maintainer="Mu Lu <murphytalk@gmail.com>"

USER root

RUN apt-get update && apt-get install -yq --no-install-recommends \
    build-essential

COPY requirements.txt .
RUN pip install -r requirements.txt && rm -f requirements.txt
