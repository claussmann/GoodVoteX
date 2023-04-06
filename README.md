# GoodVotes
A scientifically approved voting platform for complex preferences.

# Please Note:
This application is only tested with the Chrome browser family. In particular, we are currently working on a fix for Firefox. It seems that firefox is not supporting our drag-and-drop functions.


## Run

For development, simply run the script `run-debug.sh` in `Application/Server`.
For production it is better to run the docker container. For this purpose, go to the `Application` folder and run `docker build -t goodvotes .` in the terminal.
After building the image you can start it using `sudo docker run -p 5000:5000 goodvotes` where the first `5000` specifies the port on the host where the application in the container becomes available.

Note that you can stop the container by typing `docker container list` into another terminal, and then typing `docker stop abc123` (where abc123 is the container ID you get from the first command). You can restart the container later by typing `docker restart abc123`.

## Use
The Server will listen on port 5000 (unless you specify an other port). An example election is preloaded (search for "Goodmans Pipes and Tubes"), but you can create elections as you like. The evaluation token for the "Goodmans Pipes and Tubes" election is "b074dacd".
