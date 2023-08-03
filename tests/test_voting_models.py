from .context import goodvotex
from goodvotex.voting.models import *

import pytest


#################################################################################
#                 Helpers
#################################################################################

def make_dummy_election(cosntructor, committeesize, candidate_ids):
    e = cosntructor(title="Test", description="test", committeesize=committeesize,
                is_stopped=False, votecount=0, ballots=list())
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
        'sets' : {"bs1": ["a", "a", "b", "c"], "bs2": ["x", "y"], "bs3": ["d"], "bs4": ["e", "f", "g"]},
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

def test_bounded_approval_ballot_forbidden_ballots():
    json_content1 = {
        'sets' : {"bs1": ["a", "b", "c"], "bs2": ["a", "b"], "bs3": ["d"]},
        'bounds' : {"bs1": [1, 2, 3], "bs2": [1, 1, 1], "bs3": [1, 1, 1]}
    }
    ballot = BoundedApprovalBallot(json_content1)
    assert not ballot._check_validity() # not disjoint

    json_content2 = {
        'sets' : {"bs1": ["a", "b", "c"], "bs2": ["d", "e"], "bs3": ["f"]},
        'bounds' : {"bs1": [1, 2, 3], "bs2": [1, 1, 1], "bs3": [2, 2, 2]}
    }
    ballot = BoundedApprovalBallot(json_content2)
    assert not ballot._check_validity() # lower bound too high

    json_content3 = {
        'sets' : {"bs1": ["a", "b", "c"], "bs2": ["d", "e"]},
        'bounds' : {"bs1": [1, 2, 3], "bs2": [2, 1, 2]}
    }
    ballot = BoundedApprovalBallot(json_content3)
    assert not ballot._check_validity() # lower bound higher than saturation

    json_content4 = {
        'sets' : {"bs1": ["a", "b", "c"], "bs2": ["d", "e"]},
        'bounds' : {"bs1": [1, 2, 3], "bs2": [1, 1]}
    }
    ballot = BoundedApprovalBallot(json_content4)
    assert not ballot._check_validity() # incomplete bounds


#################################################################################
#                 Elections
#################################################################################

def test_general_election_methods_start_stop():
    e = Election(title="Test", description="test", committeesize=2, is_stopped=False, ballots=list(), votecount=0)
    e.stop()
    assert e.is_stopped == True
    with pytest.raises(Exception):
        e.add_ballot(ApprovalBallot({"app_candidates" : ["1", "2", "3"]}))
    e.restart()
    assert e.is_stopped == False
    e.add_ballot(ApprovalBallot({"app_candidates" : ["1", "2", "3"]}))
    assert e.votecount == 1

def test_general_election_methods_search_relevance():
    e = Election(title="This Year Food Selection: What should be served?",
                 description="You decide on Food: Banana, or Fish? Döner",
                 id=42)
    assert e.search_relevance("Food") == 1
    assert e.search_relevance("fOod") == 1
    assert e.search_relevance("Food Selection?") == 2
    assert e.search_relevance("You be or Banana") == 1
    assert e.search_relevance("Apple") == 0
    assert e.search_relevance("be") == 0  # short words are ignored
    assert e.search_relevance("döner") == 1
    assert e.search_relevance("What should be served? Banana or Fish?") == 5
    assert e.search_relevance("42") == 100

def test_approval_election_compute_winners():
    e = make_dummy_election(ApprovalElection, 3, ["a", "b", "c", "d", "e", "f"])
    e.add_ballot(ApprovalBallot({"app_candidates" : ["a", "b", "e"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["a", "e"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["c", "f"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["e"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["c"]}))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"a", "c", "e"}

def test_approval_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(ApprovalElection, 3, ["a", "b", "c", "d", "e", "f"])
    with pytest.raises(Exception):
        e.add_ballot(ApprovalBallot({"app_candidates" : ["x", "b"]})) # x is no candidate
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1}})) # no approval ballot

def test_sav_election_compute_winners():
    e = make_dummy_election(SAVElection, 2, ["a", "b", "c", "d", "e", "f"])
    e.add_ballot(ApprovalBallot({"app_candidates" : ["a", "b", "e"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["a", "e"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["d", "e", "f"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["c"]}))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"c", "e"}

def test_sav_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(SAVElection, 3, ["a", "b", "c", "d", "e", "f"])
    with pytest.raises(Exception):
        e.add_ballot(ApprovalBallot({"app_candidates" : ["x", "b"]})) # x is no candidate
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1}})) # no approval ballot

def test_pav_election_compute_winners():
    e = make_dummy_election(PAVElection, 3, ["a", "b", "c", "d", "e"])
    e.add_ballot(ApprovalBallot({"app_candidates" : ["a", "b", "e"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["a", "e"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["d", "e"]}))
    e.add_ballot(ApprovalBallot({"app_candidates" : ["c"]}))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"a", "e", "c"}

def test_pav_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(PAVElection, 3, ["a", "b", "c", "d", "e", "f"])
    with pytest.raises(Exception):
        e.add_ballot(ApprovalBallot({"app_candidates" : ["x", "b"]})) # x is no candidate
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1}})) # no approval ballot

