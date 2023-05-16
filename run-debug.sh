#!/bin/bash

export FLASK_APP=goodvotes.app
export FLASK_DEBUG=true

# flask create-db --overwrite
flask create-db
flask add-user admin "Armin Admin" Foo123AB
flask run
