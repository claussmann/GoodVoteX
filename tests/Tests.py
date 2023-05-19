from pathlib import Path

from .context import goodvotes
from goodvotes.voting.models import *
import pytest
import os

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

def test_bounded_sets_encode_correctly():
    bs1 = BoundedSet(2, 3, 3, {"a", "b", "c", "d"})
    bs2 = BoundedSet(1, 1, 1, {"f", "g"})
    ballot = BoundedApprovalBallot()
    ballot.encode([bs1, bs2])
    assert [bs1, bs2] == ballot._decode()

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

    ballot = BoundedApprovalBallot()
    ballot.election = e
    ballot.encode([bs1, bs2])
    assert ballot.check_validity() # should be fine; ballots non-overlapping, candidates ok

    ballot = BoundedApprovalBallot()
    ballot.election = e
    ballot.encode([bs1, bs2, bs3])
    assert not ballot.check_validity() # ballots are overlapping

    ballot = BoundedApprovalBallot()
    ballot.election = e
    ballot.encode([bs1, bs3])
    assert not ballot.check_validity() # candidate "e" doesn't exist

def test_bounded_ballots_score():
    bs1 = BoundedSet(1, 2, 3, {"a", "b", "c", "d"})
    bs2 = BoundedSet(1, 2, 2, {"e", "f"})
    bs3 = BoundedSet(2, 3, 3, {"g", "h", "i"})

    ballot = BoundedApprovalBallot()
    ballot.encode([bs1, bs2, bs3])
    assert ballot.score({"a", "b", "f", "g"}) == 3
    assert ballot.score({"a", "b", "e", "f"}) == 4
    assert ballot.score({"a", "b", "c", "e", "f"}) == 4
    assert ballot.score({"a", "b", "c", "d", "e", "f"}) == 2
    assert ballot.score({"a", "g"}) == 1
    assert ballot.score({"a", "g", "i"}) == 3

# """
#     Tests for Election
# """


# def test_search_relevance():
#     e = Election(42, "This Year Food Selection: What should be served?", "You decide on Food: Banana, or Fish? Döner?",
#                  {"a", "b", "c", "d", "e"}, 3)
#     assert e.search_relevance("Food") == 1
#     assert e.search_relevance("fOod") == 1
#     assert e.search_relevance("Food Selection?") == 2
#     assert e.search_relevance("You be or Banana") == 1
#     assert e.search_relevance("Apple") == 0
#     assert e.search_relevance("be") == 0  # short words are ignored
#     assert e.search_relevance("döner") == 1
#     assert e.search_relevance("What should be served? Banana or Fish?") == 5
#     assert e.search_relevance("42") == 100


# def test_election_accepts_only_disjoint_sets():
#     e = Election(42, "Test", "Testo", {"a", "b", "c", "e", "f", "g", "h", "w", "x", "y"}, 3)
#     b1 = BoundedSet(1, 1, 3, {"a", "b", "c"})
#     b2 = BoundedSet(1, 2, 3, {"e", "f", "g", "h"})
#     b3 = BoundedSet(1, 3, 4, {"w", "x", "y"})
#     b4 = BoundedSet(1, 1, 1, {"a", "e", "g"})
#     with pytest.raises(Exception):
#         e.add_ballot([b1, b2, b4])
#     e.add_ballot([b1, b2, b3])


# def test_score():
#     e = Election(42, "Test", "Testo", {"a", "b", "c", "e", "f", "g", "h", "w", "x", "y", "z"}, 3)
#     b1 = BoundedSet(1, 1, 3, {"a", "b", "c"})
#     b2 = BoundedSet(1, 2, 3, {"e", "f", "g", "h"})
#     b3 = BoundedSet(2, 2, 3, {"w", "x", "y", "z"})
#     e.add_ballot([b1, b2, b3])

#     assert e.score({"a", "b", "c"}) == 1
#     assert e.score({"a", "b", "y", "z", "e"}) == 4
#     assert e.score({"a", "b", "y", "e"}) == 2
#     assert e.score({"a", "w", "x", "y"}) == 3
#     assert e.score({"a", "w", "x", "y", "z"}) == 1


# def test_stop_election():
#     e = Election(42, "Test", "Testo", {"a", "b", "c", "d"}, 2)
#     b1 = BoundedSet(1, 1, 2, {"a", "b"})
#     b2 = BoundedSet(1, 2, 2, {"c", "d"})
#     e.add_ballot([b1, b2])
#     e.stop()

#     with pytest.raises(Exception):
#         e.add_ballot([b1, b2])


# """
#     Tests for User
# """


# def test_password_auth():
#     u = User("admin", "Administrator Rex", "admin123")
#     assert u.check_password("admin123")
#     assert not u.check_password("armin1234")


# def test_password_length():
#     with pytest.raises(Exception):
#         u = User("admin", "Administrator Rex", "n123")  # too short
#     with pytest.raises(Exception):
#         u = User("admin", "Administrator Rex", "1234567890a1234567890a1234567890a1234567890a")  # too long


# """
#     Tests for DB
# """


# def test_import_export_election():
#     e = Election(42, "This Year Food Selection: What should be served?", "You decide on Food: Banana, or Fish? Döner?",
#                  {"a", "b", "c", "d", "e", "f", "g"}, 3)
#     db.add_election(e)
#     e.add_ballot([BoundedSet(1, 2, 4, {"a", "b", "c", "f"}), BoundedSet(1, 1, 2, {"d", "g"})])
#     e.add_ballot([BoundedSet(1, 1, 1, {"a", "b", "c"})])
#     db.sync_election(e.eid)

#     db2 = JSONFileStorage(Path(__file__).parent / "storage/2")
#     e2 = db.get_election("42")
#     assert e2.name == e.name
#     assert e2.eid == e.eid
#     assert e2.description == e.description
#     assert e2.K == e.K
#     assert e2.candidates == e.candidates
#     assert len(e2.__ballots__) == len(e.__ballots__)
#     db.dump()


# def test_import_export_user():
#     u = User("admin", "Administrator Rex", "admin123")
#     db.add_user(u)

#     db2 = JSONFileStorage(Path(__file__).parent / "storage/2")
#     u2 = db.get_user("admin")
#     assert u2.name == u.name
#     assert u2.username == u.username
#     assert u2.password_hash == u.password_hash
#     assert u2.salt == u.salt
#     db.dump()


# def test_delete_election():
#     e = Election(42, "This Year Food Selection: What should be served?", "You decide on Food: Banana, or Fish? Döner?",
#                  {"a", "b", "c", "d", "e", "f", "g"}, 3)
#     db.add_election(e)
#     assert str(e.eid) + ".json" in [f for f in os.listdir(db.election_storage_path) if f.endswith(".json")]
#     db.delete_election(e.eid)
#     assert str(e.eid) + ".json" not in [f for f in os.listdir(db.election_storage_path) if f.endswith(".json")]
#     db.dump()


# def test_delete_user():
#     u = User("admini", "Administrator Rex", "admin123")
#     db.add_user(u)
#     assert str(u.username) + ".json" in [f for f in os.listdir(db.user_storage_path) if f.endswith(".json")]
#     db.delete_user(u.username)
#     assert str(u.username) + ".json" not in [f for f in os.listdir(db.user_storage_path) if f.endswith(".json")]
#     db.dump()


# def test_election_not_exists():
#     with pytest.raises(Exception):
#         db.get_election("abcdef")


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
