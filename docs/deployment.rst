Production ready deployment
===========================

The recommended deployment for a goodvotex production setup is via docker using an external proxy.
You can use the compose file `docs/examples/docker-compose.yml.traefik` as a starting point for a deplyoment using traefik as reverse proxy.

After configuring it to your needs, simply run `docker-compose up -d`.

**Standalone (no reverse proxy)**

Additionally, we provide a template docker-compose file for deployment without a reverse proxy.
The standalone docker-compose file will bind to port 80 on the host machine by default.
