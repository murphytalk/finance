FROM python:3.9.6-slim-buster
LABEL com.centurylinklabs.watchtower.enable="false"
RUN mkdir /app
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["/finance/sbin/docker-run.sh"]
