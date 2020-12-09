# --------------------------
# A simpler Dockerfile
# for development environments.
# --------------------------

FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY ./web/django_backend /app

# Psycopg2 dependencies
RUN apk add --update --no-cache --virtual .tmp postgresql-dev gcc python3-dev musl-dev

# Install application dependencies
RUN pip install -r requirements.txt

EXPOSE 8000
