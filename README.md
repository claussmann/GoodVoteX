# GoodVotes
A scientifically approved voting platform for complex preferences.


## Configuration

To configure the application, rename (or copy) `.env.example` to `.env`.
Open the `.env` file in a text editor and edit it according to the instructions in the file.


## Run

For development, simply run the script `run-debug.sh` after configuring the application as described above, with env vars exported e.g. `env $(cat .env|xargs) ./run-debug.sh`.

For production, it is better to build and run the docker container.
To deploy GoodVotes using docker download and run the (https://github.com/claussmann/GoodVotes/blob/main/install.sh)[install.sh] script provided by the repository.
The `install.sh` default project directory is `/srv/docker`. To change this set `GOODVOTES_PROJECT_DIR` to a path of your choosing.

`GOODVOTES_PROJECT_DIR=/home/goodvotes ./install.sh`

Once installed the `docker-compose.yml` file can be found in `$GOODVOTES_PROJECT_DIR/GoodVotes/`.

Configuration changes can be applied to `$GOODVOTES_PROJECT_DIR/GoodVotes/.env`


## Use

The Server will listen on port 8080 in development, or 80 when in the docker container.


## Copyright notice

This software is licensed under the MIT License. It was developed by Christian Laußmann at the Heinrich-Heine-University in Düsseldorf.
The functions of this software are based on the AAMAS-2023 paper "Bounded Approval Ballots: Balancing Expressiveness and Simplicity for Multiwinner Elections" by D. Baumeister, L. Boes, C. Laußmann and S. Rey.

This software contains the jQuery library which is licensed under the MIT License, too.
See the file /goodvotes/static/jquery-3.6.0.min.js for more information.
