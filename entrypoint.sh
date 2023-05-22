#!/bin/bash

FLASK_DEBUG=false

HOST_PORT=80
HOST=0.0.0.0

if [ -z "$GOODVOTES_ADMIN_PASSWORD" ]
then
  echo "Please set a password for the admin user: set \$GOODVOTES_ADMIN_PASSWORD."
  exit -1
fi

# exit when initialization fails
set -e

flask goodvotes create-db
flask auth add-user admin "Armin Admin" "${GOODVOTES_ADMIN_EMAIL}" "${GOODVOTES_ADMIN_PASSWORD}"

waitress-serve --host "${HOST}" --port "${HOST_PORT}" --call goodvotes:create_app