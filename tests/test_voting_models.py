from .context import goodvotex
from goodvotex.voting.models import *

import pytest



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



"""
    Tests for Election
"""

def test_stopped_election_doesnt_accept_ballots():
    e = make_dummy_election(2, "any", [1,2,3])
    e.stop()
    b = make_approval_ballot([1,2,3])
    with pytest.raises(Exception):
        e.add_ballot(b)

def test_stopped_election_can_be_restarted():
    e = make_dummy_election(2, "any", [1,2,3,4,5])
    e.stop()
    e.restart()
    b = make_approval_ballot([1,2,3])
    e.add_ballot(b)

def test_election_accepts_only_correct_ballots():
    e = make_dummy_election(2, "approvalBallot", [1,2,3,4])
    b = make_bounded_ballot(BoundedSet(1,2,3,{'a', 'b', 'c', 'd'}))
    with pytest.raises(Exception): # bounded ballots cannot be added
        e.add_ballot(b)

def test_election_accepts_only_ballots_ith_valid_candidates():
    e = make_dummy_election(2, "any", [1,2,3,4])
    b = make_approval_ballot([1,5])
    with pytest.raises(Exception): # candidate with id 5 doesnt exist
        e.add_ballot(b)

def test_search_relevance():
    e = Election()
    e.id = 42
    e.title = "This Year Food Selection: What should be served?"
    e.description = "You decide on Food: Banana, or Fish? Döner?"
    assert e.search_relevance("Food") == 1
    assert e.search_relevance("fOod") == 1
    assert e.search_relevance("Food Selection?") == 2
    assert e.search_relevance("You be or Banana") == 1
    assert e.search_relevance("Apple") == 0
    assert e.search_relevance("be") == 0  # short words are ignored
    assert e.search_relevance("döner") == 1
    assert e.search_relevance("What should be served? Banana or Fish?") == 5
    assert e.search_relevance("42") == 100

