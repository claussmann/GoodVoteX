# GoodVoteX

GoodVoteX allows you to conduct elections with a variety of ballot types and voting rules.
All voting procedures used have a scientific background.
That is, their properties have been studied e.g. in Computational Social Choice literature.
Thus, the platform allows you to choose a suitable voting rule and ballot format for your election.

We currently support the following ballot types and voting rules:

| Ballot Type                         | Available Voting Rules | Reference                                                                                                                                                   |
|-------------------------------------|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Bounded approval ballots (disjoint) | Total Scoring          | AAMAS-2023: "Bounded Approval Ballots: Balancing Expressiveness and Simplicity for Multiwinner Elections" by D. Baumeister, L. Boes, C. Laußmann and S. Rey |
| Approval ballots                    | Approval               | -                                                                                                                                                           |

## Run

You basically have two options to run the application.
You can run it in development mode, or in production mode.
The development mode runs the application with debugging features such as hot reloading.
However, this mode should only be used for development on your own machine.
For production, the application will run in a docker container with a production WSGI server (see `docs/deployment.rst`).

### Development

For development, you first need to add the configuration.
To this end, add a file `.env` to the root of this repository.
You can use `.env.example` as a template.

There are two possibilities for local development:

1) `docker-compose` ,
2) a local python interpreter running flask.

To ease the first setup we provide a `setup-development.sh` script, which

* creates all necessary directories,
* downloads external assets,
* installs python package requirements (and creates a venv if wanted).

This is mainly used when using a local python interpreter or docker-compose with change detection.

#### External Assets

GoodVotesX uses Bootstrap and JQuery.
The docker image downloads these during the build.
During local development you may need to download the files yourselves.
For this we provide `.\download-static-dependencies.sh`.
Note that this will download from third party locations such as e.g. jsdelivr.
However, checksums are checked for all files.

#### docker-compose ()

After setting up the configuration, simply run `docker-compose up`.

Executing flask cli commands can be done via `docker-compose exec goodvotex-webservice CMD`.

Rebuilding the container can be achieved by using `docker-compose build`.

**Change detection and auto-reloading**

The provided docker-compose file is configured to support flask change detection and auto-reloading.
For this to work we mapped the `goodvotex` as a volume.
Please make sure, that you have downloaded the necessary external assets.
It also requires a different entrypoint as the production image.
```yaml
services:
 webserver:
  # [...]
  entrypoint: sh -c 'flask goodvotex create-db; flask auth add-user admin "Armin Admin" "${GOODVOTEX_ADMIN_EMAIL}" "${GOODVOTEX_AMIN_PASSWORD}"; flask run --host=0.0.0.0 --port=80 --debug;'
```
__
If you want to stay as close to production as possible, simply comment the following lines in the docker-compose file:

* `- ./goodvotex:/App/goodvotex`
* `entrypoint: sh -c 'flask goodvotex create-db; flask auth add-user admin "Armin Admin" "${GOODVOTEX_ADMIN_EMAIL}" "${GOODVOTEX_AMIN_PASSWORD}"; flask run --host=0.0.0.0 --port=80 --debug;'`

#### local interpreter

Running goodvotex locally requires the full setup as explained above (use setup-development.sh).

Afterwards run:

```bash
#activate venv
source venv/bin/activate

# read ENV vars from file.
export $(grep "^[^#;]" .env | xargs)

# Setup app for before first usage
flask goodvotex create-db
flask auth add-user admin "Armin Admin" "${GOODVOTEX_ADMIN_EMAIL}" "${GOODVOTEX_ADMIN_PASSWORD}"

# Run flask debug server
flask run --port="${GOODVOTEX_PORT}" --debug
```

### Building a Docker Container From Source

Run `docker build . -f docker/Dockerfile --tag goodvotex` from the root of the repository.
Make sure your docker-compose file (if applicable) matches the new tag.

## Contribute

We welcome everyone who wants to add ballot formats.

First, think of a good name for your ballot format.
Let's assume you want to call the ballot `Simple Ballot`.
Next, in the file `goodvotex/voting/models.py` you create a class `SimpleBallot` which inherits from the class `Ballot`.
Note that you have to overwrite the following methods:

- `score(self, committee)`: Returns the score `committee` receives from this ballot.
- `check_validity(self)`: Returns `True` if and only if this ballot is valid (OPTIONAL; as a default every ballot is considered valid).
- `is_of_type(self, ballot_type)`: Returns `True` if and only if this ballot is of type `ballot_type`, which is a string.
- `parse_from_json(self, json)`: This function is called immediately after construction. 
 It is given a dict in a JSON like structure. 
 The format of this dict is defined by you when you write the HTML/JS form later.
- `get_involved_candidates(self)`: Returns a set of all involved candidates in this ballot.

Further, your class must have the following database attributes:

    id: Mapped[int] = mapped_column(ForeignKey("ballot.id"), primary_key=True)
    json_encoded = db.Column(db.String(1000), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "simpleBallot",
    }

Of course, you replace `simpleBallot` by the name of your ballot.

Next, go to the file `goodvotex/voting/service.py` and find the function `add_vote_from_json` where you add your instructions for `simpleBallot`.

Finally, you have to create an HTML template for your ballot format.
Place it in `goodvotex/voting/templates` and name it `vote_simpleBallot.html`.
You can do whatever you want in this template.
However, eventually you must POST a JSON formatted object to the URL `/vote/{{election.id}}`.
You can format it as you like, as you will evaluate it on your own in the function `parse_from_json(self, json)`.
The only requirement is that it has an attribute `type` with the value `"simpleBallot"`, 
as this is used to figure out which ballot object should be created.

Now, your new ballot type is registered in the system.
However, if you want to create an election with this ballot type, 
you have to add this option in the file `goodvotex/voting/templates/start.html` in the select-form with id `ballot_type`.
That's it.

## Copyright notice

This software is licensed under the MIT License. 
It was developed in 2022 and 2023 by Christian Laußmann and Paul Nüsken at the Heinrich-Heine-University in Düsseldorf.
