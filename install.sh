#!/bin/bash

# This script can be used to install and configure goodvotes.
# It is still a WIP and subject to change.

create_env_file(){
  read -p "Please provide a host for docker to listen on [0.0.0.0]: " HOST
  read -p "Please provide a port for docker [80]: " PORT
  read -p "Please provide an email for the goodvotes-admin user: " ADMIN_EMAIL
  read -s -p "Please provide a password for the goodvotes-admin user: " ADMIN_PASSWORD
  echo ""
  read -p 'Disable user registration? ([No]|Yes): ' DISABLE_REGISTRATION
  read -p 'Enter the link to your imprint: ' IMPRINT
  read -p 'Enter the link to your privacy statement: ' PRIVACY

  if [[ "$DISABLE_REGISTRATION" =~ ^(Y|Yes|y|yes|)$ ]]; then
    ENABLE_REGISTRATION='False'
  else
    ENABLE_REGISTRATION='True'
  fi

  echo "
FLASK_APP=goodvotes
FLASK_SQLALCHEMY_TRACK_MODIFICATIONS=False
FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex())')
# Optional (overwrite default config from config/config.py)
FLASK_AUTH_ENABLE_REGISTRATION=${ENABLE_REGISTRATION}

FLASK_GOODVOTES_IMPRINT_URL=${IMPRINT}
FLASK_GOODVOTES_PRIVACY_URL=${PRIVACY}

# entrypoint.sh config / docker-compose config
GOODVOTES_ADMIN_PASSWORD=${ADMIN_PASSWORD}
GOODVOTES_ADMIN_EMAIL=${ADMIN_EMAIL}
GOODVOTES_PORT=${PORT:-80}
GOODVOTES_HOST=${HOST:-0.0.0.0}
" > .env

}

# create project dir
PROJECT_BASE_DIR=${GOODVOTES_PROJECT_DIR:-"/srv/docker"}
echo "Creating project directory [${PROJECT_BASE_DIR}] ..."
mkdir -p "${PROJECT_BASE_DIR}"
cd "${PROJECT_BASE_DIR}" || exit 255


PROJECT_DIR='GoodVotes'
# clone current repository
echo "Cloning git repository into [${PROJECT_BASE_DIR}/${PROJECT_DIR}] ..."
git clone https://github.com/claussmann/GoodVotes.git "${PROJECT_DIR}"

cd "${PROJECT_DIR}" || exit 255

read -p "Create new .env file? ([Y]es)?" ASK_CREATE_ENV
case "$ASK_CREATE_ENV" in
  Yes|yes|y|Y)
    create_env_file
    ;;
  * )
    echo "Skipping .env file creation. Please set your configuration manually."
    ;;
esac

# create directory for database file
mkdir storage

if grep -q 'FLASK_DB_RELATIVE_PATH' .env; then
  echo "You have configured a non default path for the database file. Please manually update the docker-compose file before starting the first time."
fi

read -p "Build docker image? ([Y]es)?" ASK_BUILD
case "$ASK_BUILD" in
  Yes|yes|y|Y )
    docker-compose -f "${PROJECT_BASE_DIR}/${PROJECT_DIR}/docker-compose.yml" build
    ;;
  * )
    echo "Skipping build. To build the goodvotes image use 'docker-compose build'"
    exit 1
    ;;
esac

read -p "Start docker container? ([Y]es)?" ASK_BUILD
case "$ASK_BUILD" in
  Yes|yes|y|Y )
    docker-compose -f "${PROJECT_BASE_DIR}/${PROJECT_DIR}/docker-compose.yml" up -d
    ;;
  * )
    echo "Skipping startup. To start the goodvotes container use 'docker-compose up -d'"
    exit 1
    ;;
esac

