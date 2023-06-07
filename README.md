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

For development, you first need to add the configuration.
To this end, add a file `.env` to the root of this repository.
You can use the example in `docs/examples/.env.example` as a template.
After adding the configuration, you can run the script `run-development.sh`, and access the app in your web browser under `http://127.0.0.1:5000`.

Note that python3, pypy3, and the dependencies from `requirements.txt` need to be installed.

### Production

Production deployment works via docker-compose.
You can use the compose file `docs/examples/docker-compose.yml.example` as a template.
After configuring it to your needs, simply run `docker-compose -f PATH_TO_DOCKER_COMPOSE_FILE up -d`.

### Building a Docker Container From Source

Run `docker build . -f docker/Dockerfile --tag goodvotes` from the root of the repository.


## Contribute

We welcome everyone who wants to add ballot formats.

First, think of a good name for your ballot format.
Let's assume you want to call the ballot `Simple Ballot`.
Next, in the file `goodvotes/voting/models.py` you create a class `SimpleBallot` which inherits from the class `Ballot`.
Note that you have to overwrite the following methods:

- `score(self, committee)`: Returns the score `committee` receives from this ballot.
- `check_validity(self)`: Returns `True` if and only if this ballot is valid (OPTIONAL; as a default every ballot is considered valid).
- `is_of_type(self, ballot_type)`: Returns `True` if and only if this ballot is of type `ballot_type`, which is a string.
- `parse_from_json(self, json)`: This function is called immediately after construction. It is given a dict in a JSON like structure. The format of this dict is defined by you when you write the HTML/JS form later.
- `get_involved_candidates(self)`: Returns a set of all involved candidates in this ballot.

Further, your class must have the following database attributes:


    id: Mapped[int] = mapped_column(ForeignKey("ballot.id"), primary_key=True)
    json_encoded = db.Column(db.String(1000), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "simpleBallot",
    }

Of course, you replace `simpleBallot` by the name of your ballot.

Next, go to the file `goodvotes/voting/service.py` and find the function `add_vote_from_json` where you add your instructions for `simpleBallot`.

Finally, you have to create an HTML template for your ballot format.
Place it in `goodvotes/voting/templates` and name it `vote_simpleBallot.html`.
You can do whatever you want in this template.
However, eventually you must POST a JSON formatted object to the URL `/vote/{{election.id}}`.
You can format it as you like, as you will evaluate it on your own in the function `parse_from_json(self, json)`.
The only requirement is that it has an attribute `type` with the value `"simpleBallot"`, as this is used to figure out which ballot object should be created.

Now, your new ballot type is registered in the system.
However, if you want to create an election with this ballot type, you have to add this option in the file `goodvotes/voting/templates/start.html` in the select-form with id `ballot_type`.
That's it.


## Copyright notice

This software is licensed under the MIT License. It was developed in 2022 and 2023 by Christian Laußmann and Paul Nüsken at the Heinrich-Heine-University in Düsseldorf.
