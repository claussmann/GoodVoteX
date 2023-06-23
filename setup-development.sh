#!/bin/bash

# Downloading files if not present
echo "Checking if external JS and CSS libraries are present..."


SCRIPTPATH="$( cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 || exit ; pwd -P )"


bash "$SCRIPTPATH"/download-static-dependencies.sh "${SCRIPTPATH}/goodvotex/static/external/"


# environment
echo ""

export FLASK_APP=goodvotex
export FLASK_DEBUG=true

mkdir -p storage

if [ -e ".env" ]; then
  printf "loading environment variables... "
  export $(grep "^[^#;]" .env)
  printf "\033[0;32mOK\033[0m\n"
else
  printf "\033[0;31mPlease create a .env file from .env.example\033[0m\n"
  exit 2
fi

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Could not detect an active virtualenv."
    read -p "Create a new virtualenv (c), exit (e) or use system-interpreter/continue (s)? ([e],c,s): " venv_prompt
    case $venv_prompt in
        [s]* )
          echo "Using system interpreter ..."
          ;;
        c )
          echo "Creating new virtualenv (venv) ..."
          cd SCRIPTPATH || exit; python3 -m venv venv
          ;;
        * ) exit
          ;;
    esac
fi

echo "Installing requirements from requirements.txt ..."
pip install -r "$SCRIPTPATH"/requirements.txt

read -p "Start GoodVoteX in development mode now? (y/n)" start_prompt
case $start_prompt in
    y )
      echo "Starting GoodVoteX"
      flask run --port="${GOODVOTEX_PORT}"
      ;;
    n )
      echo "You can start GoodVoteX at any time by exporting the environment variables and running:"
      echo "flask run --port='\${GOODVOTEX_PORT}'"
      ;;
esac

