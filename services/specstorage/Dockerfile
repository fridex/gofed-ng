FROM fedora:23
MAINTAINER Fridolin Pokorny <fpokorny@redhat.com>

# Service configuration
ENV SERVICE_DOCKER_DIR="/home/service"
ENV SERVICE_NAME="specstorage"
ENV SERVICE_DIR="services/${SERVICE_NAME}"
ENV PYTHONPATH="${SERVICE_DOCKER_DIR}"

# Prepare environment
RUN mkdir ${SERVICE_DOCKER_DIR}
COPY ${SERVICE_DIR}/requirements.txt ${SERVICE_DOCKER_DIR}
RUN dnf install -y python-pip
RUN pip install -r ${SERVICE_DOCKER_DIR}/requirements.txt

# Copy all service files
COPY ${SERVICE_DIR}/service.py ${SERVICE_DOCKER_DIR}
COPY ${SERVICE_DIR}/service.conf ${SERVICE_DOCKER_DIR}
COPY common ${SERVICE_DOCKER_DIR}/common/

ENTRYPOINT PYTHONPATH="/home/service/" \
	python ${SERVICE_DOCKER_DIR}/service.py \
				--config "${SERVICE_DOCKER_DIR}/service.conf"

