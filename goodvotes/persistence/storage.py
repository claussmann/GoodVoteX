import json
import time
from pathlib import Path

from .models.auth import *
from .models.election import *


class JSONFileStorage:
    def __init__(self, storage_path: Path):
        self.user_storage_path = storage_path / "users"
        self.election_storage_path = storage_path / "elections"

        self.user_storage_path.mkdir(parents=True, exist_ok=True)
        self.election_storage_path.mkdir(parents=True, exist_ok=True)

        self.elections = dict()  # eID -> election
        self.users = dict()  # username -> user
        self.sessions = dict()  # token -> user
        self.sessions_ttl = dict()  # token -> expiration time
        self._load_all()

    def get_user(self, username):
        """
        Returns the user if it exists.

        :param username:
        :return:
        """
        if username in self.users:
            return self.users[username]
        raise Exception("The user with ID %s does not exist." % str(username))

    def get_election(self, eID):
        """
        Returns the election if it exists.

        :param eID:
        :return:
        """
        if eID in self.elections:
            return self.elections[eID]
        raise Exception("The election with ID %s does not exist." % str(eID))

    def get_all_elections(self):
        """
        Returns a list of all elections.

        :return:
        """
        return self.elections.values()

    def get_user_for_session(self, token):
        """
        Returns the user if session exists.

        :param token:
        :return:
        """
        if token in self.sessions:
            if time.time() > self.sessions_ttl[token]:
                self.sessions.pop(token)
                self.sessions_ttl.pop(token)
                raise Exception("This session expired. Log in again.")
            return self.sessions[token]
        raise Exception("This session does not exist")

    def add_user(self, user):
        """
        Adds a user to storage unless it exists already.

        Use sync_election(username) to persist changes to an already registered User.

        :param user:
        :return:
        """
        if len(self.users) > 0xFF:
            raise Exception("User stroage is full.")
        if user.username in self.users:
            raise Exception("The user with ID %s already exists." % user.username)
        self.users[user.username] = user
        self.sync_user(user.username)

    def add_election(self, election):
        """
        Register and persist an election to storage.

        Use sync_election(eid) to persist changes to an already registered election.

        :raise Exception: If storage is full, or eid is taken/election is already registered.
        :param election:
        :return:
        """
        if len(self.elections) > 0xFFFF:
            raise Exception("Election storage is full.")
        if election.eid in self.elections:
            raise Exception("An election with ID %s already exists." % election.eid)
        self.elections[election.eid] = election
        self.sync_election(election.eid)

    def get_new_unique_id(self):
        """
        Returns a new unique ID to create a new election.

        :return:
        """
        new_id = "%06x" % random.randint(0, 0xFFFFFF)
        while new_id in self.elections:
            new_id = "%06x" % random.randint(0, 0xFFFFFF)
        return new_id

    def create_new_session_id(self, username):
        """
        Returns a new unique session ID for the user.

        :param username:
        :return:
        """
        user = self.get_user(username)
        token = "%020x" % random.randint(0, 0xFFFFFFFFFFFFFFFF)
        while token in self.sessions:
            token = "%020x" % random.randint(0, 0xFFFFFFFFFFFFFFFF)
        self.sessions[token] = user
        self.sessions_ttl[token] = time.time() + 1800  # 30 minutes
        return token

    def terminate_user_session(self, token):
        """
        Removes user session and effectively logs out the user.

        :param token:
        :return:
        """
        if token in self.sessions:
            self.sessions.pop(token)
            self.sessions_ttl.pop(token)
        else:
            raise Exception("This session was logged out already.")

    def sync_user(self, username):
        """
        Persists changes to a user.

        :param username:
        :return:
        """
        user = self.get_user(username)
        filename = self.user_storage_path / "{}.json".format(user.username)
        json_str = json.dumps(user.serialize())
        f = open(filename, "w")
        f.write(json_str)
        f.close()

    def sync_election(self, eID):
        """
        Persists changes to an election.

        :param eID:
        :return:
        """
        election = self.get_election(eID)
        filename = self.election_storage_path / "{}.json".format(election.eid)
        json_str = json.dumps(election.serialize())
        f = open(filename, "w")
        f.write(json_str)
        f.close()

    def delete_election(self, eID):
        """
        Deletes the given election. This will also delete it from the persistent storage!

        :param eID:
        :return:
        """
        e = self.get_election(eID)
        self.elections.pop(eID)
        (self.election_storage_path / "{}.json".format(eID)).unlink()

    def delete_user(self, username):
        """
        Deletes the given user. This will also delete it from the persistent storage!

        :param username:
        :return:
        """
        u = self.get_user(username)
        self.users.pop(username)
        (self.user_storage_path / "{}.json".format(username)).unlink()

    def dump(self):
        """
        WARNING: This deletes the database forever!

        :return:
        """

        for f in self.election_storage_path.glob("*.json"):
            f.unlink()
        for f in self.user_storage_path.glob("*.json"):
            f.unlink()

        self.users = dict()
        self.sessions = dict()
        self.elections = dict()

    ###################################################
    #               Private Methods                   #
    ###################################################

    def _load_election_from_file(self, filename: Path):
        f = open(filename, "r")
        raw_obj = json.loads(f.read())
        e = Election(raw_obj["eid"], raw_obj["name"], raw_obj["description"], set(raw_obj["candidates"]), raw_obj["K"])
        if "current_winner" in raw_obj:
            e.current_winner = raw_obj["current_winner"]
        for ballot in raw_obj["__ballots__"]:
            e.add_ballot([BoundedSet(bs["lower"], bs["saturation"], bs["upper"], *bs["set"]) for bs in ballot])
        e.is_stopped = raw_obj["is_stopped"]
        f.close()
        return e

    def _load_user_from_file(self, filename: Path):
        f = open(filename, "r")
        raw_obj = json.loads(f.read())
        u = User(raw_obj["username"], raw_obj["name"], "dummy1234")
        u.salt = raw_obj["salt"]
        u.password_hash = raw_obj["password_hash"]
        for eid in raw_obj["elections"]:
            u.add_election(self.get_election(eid))
        f.close()
        return u

    def _load_all(self):
        for f in self.election_storage_path.glob("*.json"):
            e = self._load_election_from_file(f)
            self.elections[e.eid] = e

        for f in self.user_storage_path.glob("*.json"):
            u = self._load_user_from_file(f)
            self.users[u.username] = u
