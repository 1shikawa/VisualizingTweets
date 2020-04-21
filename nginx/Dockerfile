FROM nginx
# COPY ./nginx.conf /etc/nginx
RUN rm /etc/nginx/conf.d/django_nginx.conf
COPY ./nginx.conf /etc/nginx/conf.d
COPY ./mime.types /etc/nginx


