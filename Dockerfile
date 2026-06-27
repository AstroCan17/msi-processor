# Copyright 2026 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This Dockerfile relies on Docker's multi-stage build feature:
# https://docs.docker.com/build/building/multi-stage/
#
# Currently, there is a known problem with pre-stages not being cached.
# See this link for more information: https://snyk.io/blog/best-practices-containerizing-python-docker/
# and the section "Known issues with multi-stage builds for containerized Python applications".
#
# Thus, please run the following commands to build the image:
#
#   export DOCKER_BUILDKIT=1
#   export BUILDKIT_PROGRESS=plain
#   docker build -t cpm:multi-stage --cache-from cpm:multi-stage --build-arg BUILDKIT_INLINE_CACHE=1 .

# Build stage
FROM python:3.11.7-bullseye as build

# Define the CPM package registry to be able to install the CPM package.
#
# Please use read-only tokens to access the GitLab package registries.
ENV PIP_EXTRA_INDEX_URL "https://eopf:LXMYBdDVhRqNqMSB1Rn8@gitlab.eopf.copernicus.eu/api/v4/projects/14/packages/pypi/simple"

# Install msi_processor from source.
#
# This solution has been chosen to allow building an image for the latest state
# of the "main" branch without previously uploading a fixed version of the
# corresponding Python package into the package registry,
# thus simplifying the testing of the "main" branch.
COPY . /opt/msi_processor
# Skip the "bin not on PATH" warning: This is only a build container.
RUN pip install --user --no-cache-dir --no-warn-script-location /opt/msi_processor[cluster-plugin]

# Final stage
#
# Use the EOPF Dask image as the base of the Dask runtime environment.
# The 'latest' tag is used by the template to test the current version.
# Moreover, the usage of the 'latest' tag causes a warning to be raised by
# the docker-linter CI job.
# However, user projects are encouraged to fix the version of the base image.
FROM registry.eopf.copernicus.eu/sde/dask-container-images/dask-scheduler-worker:latest

# OCI annotations
# See https://github.com/opencontainers/image-spec/blob/main/annotations.md#pre-defined-annotation-keys
ARG CI_COMMIT_SHA
LABEL org.opencontainers.image.title="msi-processor Dask runtime"
LABEL org.opencontainers.image.description="Dask runtime environment including the msi-processor"
LABEL org.opencontainers.image.source="https://gitlab.eopf.copernicus.eu/ipf/msi-processor/"
LABEL org.opencontainers.image.url="https://gitlab.eopf.copernicus.eu/ipf/msi-processor/-/blob/main/Dockerfile"
LABEL org.opencontainers.image.revision="$CI_COMMIT_SHA"
LABEL org.opencontainers.image.vendor="ESA"
LABEL org.opencontainers.image.authors="AstroCan17"
LABEL org.opencontainers.image.base.name="registry.eopf.copernicus.eu/sde/dask-container-images/dask-scheduler-worker:latest"

# Copy all installed Python packages into the final image
COPY --from=build --chown=dask:dask /root/.local /home/dask/.local/
