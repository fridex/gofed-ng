FROM fedora:23
MAINTAINER Fridolin Pokorny <fpokorny@redhat.com>

# Service configuration
ENV SERVICE_DOCKER_DIR="/home/service"
ENV SERVICE_NAME="api"
ENV SERVICE_DIR="services/${SERVICE_NAME}"
ENV PYTHONPATH="${SERVICE_DOCKER_DIR}"

# TODO: add requirements for gofedlib, see:
#   https://github.com/gofed/lib/issues/5

# Prepare environment
RUN mkdir ${SERVICE_DOCKER_DIR}
COPY ${SERVICE_DIR}/requirements.txt ${SERVICE_DOCKER_DIR}
RUN dnf install -y python-pip
RUN pip install -r ${SERVICE_DOCKER_DIR}/requirements.txt

# Copy all service files
COPY ${SERVICE_DIR}/gofedlib ${SERVICE_DOCKER_DIR}
COPY ${SERVICE_DIR}/service.py ${SERVICE_DOCKER_DIR}
COPY ${SERVICE_DIR}/service.conf ${SERVICE_DOCKER_DIR}
COPY common ${SERVICE_DOCKER_DIR}/common/

# Run service
ENTRYPOINT PYTHONPATH="/home/service/" \
	python ${SERVICE_DOCKER_DIR}/service.py \
				--config "${SERVICE_DOCKER_DIR}/service.conf"

