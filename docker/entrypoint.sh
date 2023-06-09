#!/bin/bash

FLASK_DEBUG=false

HOST_PORT=80
HOST=0.0.0.0


flask goodvotex create-db
flask auth add-user admin "Armin Admin" "${GOODVOTX_ADMIN_EMAIL}" "${GOODVOTEX_ADMIN_PASSWORD}"

waitress-serve --host "${HOST}" --port "${HOST_PORT}" --call goodvotex:create_app