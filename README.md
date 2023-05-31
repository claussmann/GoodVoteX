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
Finally, you can run the script `run-development.sh`, and access the app in your web browser under `http://127.0.0.1:5000`.

Note that python3, pypy3, and the dependencies from `requirements.txt` need to be installed.

### Production

Production deployment works via docker-compose.
Detailed instructions can be found in the directory `deployment`.


## Copyright notice

This software is licensed under the MIT License. It was developed in 2022 and 2023 by Christian Laußmann and Paul Nüsken at the Heinrich-Heine-University in Düsseldorf.