def test_score():
    e = make_dummy_election(3, "boundedApprovalBallot", ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'])
    b1 = make_bounded_ballot(BoundedSet(1,2,3,{'a', 'b', 'c', 'd'}), BoundedSet(1,2,2,{'e', 'f'}))
    b2 = make_bounded_ballot(BoundedSet(1,2,3,{'a', 'b', 'c', 'd'}), BoundedSet(2,3,3,{'g', 'h', 'i'}))
    e.ballots = [b1, b2]
    assert e._score({e.candidates[0], e.candidates[1], e.candidates[2], e.candidates[5], e.candidates[7]}) == 5

def test_winners():
    e = make_dummy_election(3, "approvalBallot", ['a', 'b', 'c', 'd', 'e'])
    e.add_ballot(make_approval_ballot(['a', 'b']))
    e.add_ballot(make_approval_ballot(['c', 'b', 'e']))
    e.add_ballot(make_approval_ballot(['c', 'e']))
    e.add_ballot(make_approval_ballot(['b']))
    e.add_ballot(make_approval_ballot(['c']))
    e.add_ballot(make_approval_ballot(['e', 'd', 'c']))

    e.recompute_current_winner()
    winners = e.get_winners()
    assert len(winners) == 3
    assert {str(c.id) for c in winners} == {'b', 'c', 'e'}



"""
    Tests for Bounded Approval Ballots
"""

def test_create_bounded_set():
    bs = BoundedSet(1, 3, 4, "a", "b", "c")
    assert bs.lower == 1
    assert bs.saturation == 3
    assert bs.upper == 4
    assert "a" in bs
    assert "c" in bs

def test_create_bounded_set_from_set():
    bs = BoundedSet(1, 3, 4, {"a", "b", "c"})
    assert bs.lower == 1
    assert bs.saturation == 3
    assert bs.upper == 4
    assert "a" in bs
    assert "c" in bs

def test_bounded_set_to_string():
    bs = BoundedSet(1, 3, 4, {"a", "b", "c"})
    assert str(bs) == "<{'a', 'b', 'c'}, 1, 3, 4>"
    bs = BoundedSet(1, 3, 4, "b", "c", "a")
    assert str(bs) == "<{'a', 'b', 'c'}, 1, 3, 4>"

def test_bounded_set_iterator():
    x = set()
    bs = BoundedSet(1, 3, 4, {"a", "b", "c"})
    for a in bs:
        x.add(a)
    assert x == {"a", "b", "c"}
    assert len(bs) == 3

def test_bounded_set_intersection():
    b1 = BoundedSet(1, 3, 3, {"a", "b", "c"})
    b2 = BoundedSet(1, 1, 2, {"c", "d"})
    b3 = BoundedSet(1, 3, 4, {"e", "f", "g", "h"})
    b4 = BoundedSet(1, 2, 3, {"a", "b", "c"})
    s5 = {"b", "d", "g", "h"}

    assert b1.is_disjoint(b3)
    assert b1.intersection_size(b2) == 1
    assert b1.intersection_size(b4) == 3
    assert b1.intersection_size(s5) == 1
    assert b3.intersection_size(s5) == 2

def test_bounded_set_equals():
    b1 = BoundedSet(1, 3, 3, {"a", "b", "c"})
    b2 = BoundedSet(1, 3, 3, {"a", "b", "c"})
    b3 = BoundedSet(1, 3, 3, {"e", "b", "c"})
    b4 = BoundedSet(1, 1, 3, {"a", "b", "c"})

    assert b1 == b2
    assert b1 != b3
    assert b1 != b4

def test_bounded_set_phi():
    bs = BoundedSet(2, 3, 5, {"a", "b", "c", "d", "e", "f", "g"})
    assert bs.phi({"a"}) == 0
    assert bs.phi({"a", "c"}) == 1
    assert bs.phi({"a", "c", "e"}) == 1
    assert bs.phi({"a", "c", "e", "f"}) == 3 / 4
    assert bs.phi({"a", "c", "e", "f", "g"}) == 3 / 5
    assert bs.phi({"a", "c", "e", "f", "g", "b"}) == 0

def test_bounded_ballots_validity():
    e = make_dummy_election(3, 'boundedApprovalBallot', ['a', 'b', 'c', 'd', 'f', 'g'])
    bs1 = BoundedSet(2, 3, 3, {"a", "b", "c", "d"})
    bs2 = BoundedSet(1, 1, 1, {"f", "g"})
    bs3 = BoundedSet(1, 1, 1, {"e", "f", "g"})

    make_bounded_ballot(bs1, bs2) # should be fine; ballots non-overlapping, candidates ok
    with pytest.raises(Exception): # ballots are overlapping
        make_bounded_ballot(bs1, bs2, bs3)

def test_bounded_ballots_score():
    ballot = make_bounded_ballot(BoundedSet(1,2,3,{'a', 'b', 'c', 'd'}), BoundedSet(1,2,2,{'e', 'f'}), BoundedSet(2,3,3,{'g', 'h', 'i'}))
    assert ballot.score({"a", "b", "f", "g"}) == 3
    assert ballot.score({"a", "b", "e", "f"}) == 4
    assert ballot.score({"a", "b", "c", "e", "f"}) == 4
    assert ballot.score({"a", "b", "c", "d", "e", "f"}) == 2
    assert ballot.score({"a", "g"}) == 1
    assert ballot.score({"a", "g", "i"}) == 3

def test_bounded_ballot_involved_candidates():
    ballot = make_bounded_ballot(BoundedSet(1,2,3,{'a', 'b', 'c', 'd'}), BoundedSet(1,2,2,{'e', 'f'}))
    assert ballot.get_involved_candidates() == {'a', 'b', 'c', 'd', 'e', 'f'}





"""
    Tests for regular Approval Ballot
"""

def test_approval_ballots_score():
    ballot = make_approval_ballot(['a', 'b', 'c'])
    assert ballot.score({"a", "b", "f", "g"}) == 2
    assert ballot.score({"a", "b", "c", "f"}) == 3
    assert ballot.score({"e", "f"}) == 0

def test_approval_ballots_decode():
    ballot = make_approval_ballot(['a', 'b', 'c'])
    assert ballot._decode() == {'a', 'b', 'c'}

def test_approval_ballots_involved_candidates():
    ballot = make_approval_ballot(['a', 'b', 'c'])
    assert ballot.get_involved_candidates() == {'a', 'b', 'c'}