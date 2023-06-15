
SCRIPTPATH="$( cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 || exit ; pwd -P )"
TARGET=${TARGET:-"$SCRIPTPATH"/goodvotex/static/external/}


mkdir -p "${TARGET}"
echo "Downloading bootstrap.min.css"
sha_from_website=KK94CHFLLe+nY2dmCWGMq91rCGa5gtU4mk92HdvYe+M/SXH301p5ILy+dN9+nJOZ
convertedHex=$(echo "$sha_from_website" | base64 -d | hexdump -e '/1 "%02X"')
wget --quiet https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css

if echo "$convertedHex  bootstrap.min.css" | sha384sum --check - > /dev/null; then
  printf "bootstrap.min.css: \033[0;32mChecksum OK\033[0m\n"
  mv bootstrap.min.css "${TARGET}"
else
  rm bootstrap.min.css
  printf "\033[0;31mFailed to validate checksum for bootstrap.min.css\033[0m\n"
  exit 1
fi


echo "Downloading bootstrap.bundle.min.js"
sha_from_website=ENjdO4Dr2bkBIFxQpeoTz1HIcje39Wm4jDKdf19U8gI4ddQ3GYNS7NTKfAdVQSZe
convertedHex=$(echo "$sha_from_website" | base64 -d | hexdump -e '/1 "%02X"')
wget --quiet https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js
echo "$convertedHex  bootstrap.bundle.min.js" | sha384sum --check - > /dev/null
if [ $? -eq 0 ]; then
  printf "bootstrap.bundle.min.js: \033[0;32mChecksum OK\033[0m\n"
  mv bootstrap.bundle.min.js "${TARGET}"
else
  rm bootstrap.bundle.min.js
  printf "\033[0;31mFailed to validate checksum for bootstrap.bundle.min.js\033[0m\n"
  exit 1
fi


echo "Downloading jquery-3.7.0.min.js"
sha_from_website=2Pmvv0kuTBOenSvLm6bvfBSSHrUJ+3A7x6P5Ebd07/g=
convertedHex=$(echo "$sha_from_website" | base64 -d | hexdump -e '/1 "%02X"')
wget --quiet https://code.jquery.com/jquery-3.7.0.min.js
echo "$convertedHex  jquery-3.7.0.min.js" | sha256sum --check - > /dev/null
if [ $? -eq 0 ]; then
    printf "jquery-3.7.0.min.js: \033[0;32mChecksum OK\033[0m\n"
    mv jquery-3.7.0.min.js "${TARGET}"
else
    rm jquery-3.7.0.min.js
    printf "\033[0;31mFailed to validate checksum for jquery-3.7.0.min.js\033[0m\n"
    exit 1
fi
