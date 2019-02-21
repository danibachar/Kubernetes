FROM python:3.5.3
MAINTAINER Daniel Bachar <daniel@gmail.cat>

RUN mkdir -p /usr/src/hpa
WORKDIR /usr/src/hpa

# Installign requirements
COPY ./hpa/requirements.txt ./hpa/requirements.txt
RUN pip3 install --no-cache-dir -r ./hpa/requirements.txt

# Microservices code copy
COPY ./hpa /usr/src/hpa

WORKDIR /usr/src
RUN chmod -R 777 /usr/src/hpa
# For local testing
EXPOSE 80
CMD ["python", "./hpa/app.py"]
