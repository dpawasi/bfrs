# Dockerfile to build BFRS application images.
# Prepare the base environment.
FROM dbcawa/ubuntu:18.04-latexmk as builder_base_bfrs
MAINTAINER asi@dbca.wa.gov.au
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y \
  && apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin \
  python python-setuptools python-dev python-pip tzdata \
  && pip install --upgrade pip

ENV TZ=Australia/Perth

# Install Python libs from requirements.txt.
FROM builder_base_bfrs as python_libs_bfrs
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
  # Update the Django <1.11 bug in django/contrib/gis/geos/libgeos.py
  # Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
  && sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" /usr/local/lib/python2.7/dist-packages/django/contrib/gis/geos/libgeos.py \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_bfrs
COPY gunicorn.ini manage.py ./
COPY bfrs ./bfrs
COPY bfrs_project ./bfrs_project
COPY templates ./templates
# NOTE: we can't currently run the collectstatic step due to how BFRS is written.
# Always be sure to run collectstatic locally prior to building the image.
COPY .env ./.env
RUN python manage.py collectstatic --noinput
RUN rm .env

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["gunicorn", "bfrs_project.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]
