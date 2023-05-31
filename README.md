# GoodVotes

GoodVotes allows you to conduct elections with a variety of ballot types and voting rules.
All voting procedures used have a scientific background.
That is, their properties have been studied e.g. in Computational Social Choice literature.
Thus, the platform allows you to choose a suitable voting rule and ballot format for your election.

We currently support the following ballot types and voting rules:

| Ballot Type                         | Available Voting Rules | Reference                                                                                                                                                   |
|-------------------------------------|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Bounded approval ballots (disjoint) | Total Scoring          | AAMAS-2023: "Bounded Approval Ballots: Balancing Expressiveness and Simplicity for Multiwinner Elections" by D. Baumeister, L. Boes, C. Laußmann and S. Rey |
| Approval ballots | Approval          | - |


## Run

You basically have two options to run the application.
You can run it in development mode, or in production mode.
The development mode runs the application with debugging features such as hot reloading.
However, this mode should only be used for development on your own machine.
For production, the application will run in a docker container with a production WSGI server.

### Development

For development, you first need to edit the configuration.
To this end, rename (or copy) `.env.example` to `.env`.
Open the `.env` file in a text editor and edit it according to the instructions in the file.
Finally, you can run the script `run-debug.sh`, with env vars exported e.g. `env $(cat .env|xargs) ./run-debug.sh`.

### Production

To deploy GoodVotes using docker download and run the [install.sh](https://raw.githubusercontent.com/claussmann/GoodVotes/main/install.sh) script provided by the repository.

The following dependencies are required: `docker`, `docker-compose`, `python3`

The `install.sh` default project directory is `/srv/docker`. To change this set `GOODVOTES_PROJECT_DIR` to a path of your choosing.

`GOODVOTES_PROJECT_DIR=/home/goodvotes ./install.sh`

Once installed, the `docker-compose.yml` file can be found in `$GOODVOTES_PROJECT_DIR/GoodVotes/`.
The installer will ask you whether you want to build and start the docker container right now.
Note that you will (depending on your system configuration) need root permissions to do this.
Thus, in case the installer fails to build and start the container, you can later build it by running

`sudo docker-compose -f "$GOODVOTES_PROJECT_DIR/GoodVotes/docker-compose.yml" build`

and start it by running

`sudo docker-compose -f "$GOODVOTES_PROJECT_DIR/GoodVotes/docker-compose.yml" up -d`

Configuration changes can be applied to `$GOODVOTES_PROJECT_DIR/GoodVotes/.env`.
However, you will need to restart the container afterwards.


## Use

The Server will listen on port 5000 in development, or 80 when in the docker container.
Open the URL (e.g. `http://127.0.0.1:5000` for development) in a web browser and start using the application.


## Copyright notice

This software is licensed under the MIT License. It was developed in 2022 and 2023 by Christian Laußmann and Paul Nüsken at the Heinrich-Heine-University in Düsseldorf.

This software contains the jQuery library which is licensed under the MIT License, too.
See the file /goodvotes/static/jquery-3.6.0.min.js for more information.
