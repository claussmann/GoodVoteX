#!/bin/bash

export FLASK_APP=goodvotes
export FLASK_DEBUG=false

$HOST_PORT=${GOODVOTES_PORT:-5000}
$HOST=${GOODVOTES_HOST:-127.0.0.1}

if [ -z "$GOODVOTES_ADMIN_PASSWORD" ]
then
  echo "Please set a password for the admin user: set \$GOODVOTES_ADMIN_PASSWORD."
  exit -1
fi

# exit when initialization fails
set -e

flask create-db
flask add-user admin "Armin Admin" "${GOODVOTES_ADMIN_EMAIL}" "${GOODVOTES_ADMIN_PASSWORD}"

waitress-serve --host ${HOST} --port "${HOST_PORT}" goodvotes:app