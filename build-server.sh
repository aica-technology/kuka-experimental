#!/bin/bash
BASE_IMAGE_TAG=latest

IMAGE_NAME=kuka-experimental
IMAGE_TAG=latest

SERVE_REMOTE=false
REMOTE_SSH_PORT=6666

HELP_MESSAGE="Usage: build-server.sh [-d] [--test] [-r] [-v] [-s]
Options:
  -r, --rebuild          Rebuild the image using the docker
                         --no-cache option.
  -v, --verbose          Use the verbose option during the building
                         process.
  -s, --serve            Start the remove development server.
  -h, --help             Show this help message.
"

BUILD_FLAGS=()

while [[ $# -gt 0 ]]; do
  opt="$1"
  case $opt in
    -r|--rebuild) BUILD_FLAGS+=(--no-cache); shift 1;;
    -v|--verbose) BUILD_FLAGS+=(--progress=plain); shift 1;;
    -s|--serve) SERVE_REMOTE=true; shift;;
    -h|--help) echo "${HELP_MESSAGE}"; exit 0;;
    *) echo "Error in command line parsing" >&2
       echo -e "\n${HELP_MESSAGE}"
       exit 1
  esac
done

BUILD_FLAGS+=(--build-arg BASE_TAG="${BASE_IMAGE_TAG}")
BUILD_FLAGS+=(-t "${IMAGE_NAME}:${IMAGE_TAG}")

docker pull ghcr.io/aica-technology/component-sdk:"${BASE_IMAGE_TAG}" || exit 1
DOCKER_BUILDKIT=1 docker build "${BUILD_FLAGS[@]}" . || exit 1

if [ "${SERVE_REMOTE}" = true ]; then
  aica-docker server "${IMAGE_NAME}:${IMAGE_TAG}" -u ros2 -p "${REMOTE_SSH_PORT}"
fi