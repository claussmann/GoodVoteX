#!/bin/bash

# Downloading files if not present
echo "Checking if external JS and CSS libraries are present..."

mkdir -p ./goodvotex/static/external/

if [ -e "./goodvotex/static/external/bootstrap.min.css" ]
then
  echo "bootstrap.min.css exists"
else
  echo "bootstrap.min.css is missing. Downloading..."
  sha_from_website=KK94CHFLLe+nY2dmCWGMq91rCGa5gtU4mk92HdvYe+M/SXH301p5ILy+dN9+nJOZ
  convertedHex=$(echo "$sha_from_website" | base64 --decode | hexdump -e '/1 "%02X"')

  wget --quiet https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css
  echo "$convertedHex  bootstrap.min.css" | sha384sum --check - > /dev/null

  if [ $? -eq 0 ]; then
    printf "bootstrap.min.css: \033[0;32mChecksum OK\033[0m\n"
    mv bootstrap.min.css ./goodvotex/static/external/
  else
    printf "\033[0;31mFailed to validate checksum for bootstrap.min.css\033[0m\n"
    exit 1
  fi
fi

if [ -e "./goodvotex/static/external/bootstrap.bundle.min.js" ]
then
  echo "bootstrap.bundle.min.js exists"
else
  echo "bootstrap.bundle.min.js is missing. Downloading..."
  sha_from_website=ENjdO4Dr2bkBIFxQpeoTz1HIcje39Wm4jDKdf19U8gI4ddQ3GYNS7NTKfAdVQSZe
  convertedHex=$(echo "$sha_from_website" | base64 --decode | hexdump -e '/1 "%02X"')

  wget --quiet https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js
  echo "$convertedHex  bootstrap.bundle.min.js" | sha384sum --check - > /dev/null

  if [ $? -eq 0 ]; then
    printf "bootstrap.bundle.min.js: \033[0;32mChecksum OK\033[0m\n"
    mv bootstrap.bundle.min.js ./goodvotex/static/external/
  else
    printf "\033[0;31mFailed to validate checksum for bootstrap.bundle.min.js\033[0m\n"
    exit 1
  fi
fi

if [ -e "./goodvotex/static/external/jquery-3.7.0.min.js" ]
then
  echo "jquery-3.7.0.min.js exists"
else
  echo "jquery-3.7.0.min.js is missing. Downloading..."
  sha_from_website=2Pmvv0kuTBOenSvLm6bvfBSSHrUJ+3A7x6P5Ebd07/g=
  convertedHex=$(echo "$sha_from_website" | base64 --decode | hexdump -e '/1 "%02X"')

  wget --quiet https://code.jquery.com/jquery-3.7.0.min.js
  echo "$convertedHex  jquery-3.7.0.min.js" | sha256sum --check - > /dev/null

  if [ $? -eq 0 ]; then
      printf "jquery-3.7.0.min.js: \033[0;32mChecksum OK\033[0m\n"
      mv jquery-3.7.0.min.js ./goodvotex/static/external/
  else
      printf "\033[0;31mFailed to validate checksum for jquery-3.7.0.min.js\033[0m\n"
      exit 1
  fi
fi


# environment
echo ""

export FLASK_APP=goodvotex
export FLASK_DEBUG=true

mkdir storage

if [ -e ".env" ]; then
  printf "loading environment variables... "
  export $(grep "^[^#;]" .env | xargs)
  printf "\033[0;32mOK\033[0m\n"
else
  printf "\033[0;31mPlease create a .enf file from .env.example\033[0m\n"
  exit 2
fi

# start app
echo ""
echo "Starting App"

flask goodvotex create-db
flask auth add-user admin "Armin Admin" "${GOODVOTEX_ADMIN_EMAIL}" "${GOODVOTEX_ADMIN_PASSWORD}"

flask run
