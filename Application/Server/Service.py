import random
from DataStructures import *
from DataBase import *


db = DataBase("../DB")

"""
Registers a new election.

@return: When registration successful, returns the election object.
"""
def register_election(name, description, candidates, K, user_owner):
    if not user_owner:
        raise Exception("You must login to create elections.")
    e = Election(db.get_new_unique_id(), name, description, candidates, K)
    db.add_election(e)
    user_owner.add_election(e)
    db.sync_user(user_owner.username)
    return e

"""
Registers a new user.

@return: When registration successful, returns the election object.
"""
def register_user(username, name, password):
    u = User(username, name, password)
    db.add_user(u)
    return u

"""
@return: The election object with the given ID (if exists).
"""
def get_election(election_id):
    return db.get_election(election_id)

"""
@return: The user object with the given username (if exists).
"""
def get_user(username):
    return db.get_user(username)

"""
@return: The user object with the given session token. If it doesn't exist, returns False.
"""
def get_user_by_session(token):
    try:
        return db.get_user_for_session(token)
    except:
        return False

"""
@return: Temporary access token if the user exists and passowrd is correct.
"""
def get_session_token(username, password):
    user = db.get_user(username)
    if not user.check_password(password):
        raise Exception("Incorrect password!")
    return db.create_new_session_id(username)

"""
Searches the database for elections which match the search string. The results are
ordered by relevance.

@return: A list of election objects.
"""
def search(search_string):
    if len(search_string) > 60: raise Exception("Search is too long.")
    ret = list()
    for election in db.get_all_elections():
        search_relevance = election.search_relevance(search_string)
        if search_relevance > 0:
            ret.append((search_relevance, election))
    return [x[1] for x in sorted(ret, key = lambda e : e[0], reverse=True)] # Sort results by relevance

"""
Adds a ballot to the given election.
"""
def add_vote(election_id, ballot):
    e = db.get_election(election_id)
    e.add_ballot(ballot)
    db.sync_election(election_id)

"""
Deletes the given election. This will also delete it from the persistent storage!
"""
def delete_election(election_id, user):
    if election_id not in user.elections:
        raise Exception("You need to login!")
    db.delete_election(election_id)

"""
Evaluates an election, i.e. computes the current winners.

@return: A dict mapping a committee-ID to committee members. Each committee
         in the dict is a winner committee (due to ties we do not always
         have a unique winner committee). The committee-IDs are known to the
         system, and can be referenced e.g. for tie-breaking in the final
         outcome.
"""
def evaluate_current_winners(election_id):
    e = db.get_election(election_id)
    e.stop()
    ret = e.evaluate()
    e.restart()
    db.sync_election(election_id)
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
    e = db.get_election(election_id)
    e.stop()
    ret = e.evaluate()
    db.sync_election(election_id)
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
    e = db.get_election(election_id)
    e.set_winner(committee_id)
    db.sync_election(election_id)