def test_bounded_ballot_election_compute_winners():
    e = make_dummy_election(BoundedApprovalElection, 3, ["a", "b", "c", "d", "e"])
    json_content1 = {
        'sets' : {"bs1": ["a", "c"], "bs2": ["d", "e"]},
        'bounds' : {"bs1": [1, 2, 2], "bs2": [1, 1, 1]}
    }
    json_content2 = {
        'sets' : {"bs2": ["a", "b"], "bs3": ["c", "d"]},
        'bounds' : {"bs2": [1, 1, 2], "bs3": [2, 2, 2]}
    }
    e.add_ballot(BoundedApprovalBallot(json_content1))
    e.add_ballot(BoundedApprovalBallot(json_content2))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"a", "c", "d"}

def test_bounded_ballot_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(BoundedApprovalElection, 3, ["a", "b", "c", "d"])
    with pytest.raises(Exception):
        json_content = {
            'sets' : {"bs1": ["a", "x"], "bs2": ["d", "y"]},
            'bounds' : {"bs1": [1, 2, 2], "bs2": [1, 1, 1]}
        }
        e.add_ballot(BoundedApprovalBallot(json_content)) # x, y are no candidates
    with pytest.raises(Exception):
        json_content = {
            'sets' : {"bs1": ["a", "b"], "bs2": ["b", "d"]},
            'bounds' : {"bs1": [1, 2, 2], "bs2": [1, 1, 1]}
        }
        e.add_ballot(BoundedApprovalBallot(json_content)) # not disjoint
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1}})) # no bounded ballot

def test_borda_election_compute_winners():
    e = make_dummy_election(BordaElection, 2, ["a", "b", "c", "d", "e"])
    e.add_ballot(OrdinalBallot({"order" : ["b", "a", "d", "c", "e"]}))
    e.add_ballot(OrdinalBallot({"order" : ["e", "b", "a", "d", "c"]}))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"a", "b"}

def test_borda_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(BordaElection, 3, ["a", "b", "c", "d"])
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["b", "x", "d", "y", "e"]})) # x, y are no candidates
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["b", "a", "d"]})) # not complete
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1}})) # no ordinal ballot

def test_copeland_election_compute_winners():
    e = make_dummy_election(CopelandElection, 1, ["a", "b", "c", "d"])
    e.add_ballot(OrdinalBallot({"order" : ["b", "a", "d", "c"]}))
    e.add_ballot(OrdinalBallot({"order" : ["c", "a", "d", "b"]}))
    e.add_ballot(OrdinalBallot({"order" : ["b", "a", "d", "c"]}))
    e.add_ballot(OrdinalBallot({"order" : ["c", "a", "d", "b"]}))
    e.add_ballot(OrdinalBallot({"order" : ["b", "a", "d", "c"]}))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"b"}

def test_copeland_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(BordaElection, 3, ["a", "b", "c", "d"])
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["b", "x", "d", "y", "e"]})) # x, y are no candidates
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["b", "a", "d"]})) # not complete
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1}})) # no ordinal ballot

def test_borda_cc_election_compute_winners():
    e = make_dummy_election(BordaCCElection, 2, ["a", "b", "c", "d", "e"])
    e.add_ballot(OrdinalBallot({"order" : ["c", "a", "d", "b", "e"]}))
    e.add_ballot(OrdinalBallot({"order" : ["e", "b", "a", "d", "c"]}))
    e.add_ballot(OrdinalBallot({"order" : ["e", "b", "a", "d", "c"]}))
    e.add_ballot(OrdinalBallot({"order" : ["e", "b", "a", "d", "c"]}))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"c", "e"}

def test_borda_cc_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(BordaCCElection, 3, ["a", "b", "c", "d"])
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["b", "x", "d", "y", "e"]})) # x, y are no candidates
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["b", "a", "d"]})) # not complete
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1}})) # no ordinal ballot

def test_stv_election_compute_winners():
    e = make_dummy_election(STVElection, 2, ["a", "b", "c", "d", "e"])
    e.add_ballot(OrdinalBallot({"order" : ["c", "a", "d", "b", "e"]}))
    e.add_ballot(OrdinalBallot({"order" : ["e", "c", "a", "d", "b"]}))
    e.add_ballot(OrdinalBallot({"order" : ["e", "b", "a", "d", "c"]}))
    e.add_ballot(OrdinalBallot({"order" : ["e", "b", "a", "d", "c"]}))
    e.add_ballot(OrdinalBallot({"order" : ["e", "b", "a", "d", "c"]}))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"e", "c"}

def test_stv_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(STVElection, 3, ["a", "b", "c", "d"])
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["b", "x", "d", "y", "e"]})) # x, y are no candidates
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["b", "a", "d"]})) # not complete
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1}})) # no ordinal ballot

def test_utilitarian_election_compute_winners():
    e = make_dummy_election(UtilitarianElection, 2, ["a", "b", "c", "d", "e"])
    e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1, "c":5}}))
    e.add_ballot(CardinalBallot({"ratings" : {"a":3, "b":-1, "c":-1}}))
    e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1, "c":-1, "e":4}}))
    e.recompute_current_winner()
    winners = {c.id for c in e.get_winners()}
    assert winners == {"a", "e"}

def test_utilitarian_election_doesnt_accept_invalid_ballots():
    e = make_dummy_election(UtilitarianElection, 3, ["a", "b", "c", "d"])
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":1, "b":-1, "x":5}})) # x is no candidate
    with pytest.raises(Exception):
        e.add_ballot(CardinalBallot({"ratings" : {"a":100, "b":-1}})) # value too high
    with pytest.raises(Exception):
        e.add_ballot(OrdinalBallot({"order" : ["e", "b", "a", "d", "c"]})) # no cardinal ballot