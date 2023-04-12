# GoodVotes
A scientifically approved voting platform for complex preferences.

## Run

For development, simply run the script `run-debug.sh` in `Application/Server`.
For production it is better to run the docker container. For this purpose, go to the `Application` folder and run `docker build -t goodvotes .` in the terminal.
After building the image you can start it using `sudo docker run -p 5000:5000 goodvotes` where the first `5000` specifies the port on the host where the application in the container becomes available.

Note that you can stop the container by typing `docker container list` into another terminal, and then typing `docker stop abc123` (where abc123 is the container ID you get from the first command). You can restart the container later by typing `docker restart abc123`.

## Use
The Server will listen on port 5000 (unless you specify another port). An example election is preloaded (search for "Goodmans Pipes and Tubes"), but you can create elections as you like. The evaluation token for the "Goodmans Pipes and Tubes" election is "b074dacd".

## Copyright notice

This software is licensed under the MIT License. It was developed by Christian Laußmann at the Heinrich-Heine-University in Düsseldorf. The functions of this software are based on the AAMAS-2023 paper "Bounded Approval Ballots: Balancing Expressiveness and Simplicity for Multiwinner Elections" by D. Baumeister, L. Boes, C. Laußmann and S. Rey.

This software contains the jQuery library which is licensed under the MIT License, too. See the file /Application/Server/static/jquery-3.6.0.min.js for more information.
