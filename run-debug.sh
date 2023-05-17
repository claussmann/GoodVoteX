#!/bin/bash

export FLASK_APP=goodvotes
export FLASK_DEBUG=true

if [ -z "$GOODVOTES_ADMIN_PASSWORD" ]
then
  echo "Please set a password for the admin user: set \$GOODVOTES_ADMIN_PASSWORD."
  exit -1
fi

# exit when initialization fails
set -e

flask goodvotes create-db
flask auth add-user admin "Armin Admin" "${GOODVOTES_ADMIN_EMAIL}" "${GOODVOTES_ADMIN_PASSWORD}"

flask run
