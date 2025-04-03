FROM nginx:alpine
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /var/log/nginx
RUN touch /var/log/nginx/access.log /var/log/nginx/error.log /var/log/nginx/proxy_access.log /var/log/nginx/proxy_error.log
RUN chmod 644 /var/log/nginx/*.log

EXPOSE 80
