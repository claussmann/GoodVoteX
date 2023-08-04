# GoodVoteX

GoodVoteX allows you to conduct elections with a variety of ballot types and voting rules.
All voting procedures used have a scientific background.
That is, their properties have been studied e.g. in Computational Social Choice literature.
Thus, the platform allows you to choose a suitable voting rule and ballot format for your election.

We currently support the following voting rules:

| Voting Rule                           | Ballots                  | Reference                                                                                 |
|---------------------------------------|--------------------------|-------------------------------------------------------------------------------------------|
| Bounded Approval Voting               | Bounded Approval Ballots | AAMAS-2023: "Bounded Approval Ballots: Balancing Expressiveness and Simplicity for Multiwinner Elections" by D. Baumeister, L. Boes, C. Laußmann and S. Rey |
| Approval Voting                       | Approval Ballots         | -                                                                                        |
| Satisfaction Approval Voting          | Approval Ballots         | -                                                                                        |
| Proportional Approval Voting          | Approval Ballots         | -                                                                                        |
| Borda                                 | Ordinal Ranks            | -                                                                                        |
| Borda-Chamberlin-Courant              | Ordinal Ranks            | -                                                                                        |
| Single Transferable Vote              | Ordinal Ranks            | -                                                                                        |
| Copeland                              | Ordinal Ranks            | -                                                                                        |
| Bucklin                               | Ordinal Ranks            | -                                                                                        |
| Fallback                              | Truncated Ordinal Ranks  | -                                                                                        |
| Welfare Maximization                  | Cardinal ballot          | -                                                                                        |

## Run (Production)

For production, the application will run in a docker container with a production WSGI server (see `docs/deployment.rst`).
We provide ready-to-use docker images via the github container registry (`ghcr.io/claussmann/goodvotex:<tag>`).
Examples for docker-compose can be found under `docs`.
We provide three groups of images.
With the tag `testing` you will receive the latest image build from the testing branch.
Note that this image is still under testing, so features might be buggy, not working, or removed in the future.
For production, we recommend the tag `latest` or a specific version number (e.g. `v1.0`).
If you always want to test the latest features in the production branch, you can also use the tag `rolling` for rolling release images.

If you prefer building the docker image yourself, run `docker build . -f docker/Dockerfile --tag goodvotex` from the root of the repository.


## Run (Development)

For development, you first need to add the configuration.
To this end, add a file `.env` to the root of this repository.
You can use `.env.example` as a template.

There are two possibilities for local development:

1) `docker-compose` ,
2) a local python interpreter running flask.

To ease the setup we provide a `setup-development.sh` script, which

* creates all necessary directories,
* downloads external assets,
* installs python package requirements (and creates a venv if wanted).

This is mainly used when using a local python interpreter or docker-compose with change detection.


#### Develop using docker-compose

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

#### Develop using local interpreter

When you run `setup-development.sh` it will ask you if you want to start the application locally. If you answer `no`, you can later start the application by running 

```bash
#activate venv
source venv/bin/activate

# read ENV vars from file.
export $(grep "^[^#;]" .env | xargs)

# Run flask debug server
flask run --port="${GOODVOTEX_PORT}" --debug
```

## External Assets

GoodVotesX uses Bootstrap and JQuery which are NOT shipped with this repository.
The docker image downloads these during the build.
During local development you may need to download the files yourselves.
Running `setup-development.sh` will do this for you.
Note that this will download from third party locations such as e.g. jsdelivr.
However, checksums are checked for all files.



## Contribute

We welcome everyone who wants to add ballot formats or new voting rules.
The process is described in the subsequent paragraphs.
Note that, if you have started the app before, you will most likely need to alter the database tables after implementing your changes.
We are working on a better option, but right now the only option is to delete the database (`storage/database.db`) and recreate it (e.g. using the `setup-development.sh`).

### New Ballot Format
Let's assume you want to call the ballot `Simple Ballot`.
In the file `goodvotex/voting/models.py` you create a class `SimpleBallot` which inherits from the class `Ballot`.
Note that you have to overwrite the following methods:

- `_check_validity(self)`: Returns `True` if and only if this ballot is valid (OPTIONAL; as a default every ballot is considered valid).
- `_parse_from_json(self, json)`: This function is called immediately after construction. It is given a dict in a JSON like structure. The format of this dict is defined by you when you write the HTML/JS form later.

You may need to introduce further methods depending on your needs.

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

### New Voting Rule
We assume you call your voting rule `SimpleVoteElection`.
In the file `goodvotex/voting/models.py` you create a class `SimpleVoteElection` which inherits from the class `Election`.
Note that you have to overwrite the following methods:

- `_compute_winners(self)`: Returns the set of winners.
- `_check_validity(self, ballot)`: This function is called before adding a ballot and should return True/False depending on whether the ballot is valid (and accepted in this election).
- `get_ballot_type(self)`: Returns the type of accepted ballots in this election.

Further, your class must have the following database attributes:

    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "simpleVoteElection",
    }

Next, go to the file `goodvotex/voting/service.py` and find the function `register_election` where you add your instructions for `SimpleVoteElection`.
Finally, to make your voting rule available for the user, got to `goodvotex/voting/templates/create.html` and add it to the options.
Please also write a paragraph about you voting rule in the accordion below.


## Copyright notice

This software is licensed under the MIT License. 
It was developed in 2022 and 2023 by Christian Laußmann and Paul Nüsken at the Heinrich-Heine-University in Düsseldorf.
