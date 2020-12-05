# --------------------------
# A simpler Dockerfile
# for development environments.
# --------------------------

FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY ./django_backend /app

# Psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install -r requirements.txt
EXPOSE 8000
