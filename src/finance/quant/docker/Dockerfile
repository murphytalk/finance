# https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile
ARG BASE_CONTAINER=lalopey/zipline-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Mu Lu <murphytalk@gmail.com>"

USER root

COPY requirements.txt .
RUN pip install -r requirements.txt && rm -f requirements.txt
