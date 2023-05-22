# GoodVotes
A scientifically approved voting platform for complex preferences.


## Configuration

To configure the application, rename (or copy) `.env.example` to `.env`.
Open the `.env` file in a text editor and edit it according to the instructions in the file.


## Run

For development, simply run the script `run-debug.sh` after configuring the application as described above.

For production, it is better to build and run the docker container.
To this end, run `docker build -t goodvotes .` in the terminal.
After building the image you can start it using `docker run -p 8080:5000 goodvotes` where the `8080` specifies the port on the host where the application in the container becomes available.

Note that you can stop the container by typing `docker container list` into another terminal, and then typing `docker stop abc123` (where abc123 is the container ID you get from the first command).
You can restart the container later by typing `docker restart abc123`.


## Use

The Server will listen on port 8080 in development, or 80 when in the docker container.


## Copyright notice

This software is licensed under the MIT License. It was developed by Christian Laußmann at the Heinrich-Heine-University in Düsseldorf.
The functions of this software are based on the AAMAS-2023 paper "Bounded Approval Ballots: Balancing Expressiveness and Simplicity for Multiwinner Elections" by D. Baumeister, L. Boes, C. Laußmann and S. Rey.

This software contains the jQuery library which is licensed under the MIT License, too.
See the file /goodvotes/static/jquery-3.6.0.min.js for more information.
