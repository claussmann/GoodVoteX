import time

from ..auth.service import get_user
from .models import *
from .. import db


def register_election(election_type, title, description, candidates, K, user_owner):
    """
    Registers a new election.

    :param name:
    :param description:
    :param candidates:
    :param K:
    :param user_owner:
    :return: When registration successful, returns the election object.
    """
    constructors = {
        "approvalElection": ApprovalElection,
        "bordaElection": BordaElection,
        "bordaCCElection": BordaCCElection,
        "stvElection": STVElection,
        "savElection": SAVElection,
        "pavElection": PAVElection,
        "boundedApprovalElection": BoundedApprovalElection,
        "utilitarianElection": UtilitarianElection
    }
    e = constructors[election_type](title=title, description=description, committeesize=K)
    for c in candidates:
        e.candidates.append(Candidate(name=c))
    user_owner.elections.append(e)
    db.session.add(user_owner)
    db.session.add(e)
    db.session.commit()
    return e


def get_election(election_id):
    """

    :param election_id:
    :return: The election object with the given ID (if exists).
    """
    return Election.query.filter_by(id=election_id).first()


def get_all_elections():
    """
    Retrieve all elections from database.

    :return:
    """
    return Election.query.all()

def get_trending_elections():
    """
    Get up to 5 elections which received a lot of attention recently.

    :return:
    """
    active_elections = Election.query.filter(Election.is_stopped == False).all()
    i = 1024
    current_time = int(time.time())
    ret = list()
    while len(ret) < min(len(active_elections), 15):
        ret = [e for e in active_elections if e.last_votetime >= current_time - i]
        i = i*2
    ret = sorted(ret, key=lambda x: x.votecount, reverse=True)
    return ret[:min(len(ret), 5)]


def search(search_string):
    """
    Searches the database for elections which match the search string. The results are ordered by relevance.
    :param search_string:
    :return: A list of election objects.
    """
    if len(search_string) > 60: raise Exception("Search is too long.")
    ret = list()
    for election in get_all_elections():
        search_relevance = election.search_relevance(search_string)
        if search_relevance > 0:
            ret.append((search_relevance, election))
    return [x[1] for x in sorted(ret, key=lambda e: e[0], reverse=True)]  # Sort results by relevance


def add_vote_from_json(election_id, json_content):
    """
    Adds a ballot to the given election.

    :param election_id:
    :param ballot:
    :return:
    """
    e = get_election(election_id)
    constructors = {
        "boundedApprovalBallot": BoundedApprovalBallot,
        "approvalBallot": ApprovalBallot,
        "cardinalBallot": CardinalBallot,
        "ordinalBallot": OrdinalBallot
    }
    if json_content["type"] in constructors:
        ballot = constructors[json_content["type"]](json_content)
    else:
        raise Exception("This ballot type is unknown.")
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
    e = get_election(election_id)
    if not user.owns_election(e):
        raise Exception("You need to login!")
    Election.query.filter_by(id=election_id).delete()
    db.session.commit()


def evaluate(election_id, user):
    """
    Evaluates an election, i.e. computes the current winners.

    :param election_id:
    :param user:
    :return:
    """
    e = get_election(election_id)
    if not user.owns_election(e):
        raise Exception("You need to login!")
    e.recompute_current_winner()
    db.session.add(e)
    db.session.commit()


def stop_election(election_id, user):
    """
    Stops an election.

    :param election_id:
    :param user:
    :return:
    """
    e = get_election(election_id)
    if not user.owns_election(e):
        raise Exception("You need to login!")
    e.stop()
    db.session.add(e)
    db.session.commit()
