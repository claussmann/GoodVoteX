from pathlib import Path

from .persistence.storage import JSONFileStorage
from .persistence.models.election import *
from .persistence.models.auth import *

db = JSONFileStorage(Path(__file__).parent / "../storage")


def register_election(name, description, candidates, K, user_owner):
    """
    Registers a new election.

    :param name:
    :param description:
    :param candidates:
    :param K:
    :param user_owner:
    :return: When registration successful, returns the election object.
    """
    if not user_owner:
        raise Exception("You must login to create elections.")
    e = Election(db.get_new_unique_id(), name, description, candidates, K)
    db.add_election(e)
    user_owner.add_election(e)
    db.sync_user(user_owner.username)
    return e


def register_user(username, name, password):
    """
    Registers a new user.

    :param username:
    :param name:
    :param password:
    :return: When registration successful, returns the election object.
    """
    u = User(username, name, password)
    db.add_user(u)
    return u


def change_password(user, password, new_password, confirm_password):
    """Changes a user password."""
    if new_password != confirm_password:
        raise Exception("New passwords do not match.")
    if not user.check_password(password):
        raise Exception("Incorrect password!")
    user.set_password(new_password)
    db.sync_user(user.username)


def get_election(election_id):
    """

    :param election_id:
    :return: The election object with the given ID (if exists).
    """
    return db.get_election(election_id)


def get_user(username):
    """

    :param username:
    :return: The user object with the given username (if exists).
    """
    return db.get_user(username)


def get_user_by_session(token):
    """

    :param token:
    :return: The user object with the given session token. If it doesn't exist, returns False.
    """
    try:
        return db.get_user_for_session(token)
    except:
        return False


def terminate_user_session(token):
    """
    Logout the user.

    :param token:
    :return:
    """
    db.terminate_user_session(token)


def get_session_token(username, password):
    """

    :param username:
    :param password:
    :return: Temporary access token if the user exists and passowrd is correct.
    """
    user = db.get_user(username)
    if not user.check_password(password):
        raise Exception("Incorrect password!")
    return db.create_new_session_id(username)


def search(search_string):
    """
    Searches the database for elections which match the search string. The results are ordered by relevance.
    :param search_string:
    :return: A list of election objects.
    """
    if len(search_string) > 60: raise Exception("Search is too long.")
    ret = list()
    for election in db.get_all_elections():
        search_relevance = election.search_relevance(search_string)
        if search_relevance > 0:
            ret.append((search_relevance, election))
    return [x[1] for x in sorted(ret, key=lambda e: e[0], reverse=True)]  # Sort results by relevance


def add_vote(election_id, ballot):
    """
    Adds a ballot to the given election.

    :param election_id:
    :param ballot:
    :return:
    """
    e = db.get_election(election_id)
    e.add_ballot(ballot)
    db.sync_election(election_id)


def delete_election(election_id, user):
    """
    Deletes the given election. This will also delete it from the persistent storage!

    :param election_id:
    :param user:
    :return:
    """
    if not user or not user.owns_election(election_id):
        raise Exception("You need to login!")
    db.delete_election(election_id)


def evaluate(election_id, user):
    """
    Evaluates an election, i.e. computes the current winners.

    :param election_id:
    :param user:
    :return:
    """
    if not user or not user.owns_election(election_id):
        raise Exception("You need to login!")
    e = db.get_election(election_id)
    e.compute_current_winner()
    db.sync_election(election_id)


def stop_election(election_id, user):
    """
    Stops an election.

    :param election_id:
    :param user:
    :return:
    """
    if not user or not user.owns_election(election_id):
        raise Exception("You need to login!")
    e = db.get_election(election_id)
    e.stop()
    db.sync_election(election_id)
