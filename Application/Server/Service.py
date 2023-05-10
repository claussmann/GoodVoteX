import random
import json
import os
import itertools
import re
from hashlib import sha256
from DataStructures import *


"""
The following lines are needed to initialize the database.
"""
user_storage_path = "../DB/users/"
election_storage_path = "../DB/elections/"
elections = dict()
users = dict()
sessions = dict()







# ================================================================================
# ========================    Service Functions   ================================
# ================================================================================

"""
Registers a new election.

@return: When registration successful, returns the election object.
"""
def register_election(name, description, candidates, K, user_owner):
    if len(elections) > 0xFFF:
        raise Exception("Election stroage is full.")
    if not user_owner:
        raise Exception("You must login to create elections.")
    new_id = "%04x" % random.randint(0, 0xFFFF)
    while new_id in elections:
        new_id = "%04x" % random.randint(0, 0xFFFF)
    e = Election(new_id, name, description, candidates, K)
    elections[new_id] = e
    save_election_to_file(e)
    user_owner.add_election(e)
    save_user_to_file(user_owner)
    return e

"""
Registers a new user.

@return: When registration successful, returns the election object.
"""
def register_user(username, name, password):
    username = username.lower()
    if len(users) > 0xFFF:
        raise Exception("User stroage is full.")
    if username in users:
        raise Exception("Username already exists.")
    u = User(username, name, password)
    users[username] = u
    save_user_to_file(u)
    return u

"""
@return: The election object with the given ID (if exists).
"""
def get_election(election_id):
    if election_id not in elections:
        raise Exception("This election doesn't exist: %s" % str(election_id))
    return elections[election_id]

"""
@return: The user object with the given username (if exists).
"""
def get_user(username):
    username = username.lower()
    if username not in users:
        raise Exception("This user doesn't exist: %s" % str(username))
    return users[username]

"""
@return: The user object with the given session token. If it doesn't exist, returns False.
"""
def get_user_by_session(token):
    if token not in sessions:
        return False
    return sessions[token]

"""
@return: True if the user exists and passowrd is correct.
"""
def verify_password(username, password):
    username = username.lower()
    if username not in users:
        return false
    return users[username].check_password(password)

"""
@return: Temporary access token if the user exists and passowrd is correct.
"""
def get_session_token(username, password):
    user = get_user(username)
    if not user.check_password(password):
        raise Exception("Incorrect password!")
    token = "%08x" % random.randint(0, 0xFFFFFFFFFFFF)
    sessions[token] = user
    return token

"""
Searches the database for elections which match the search string. The results are
ordered by relevance.

@return: A list of election objects.
"""
def search(search_string):
    if len(search_string) > 60: raise Exception("Search is too long.")
    ret = list()
    for election in elections.values():
        search_relevance = election.search_relevance(search_string)
        if search_relevance > 0:
            ret.append((search_relevance, election))
    return [x[1] for x in sorted(ret, key = lambda e : e[0], reverse=True)] # Sort results by relevance

"""
Adds a ballot to the given election.
"""
def add_vote(election_id, ballot):
    e = get_election(election_id)
    e.add_ballot(ballot)
    save_election_to_file(e)

"""
Deletes the given election. This will also delete it from the persistent storage!
"""
def delete_election(election_id, user):
    if not election_id in user.elections:
        raise Exception("You need to login!")
    e = get_election(election_id)
    elections.pop(election_id)
    os.remove(election_storage_path + election_id + ".json")

"""
Deletes the given election. This will also delete it from the persistent storage!
"""
def delete_user(username):
    u = get_user(username)
    users.pop(username)
    os.remove(user_storage_path + username + ".json")

"""
Evaluates an election, i.e. computes the current winners.

@return: A dict mapping a committee-ID to committee members. Each committee
         in the dict is a winner committee (due to ties we do not always
         have a unique winner committee). The committee-IDs are known to the
         system, and can be referenced e.g. for tie-breaking in the final
         outcome.
"""
def evaluate_current_winners(election_id):
    e = get_election(election_id)
    e.stop()
    ret = e.evaluate()
    e.restart()
    save_election_to_file(e)
    return ret

"""
Evaluates an election, i.e. computes the final possible winners.

@return: A dict mapping a committee-ID to committee members. Each committee
         in the dict is a winner committee (due to ties we do not always
         have a unique winner committee). The committee-IDs are known to the
         system, and can be referenced e.g. for tie-breaking in the final
         outcome.
"""
def evaluate_final_winners(election_id, user):
    if not election_id in user.elections:
        raise Exception("You need to login!")
    e = get_election(election_id)
    e.stop()
    ret = e.evaluate()
    save_election_to_file(e)
    return ret

"""
After evaluating the election, we can break potential ties between multiple winner-
committees by setting the committee committee-ID as the winner. This ID is retreived
from the "evaluate" function.
Note that this function also stops the election.
"""
def select_winner(election_id, user, committee_id):
    if not election_id in user.elections:
        raise Exception("You need to login!")
    e = get_election(election_id)
    e.set_winner(committee_id)
    save_election_to_file(e)

"""
Saves an election is JSON format to a file.
"""
def save_election_to_file(election):
    filename = election_storage_path + election.eid + ".json"
    json_str = json.dumps(election.serialize())
    f = open(filename, "w")
    f.write(json_str)
    f.close()

"""
Saves a user is JSON format to a file.
"""
def save_user_to_file(user):
    filename = user_storage_path + user.username + ".json"
    json_str = json.dumps(user.serialize())
    f = open(filename, "w")
    f.write(json_str)
    f.close()

"""
Reads a JSON-formatted file to an election object.

@return: The election object.
"""
def load_election_from_file(filename):
    f = open(filename, "r")
    raw_obj = json.loads(f.read())
    e = Election(raw_obj["eid"], raw_obj["name"], raw_obj["description"], set(raw_obj["candidates"]), raw_obj["K"])
    e.potential_winners = raw_obj["potential_winners"]
    for ballot in raw_obj["__ballots__"]:
        e.add_ballot([BoundedSet(bs["lower"], bs["saturation"], bs["upper"], *bs["set"]) for bs in ballot])
    e.is_stopped = raw_obj["is_stopped"]
    if raw_obj["is_finished"]:
        e.is_finished = True
        e.winner = raw_obj["winner"]        
    f.close()
    return e

"""
Reads a JSON-formatted file to a user object.

@return: The election object.
"""
def load_user_from_file(filename):
    f = open(filename, "r")
    raw_obj = json.loads(f.read())
    u = User(raw_obj["username"], raw_obj["name"], "dummy1234")
    u.salt = raw_obj["salt"]
    u.password_hash = raw_obj["password_hash"]      
    u.elections = raw_obj["elections"]      
    f.close()
    return u

"""
Loads all election files and users from the storage path.
"""
def load_all():
    election_files = [f for f in os.listdir(election_storage_path) if f.endswith(".json")]
    for f in election_files:
        e = load_election_from_file(election_storage_path + f)
        elections[e.eid] = e
    
    user_files = [f for f in os.listdir(user_storage_path) if f.endswith(".json")]
    for f in user_files:
        u = load_user_from_file(user_storage_path + f)
        users[u.username] = u

