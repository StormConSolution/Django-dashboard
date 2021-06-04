FROM ubuntu
RUN apt update
ENV TZ=Europe/Lisbon
ENV DEBIAN_FRONTEND=noninteractive
RUN  apt install python3 python3-pip nginx postgresql postgresql-contrib libpq-dev -y
WORKDIR /myfolder
COPY ./docker/script.sh /myfolder
COPY ./requirements.txt /myfolder
RUN python3 -m pip install -r requirements.txt
WORKDIR /var/www/
CMD ["bash", "/myfolder/script.sh"]