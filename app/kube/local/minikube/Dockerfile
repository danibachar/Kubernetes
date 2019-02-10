FROM python:3.5.3
MAINTAINER Daniel Bachar <daniel@gmail.com>

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Installign requirements
COPY ./app/requirements.txt ./app/requirements.txt
RUN pip3 install --no-cache-dir -r ./app/requirements.txt

# Microservices code copy
COPY ./app /usr/src/app
RUN mkdir config
COPY ./config /usr/src/config

WORKDIR /usr/src
RUN chmod -R 777 /usr/src/app
# For local testing
EXPOSE 80
CMD ["python", "./app/app.py"]
