#!/bin/bash

# This script can be used to install goodvotes.


if [ -e ".env" ]; then
  printf "loading environment variables... "
  export $(grep "^[^#;]" .env | xargs)
  printf "\033[0;32mOK\033[0m\n"
else
  printf "\033[0;31mPlease create a .enf file from .env.example\033[0m\n"
  exit 1
fi

# create project dir
echo "Creating install directory [${FLASK_APP_INSTALL_PATH}] ..."
mkdir -p "${FLASK_APP_INSTALL_PATH}"
mkdir "${FLASK_APP_INSTALL_PATH}/storage"

# copy files to project dir
cp .env "${FLASK_APP_INSTALL_PATH}"
cp docker/* "${FLASK_APP_INSTALL_PATH}"
cd ..
cp -r goodvotes "${FLASK_APP_INSTALL_PATH}"
cp -r config "${FLASK_APP_INSTALL_PATH}"
cd "${FLASK_APP_INSTALL_PATH}" || exit 255
rm -rf ./goodvotes/static/external     # External files are downloaded within docker container.

# building docker image
read -p "Build docker image? ([Y]es)?" ASK_BUILD
case "$ASK_BUILD" in
  Yes|yes|y|Y )
    docker-compose -f "${FLASK_APP_INSTALL_PATH}/docker-compose.yml" build
    ;;
  * )
    echo "Skipping build. To build the goodvotes image use 'docker-compose build' within ${FLASK_APP_INSTALL_PATH}"
    exit 1
    ;;
esac

read -p "Start docker container? ([Y]es)?" ASK_BUILD
case "$ASK_BUILD" in
  Yes|yes|y|Y )
    docker-compose -f "${FLASK_APP_INSTALL_PATH}/docker-compose.yml" up -d
    ;;
  * )
    echo "Skipping startup. To start the goodvotes container use 'docker-compose up -d' within ${FLASK_APP_INSTALL_PATH}"
    exit 1
    ;;
esac