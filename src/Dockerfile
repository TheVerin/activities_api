# Pull base image
FROM python:3.7-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create root directory
RUN mkdir /src

# create the appropriate directories
ENV APP_ROOT=/src
WORKDIR $APP_ROOT

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev


# install uwsgi dependencies
RUN apk --update add linux-headers libffi-dev

# copy dependencies
COPY requirements.txt /requirements.txt

# install dependencies
RUN pip install -r /requirements.txt

# copy project
COPY . $APP_ROOT

COPY start.sh $APP_ROOT
