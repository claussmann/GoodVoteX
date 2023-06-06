from pathlib import Path

from .context import goodvotes
from goodvotes.voting.models import *
from goodvotes.auth.models import *
import pytest
import os



# @pytest.fixture()
# def app():
#     app = goodvotes.create_app()
#     app.config.update({
#         "TESTING": True,
#     })
#     with app.app_context():
#         db.create_all()
    
#     yield app





"""
    Tests for Bounded Set
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


"""
    Tests for BoundedApprovalBallot
"""

def test_bounded_ballots_validity():
    e = Election()
    e.candidates = [Candidate() for i in range(6)]
    e.candidates[0].id = "a"
    e.candidates[1].id = "b"
    e.candidates[2].id = "c"
    e.candidates[3].id = "d"
    e.candidates[4].id = "f"
    e.candidates[5].id = "g"
    bs1 = BoundedSet(2, 3, 3, {"a", "b", "c", "d"})
    bs2 = BoundedSet(1, 1, 1, {"f", "g"})
    bs3 = BoundedSet(1, 1, 1, {"e", "f", "g"})

    json_content = {'sets' : {'bs1' : ['a', 'b', 'c', 'd'], 'bs2' : ['f', 'g']}, 
                'bounds' : {'bs1' : [2,3,3], 'bs2' : [1,1,1]}}
    ballot = BoundedApprovalBallot(json_content)
    ballot.election = e
    assert ballot.check_validity() # should be fine; ballots non-overlapping, candidates ok

    json_content = {'sets' : {'bs1' : ['a', 'b', 'c', 'd'], 'bs2' : ['f', 'g'], 'bs3' : ['e', 'f', 'g']}, 
                'bounds' : {'bs1' : [2,3,3], 'bs2' : [1,1,1], 'bs3' : [1,1,1]}}
    ballot = BoundedApprovalBallot(json_content)
    ballot.election = e
    assert not ballot.check_validity() # ballots are overlapping

    json_content = {'sets' : {'bs1' : ['a', 'b', 'c', 'd'], 'bs3' : ['e', 'f', 'g']}, 
                'bounds' : {'bs1' : [2,3,3], 'bs3' : [1,1,1]}}
    ballot = BoundedApprovalBallot(json_content)
    ballot.election = e
    assert not ballot.check_validity() # candidate "e" doesn't exist

def test_bounded_ballots_score():
    json_content = {'sets' : {'bs1' : ['a', 'b', 'c', 'd'], 'bs2' : ['e', 'f'], 'bs3' : ['g', 'h', 'i']}, 
                'bounds' : {'bs1' : [1,2,3], 'bs2' : [1,2,2], 'bs3' : [2,3,3]}}
    ballot = BoundedApprovalBallot(json_content)
    assert ballot.score({"a", "b", "f", "g"}) == 3
    assert ballot.score({"a", "b", "e", "f"}) == 4
    assert ballot.score({"a", "b", "c", "e", "f"}) == 4
    assert ballot.score({"a", "b", "c", "d", "e", "f"}) == 2
    assert ballot.score({"a", "g"}) == 1
    assert ballot.score({"a", "g", "i"}) == 3

"""
    Tests for ApprovalBallot
"""

def test_approval_ballots_score():
    json_content = {'app_candidates' : ['a', 'b', 'c']}
    ballot = ApprovalBallot(json_content)
    assert ballot.score({"a", "b", "f", "g"}) == 2
    assert ballot.score({"a", "b", "c", "f"}) == 3
    assert ballot.score({"e", "f"}) == 0

"""
    Tests for Election
"""


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


# def test_election_accepts_only_valid_sets(app):
#     with app.app_context():
#         u = User(name="Peter", username="dieter", email="foo@bar.de", password_hash="123")
#         db.session.add(u)
#         e = Election(title="foo bar", description="bar fo lorem", committeesize=2)
#         for c in {"a", "b", "c", "d", "e", "f", "g", "h", "w", "x", "y"}:
#             e.candidates.append(Candidate(name=c))
#         u.elections.append(e)
#         db.session.add(e)
#         db.session.commit()
        
#         bs1 = BoundedSet(1, 1, 3, {"a", "b", "c"})
#         bs2 = BoundedSet(1, 2, 3, {"e", "f", "g", "h"})
#         bs3 = BoundedSet(1, 3, 4, {"w", "x", "y"})
#         bs4 = BoundedSet(1, 1, 1, {"a", "e", "g"})
#         bs5 = BoundedSet(1, 1, 1, {"a", "z"})

    
#         b1 = BoundedApprovalBallot()
#         b1.encode([bs1, bs2, bs4]) # overlapping
#         with pytest.raises(Exception):
#             e.add_ballot(b1)

#         b2 = BoundedApprovalBallot()
#         b2.encode([bs1, bs2, bs3]) # should be ok
#         e.add_ballot(b2)

#         b3 = BoundedApprovalBallot()
#         b3.encode([bs1, bs5]) # candidate "z" doesn't exist
#         with pytest.raises(Exception):
#             e.add_ballot(b3)


def test_score():
    e = Election()
    e.id = 42
    e.title = "This Year Food Selection: What should be served?"
    e.description = "You decide on Food: Banana, or Fish? Döner?"
    e.candidates = [Candidate() for i in range(9)]
    e.candidates[0].id = "a"
    e.candidates[1].id = "b"
    e.candidates[2].id = "c"
    e.candidates[3].id = "d"
    e.candidates[4].id = "e"
    e.candidates[5].id = "f"
    e.candidates[6].id = "g"
    e.candidates[7].id = "h"
    e.candidates[8].id = "i"
    
    json_content = {'sets' : {'bs1' : ['a', 'b', 'c', 'd'], 'bs2' : ['e', 'f']}, 
                'bounds' : {'bs1' : [1,2,3], 'bs2' : [1,2,2]}}
    b1 = BoundedApprovalBallot(json_content)
    json_content = {'sets' : {'bs1' : ['a', 'b', 'c', 'd'], 'bs3' : ['g', 'h', 'i']}, 
                'bounds' : {'bs1' : [1,2,3], 'bs3' : [2,3,3]}}
    b2 = BoundedApprovalBallot(json_content)
    e.ballots = [b1, b2]

    assert e.score({e.candidates[0], e.candidates[1], e.candidates[2], e.candidates[5], e.candidates[7]}) == 5

# """
#     Tests for service
# """


# def test_search():
#     service.db = JSONFileStorage(Path(__file__).parent / "storage/1")
#     u = service.register_user("aDmin", "Testosaurus", "adminiissttr")
#     e1 = service.register_election("Test Election Major 2023", "A test election for who will become major!",
#                                    ["a", "b", "c", "d"], 2, u)
#     e2 = service.register_election("Election Junior", "Who will become junior in our test?", ["a", "b", "c", "d"], 2, u)
#     e3 = service.register_election("Is Gollum an animal?", "New date received: DNA Test positive!",
#                                    ["a", "b", "c", "d"], 2, u)
#     e4 = service.register_election("What to take on mars", "New Mars mission!", ["a", "b", "c", "d"], 2, u)

#     search_res = service.search("Major test election")
#     assert len(search_res) == 3
#     assert search_res[0] == e1  # Keywords: "Major", "Test", "Election"
#     assert search_res[1] == e2  # Keywords: "Election", "Test"
#     assert search_res[2] == e3  # Keyword: "Test"
#     assert e4 not in search_res  # No keywords

#     service.db.dump()
