import json
import os
from DataStructures import *
from pathlib import Path
import time

class DataBase():
    def __init__(self, storage_path):
        self.user_storage_path = storage_path + "/users/"
        self.election_storage_path = storage_path + "/elections/"
        Path(self.user_storage_path).mkdir(parents=True, exist_ok=True)
        Path(self.election_storage_path).mkdir(parents=True, exist_ok=True)
        self.elections = dict() # eID -> election
        self.users = dict() # username -> user
        self.sessions = dict() # token -> user
        self.sessions_ttl = dict() # token -> expiration time
        self.__load_all__()
    
    """
    Returns the user if it exists.
    """
    def get_user(self, username):
        if username in self.users:
            return self.users[username]
        raise Exception("The user with ID %s does not exist." % str(username))
    
    """
    Returns the election if it exists.
    """
    def get_election(self, eID):
        if eID in self.elections:
            return self.elections[eID]
        raise Exception("The election with ID %s does not exist." % str(eID))
    
    """
    Returns a list of all elections.
    """
    def get_all_elections(self):
        return self.elections.values()
    
    """
    Returns the user if session exists.
    """
    def get_user_for_session(self, token):
        if token in self.sessions:
            if time.time() > self.sessions_ttl[token]:
                self.sessions.pop(token)
                self.sessions_ttl.pop(token)
                raise Exception("This session expired. Log in again.")
            return self.sessions[token]
        raise Exception("This session does not exist")

    """
    Adds a user to the data base unless it exists already.
    """
    def add_user(self, user):
        if len(self.users) > 0xFF:
            raise Exception("User stroage is full.")
        if user.username in self.users:
            raise Exception("The user with ID %s already exists." % user.username)
        self.users[user.username] = user
        self.sync_user(user.username)
    
    """
    Adds an election to the data base unless it exists already.
    """
    def add_election(self, election):
        if len(self.elections) > 0xFFFF:
            raise Exception("Election stroage is full.")
        if election.eid in self.elections:
            raise Exception("The election with ID %s already exists." % election.eid)
        self.elections[election.eid] = election
        self.sync_election(election.eid)
    
    """
    Returns a new unique ID to create a new election.
    """
    def get_new_unique_id(self):
        new_id = "%06x" % random.randint(0, 0xFFFFFF)
        while new_id in self.elections:
            new_id = "%06x" % random.randint(0, 0xFFFFFF)
        return new_id
    
    """
    Returns a new unique session ID for the user.
    """
    def create_new_session_id(self, username):
        user = self.get_user(username)
        token = "%020x" % random.randint(0, 0xFFFFFFFFFFFFFFFF)
        while token in self.sessions:
            token = "%020x" % random.randint(0, 0xFFFFFFFFFFFFFFFF)
        self.sessions[token] = user
        self.sessions_ttl[token] = time.time() + 1800 # 30 minutes
        return token
    
    """
    Removes user session and effectively logs out the user.
    """
    def terminate_user_session(self, token):
        if token in self.sessions:
            self.sessions.pop(token)
            self.sessions_ttl.pop(token)
        else:
            raise Exception("This session was logged out already.")
    
    """
    Persists changes to a user.
    """
    def sync_user(self, username):
        user = self.get_user(username)
        filename = self.user_storage_path + user.username + ".json"
        json_str = json.dumps(user.serialize())
        f = open(filename, "w")
        f.write(json_str)
        f.close()
    
    """
    Persists changes to an election.
    """
    def sync_election(self, eID):
        election = self.get_election(eID)
        filename = self.election_storage_path + election.eid + ".json"
        json_str = json.dumps(election.serialize())
        f = open(filename, "w")
        f.write(json_str)
        f.close()
    
    """
    Deletes the given election. This will also delete it from the persistent storage!
    """
    def delete_election(self, eID):
        e = self.get_election(eID)
        self.elections.pop(eID)
        os.remove(self.election_storage_path + eID + ".json")

    """
    Deletes the given user. This will also delete it from the persistent storage!
    """
    def delete_user(self, username):
        u = self.get_user(username)
        self.users.pop(username)
        os.remove(self.user_storage_path + username + ".json")
    
    """
    WARNING: This deletes the database forever!
    """
    def dump(self):
        election_files = [f for f in os.listdir(self.election_storage_path) if f.endswith(".json")]
        for f in election_files:
            os.remove(self.election_storage_path + f)
        
        user_files = [f for f in os.listdir(self.user_storage_path) if f.endswith(".json")]
        for f in user_files:
            os.remove(self.user_storage_path + f)

        self.users = dict()
        self.sessions = dict()
        self.elections = dict()




    ###################################################
    ############### Private Methods ###################
    ###################################################

    def __load_election_from_file__(self, filename):
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

    def __load_user_from_file__(self, filename):
        f = open(filename, "r")
        raw_obj = json.loads(f.read())
        u = User(raw_obj["username"], raw_obj["name"], "dummy1234")
        u.salt = raw_obj["salt"]
        u.password_hash = raw_obj["password_hash"]
        for eid in raw_obj["elections"]:
            u.add_election(self.get_election(eid))
        f.close()
        return u

    def __load_all__(self):
        election_files = [f for f in os.listdir(self.election_storage_path) if f.endswith(".json")]
        for f in election_files:
            e = self.__load_election_from_file__(self.election_storage_path + f)
            self.elections[e.eid] = e
        
        user_files = [f for f in os.listdir(self.user_storage_path) if f.endswith(".json")]
        for f in user_files:
            u = self.__load_user_from_file__(self.user_storage_path + f)
            self.users[u.username] = u

