FROM python:3.8-alpine

ENV PATH="/install_scripts:${PATH}"

COPY ./django_backend/requirements.txt /requirements.txt

# C dependencies. Placed in tmp since these are only required
# when installing our python packages.
RUN apk add --update --no-cache --virtual .tmp \
    gcc libc-dev linux-headers

# Install python packages
RUN pip install -r /requirements.txt

# Remove virtual set of requirements for lighter containers.
RUN apk del .tmp

# Clone files.
RUN mkdir /app
COPY ./django_backend /app
WORKDIR /app
COPY ./install_scripts /install_scripts

# Enable public access for all users in the container
RUN chmod +x /install_scripts/*

# Setup media and statics
RUN mkdir -p /public/web/media
RUN mkdir -p /public/web/

# Lessen priveledges of current user to minimize security risks
RUN adduser -D user
RUN chown -R  user:user /public
RUN chown -R  user:user /app/public
RUN chmod -R 755 /public/web
USER user

CMD ["entrypoint.sh"]
