#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 || exit ; pwd -P )"
export FLASK_APP=goodvotex
export FLASK_DEBUG=true




# Downloading external files if not present
printf "\033[0;34mChecking if external JS and CSS libraries are present...\033[0m\n"
if test -f "goodvotex/static/external/bootstrap.min.css"; then
    echo "External resources are present."
else
  echo "Downloading external resources..."
  bash "$SCRIPTPATH"/download-static-dependencies.sh "${SCRIPTPATH}/goodvotex/static/external/"
fi
echo ""



# Checking if .env is present; loading it.
printf "\033[0;34mloading environment variables...\033[0m\n"
if [ -e ".env" ]; then
  export $(grep "^[^#;]" .env)
  printf "\033[0;32mOK\033[0m\n"
else
  printf "\033[0;31mPlease create a .env file from .env.example\033[0m\n"
  exit 2
fi
echo ""


# Installing virtual env
printf "\033[0;34mInstalling Virtual Environment\033[0m\n"
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Could not detect an active virtualenv."
    read -p "Create a new virtualenv (c), exit (e) or use system-interpreter/continue (s)? ([e],c,s): " venv_prompt
    case $venv_prompt in
        s )
          echo "Using system interpreter ..."
          ;;
        c )
          echo "Creating new virtualenv (venv) ..."
          cd "$SCRIPTPATH" || exit; python3 -m venv venv
          source venv/bin/activate
          ;;
        * ) 
          exit
          ;;
    esac
fi
echo ""



# Installing dependencies
printf "\033[0;34mChecking Dependencies...\033[0m\n"
read -p "Install Dependencies? (y/[n])" req_prompt
case $req_prompt in
    y )
      echo "Installing requirements from requirements.txt ..."
      pip install -r "$SCRIPTPATH"/requirements.txt
      ;;
    * )
      echo "Requirements can be found in requirements.txt"
      ;;
esac
echo ""


# Creating Database
printf "\033[0;34mChecking Database...\033[0m\n"
mkdir -p storage
if test -f "storage/database.db"; then
    echo "Database exists."
else
  read -p "It seems there is no database. Create Database? (y/[n])" db_prompt
  case $db_prompt in
      y )
        echo "Creating Database ..."
        flask goodvotex create-db
        flask auth add-user admin "Armin Admin" "${GOODVOTEX_ADMIN_EMAIL}" "${GOODVOTEX_ADMIN_PASSWORD}"
        ;;
      * )
        echo "You must create a database before starting the application."
        exit
        ;;
  esac
fi
echo ""


# Start App
printf "\033[0;34mStarting App...\033[0m\n"
read -p "Start GoodVoteX in development mode now? (y/[n])" start_prompt
case $start_prompt in
    y )
      echo "Starting GoodVoteX"
      flask run --port="${GOODVOTEX_PORT}"
      ;;
    * )
      echo "You can start GoodVoteX at any time by exporting the environment variables and running:"
      echo "flask run --port='\${GOODVOTEX_PORT}'"
      ;;
esac

