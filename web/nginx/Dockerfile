# We're using this unpriveledged version to lessen security risks.
# NOTE: The classic nginx image runs as the root user as a default.
FROM nginxinc/nginx-unprivileged:1-alpine
# Temporarily switch to root user
USER root

# Clone configurations.
COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./uwsgi_params /etc/nginx/uwsgi_params


RUN mkdir -p /public/static
RUN chmod 755 /public/static

# Switch back to original user.
USER nginx
