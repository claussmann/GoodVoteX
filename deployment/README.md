# How to Deploy GoodVotes

In the following we assume you have cloned this repository, and have docker and docker-compose installed.

## Step 1: Configure Environment Variables

First, you have to create a `.env` file in this directory.
You can use `.env.exampleForProduction` as a template.
Note that configuration for production is usually different from the configuration for development.
Thus, you should not just use the `.env` file from your development configuration.

If you use `.env.exampleForProduction` as a template, you can leave several parts of the configuration unchanged unless you have special requirements in your infrastructure.
However, everyone should change the following parts:

- FLASK_SECRET_KEY must be set to a random string. Keep it secret. You can use the following command to generate a random string: `python -c 'import secrets; print(secrets.token_hex())'`
- FLASK_GOODVOTES_IMPRINT_URL and FLASK_GOODVOTES_PRIVACY_URL must be set to the (static) URL for your imprint and privacy statement.
- GOODVOTES_ADMIN_PASSWORD and GOODVOTES_ADMIN_EMAIL should be set to your needs.

There are a few optional configuration options which are documented in the template.


## Step 2: Let Docker-Compose Do the Rest

Assuming you have configured your `.env` file, and it is in this directory, you can now run the install-script `install.sh` which will first create the necessary directories, copy required files, and then build the docker image.
You will probably need superuser rights to run the script.
If not configured in the `.env` file otherwise, GoodVotes will be installed in `/srv/docker/GoodVotesService`.