from goodvotes import *
from .models.election import *
from .models.auth import *


def register_election(title, description, candidates, K, user_owner):
    """
    Registers a new election.

    :param name:
    :param description:
    :param candidates:
    :param K:
    :param user_owner:
    :return: When registration successful, returns the election object.
    """
    # u = get_user(user_owner)
    u = get_user("admin")
    e = Election(title = title, description=description, committeesize=K)
    for c in candidates:
        e.candidates.append(Candidate(name=c))
    u.elections.append(e)
    db.session.add(e)
    db.session.commit()
    return e


def register_user(username, name, password):
    """
    Registers a new user.

    :param username:
    :param name:
    :param password:
    :return: When registration successful, returns the election object.
    """
    u = User(username = username, name=name, password_hash=password_hash(password, "123"))
    db.session.add(u)
    db.session.commit()
    return u


def get_election(election_id):
    """

    :param election_id:
    :return: The election object with the given ID (if exists).
    """
    return Election.query.filter_by(id=election_id).first()


def get_user(username):
    """

    :param username:
    :return: The user object with the given username (if exists).
    """
    return User.query.filter_by(username=username).first()


def search(search_string):
    """
    Searches the database for elections which match the search string. The results are ordered by relevance.
    :param search_string:
    :return: A list of election objects.
    """
    if len(search_string) > 60: raise Exception("Search is too long.")
    ret = list()
    for election in Election.query.all():
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
    e = get_election(election_id)
    e.add_ballot(ballot)
    db.session.add(e)
    db.session.commit()


def delete_election(election_id, user):
    """
    Deletes the given election. This will also delete it from the persistent storage!

    :param election_id:
    :param user:
    :return:
    """
    Election.query.filter_by(id=election_id).delete()
    db.session.commit()


def evaluate(election_id, user):
    """
    Evaluates an election, i.e. computes the current winners.

    :param election_id:
    :param user:
    :return:
    """
    # if not user or not user.owns_election(election_id):
    #     raise Exception("You need to login!")
    e = get_election(election_id)
    e.compute_current_winner()
    db.session.add(e)
    db.session.commit()


def stop_election(election_id, user):
    """
    Stops an election.

    :param election_id:
    :param user:
    :return:
    """
    # if not user or not user.owns_election(election_id):
    #     raise Exception("You need to login!")
    e = get_election(election_id)
    e.stop()
    db.session.add(e)
    db.session.commit()
