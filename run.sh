#!/bin/bash

export FLASK_APP=goodvotes.app
export FLASK_DEBUG=false

flask create-db --overwrite
flask add-user admin "Armin Admin" Foo123AB
waitress-serve --host 0.0.0.0 --port 5000 goodvotes.app:app