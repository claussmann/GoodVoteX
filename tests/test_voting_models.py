from .context import goodvotex
from goodvotex.voting.models import *

import pytest


#################################################################################
#                 Helpers
#################################################################################

def make_approval_ballot(candidates):
    json_content = {'app_candidates' : [str(c) for c in candidates], 'type' : 'approvalBallot'}
    return ApprovalBallot(json_content)

def make_bounded_ballot(*bounded_sets):
    json_content = {
        'sets' : dict(),
        'bounds' : dict()
    }
    i = 0
    for bs in bounded_sets:
        json_content['sets'][str(i)] = [str(c) for c in bs]
        json_content['bounds'][str(i)] = [bs.lower, bs.saturation, bs.upper]
        i += 1
    return BoundedApprovalBallot(json_content)

def make_dummy_election(committeesize, ballot_type, candidate_ids):
    e = Election(title="Test", description="test", committeesize=committeesize,
                is_stopped=False, ballot_type=ballot_type, votecount=0, ballots=list())
    e.candidates = [Candidate(name=cid, id=cid) for cid in candidate_ids]
    return e



#################################################################################
#                 Ballots
#################################################################################

def test_approval_ballot():
    json_content = {"app_candidates" : ["1", "3", "7", "9"]}
    ballot = ApprovalBallot(json_content)
    assert ballot.get_involved_candidates() == {"1", "3", "7", "9"}
    assert ballot.type == "approvalBallot"

def test_ordinal_ballot():
    json_content = {"order" : ["1", "7", "2", "5", "3"]}
    ballot = OrdinalBallot(json_content)
    assert ballot.get_involved_candidates() == {"1", "3", "7", "5", "2"}
    assert ballot.type == "ordinalBallot"
    assert ballot.position_of("2") == 3

def test_cardinal_ballot():
    json_content = {"ratings" : {"1":5, "7":1, "2":-3, "5":-8, "3":0}}
    json_content2 = {"ratings" : {"1":-12, "7":1, "3":0}}
    ballot = CardinalBallot(json_content)
    ballot2 = CardinalBallot(json_content2)
    assert ballot.get_involved_candidates() == {"1", "3", "7", "5", "2"}
    assert ballot.type == "cardinalBallot"
    assert ballot.utility_for("5") == -8
    assert ballot._check_validity()
    assert not ballot2._check_validity()

def test_bounded_approval_ballot():
    json_content = {
        'sets' : {"bs1": ["a", "b", "c"], "bs2": ["x", "y"], "bs3": ["d"], "bs4": ["e", "f", "g"]},
        'bounds' : {"bs1": [1, 2, 3], "bs2": [1, 1, 1], "bs3": [1, 1, 1], "bs4": [1, 3, 3]}
    }
    ballot = BoundedApprovalBallot(json_content)
    assert ballot._check_validity()
    assert ballot.get_involved_candidates() == {"a", "b", "c", "d", "e", "f", "g", "x", "y"}
    assert ballot.score({"a", "b", "c"}) == 2
    assert ballot.score({"a", "b", "c", "z"}) == 2
    assert ballot.score({"y", "x"}) == 0
    assert ballot.score({"y", "d"}) == 2
    assert ballot.score({"e", "f", "g"}) == 3


# """
#     Tests for Election
# """

# def test_stopped_election_doesnt_accept_ballots():
#     e = make_dummy_election(2, "any", [1,2,3])
#     e.stop()
#     b = make_approval_ballot([1,2,3])
#     with pytest.raises(Exception):
#         e.add_ballot(b)

# def test_stopped_election_can_be_restarted():
#     e = make_dummy_election(2, "any", [1,2,3,4,5])
#     e.stop()
#     e.restart()
#     b = make_approval_ballot([1,2,3])
#     e.add_ballot(b)

# def test_election_accepts_only_correct_ballots():
#     e = make_dummy_election(2, "approvalBallot", [1,2,3,4])
#     b = make_bounded_ballot(BoundedSet(1,2,3,{'a', 'b', 'c', 'd'}))
#     with pytest.raises(Exception): # bounded ballots cannot be added
#         e.add_ballot(b)

# def test_election_accepts_only_ballots_ith_valid_candidates():
#     e = make_dummy_election(2, "any", [1,2,3,4])
#     b = make_approval_ballot([1,5])
#     with pytest.raises(Exception): # candidate with id 5 doesnt exist
#         e.add_ballot(b)

# def test_search_relevance():
#     e = Election()
#     e.id = 42
#     e.title = "This Year Food Selection: What should be served?"
#     e.description = "You decide on Food: Banana, or Fish? Döner?"
#     assert e.search_relevance("Food") == 1
#     assert e.search_relevance("fOod") == 1
#     assert e.search_relevance("Food Selection?") == 2
#     assert e.search_relevance("You be or Banana") == 1
#     assert e.search_relevance("Apple") == 0
#     assert e.search_relevance("be") == 0  # short words are ignored
#     assert e.search_relevance("döner") == 1
#     assert e.search_relevance("What should be served? Banana or Fish?") == 5
#     assert e.search_relevance("42") == 100

# def test_score():
#     e = make_dummy_election(3, "boundedApprovalBallot", ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'])
#     b1 = make_bounded_ballot(BoundedSet(1,2,3,{'a', 'b', 'c', 'd'}), BoundedSet(1,2,2,{'e', 'f'}))
#     b2 = make_bounded_ballot(BoundedSet(1,2,3,{'a', 'b', 'c', 'd'}), BoundedSet(2,3,3,{'g', 'h', 'i'}))
#     e.ballots = [b1, b2]
#     assert e._score({e.candidates[0], e.candidates[1], e.candidates[2], e.candidates[5], e.candidates[7]}) == 5

# def test_winners():
#     e = make_dummy_election(3, "approvalBallot", ['a', 'b', 'c', 'd', 'e'])
#     e.add_ballot(make_approval_ballot(['a', 'b']))
#     e.add_ballot(make_approval_ballot(['c', 'b', 'e']))
#     e.add_ballot(make_approval_ballot(['c', 'e']))
#     e.add_ballot(make_approval_ballot(['b']))
#     e.add_ballot(make_approval_ballot(['c']))
#     e.add_ballot(make_approval_ballot(['e', 'd', 'c']))

#     e.recompute_current_winner()
#     winners = e.get_winners()
#     assert len(winners) == 3
#     assert {str(c.id) for c in winners} == {'b', 'c', 'e'}

