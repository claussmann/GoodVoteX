from Service import *
import pytest
import os


"""
    Tests for Bounded Set
"""

def test_create_bounded_set():
    bs = BoundedSet(1,3,4,"a", "b", "c")
    assert bs.lower == 1
    assert bs.saturation == 3
    assert bs.upper == 4
    assert "a" in bs
    assert "c" in bs

def test_create_bounded_set_from_set():
    bs = BoundedSet(1,3,4,{"a", "b", "c"})
    assert bs.lower == 1
    assert bs.saturation == 3
    assert bs.upper == 4
    assert "a" in bs
    assert "c" in bs

def test_bounded_set_to_string():
    bs = BoundedSet(1,3,4,{"a", "b", "c"})
    assert str(bs) == "<{'a', 'b', 'c'}, 1, 3, 4>"
    bs = BoundedSet(1,3,4,"b", "c", "a")
    assert str(bs) == "<{'a', 'b', 'c'}, 1, 3, 4>"

def test_bounded_set_iterator():
    x = set()
    bs = BoundedSet(1,3,4,{"a", "b", "c"})
    for a in bs:
        x.add(a)
    assert x == {"a", "b", "c"}
    assert len(bs) == 3

def test_bounded_set_intersection():
    b1 = BoundedSet(1,3,3,{"a", "b", "c"})
    b2 = BoundedSet(1,1,2,{"c", "d"})
    b3 = BoundedSet(1,3,4,{"e", "f", "g", "h"})
    b4 = BoundedSet(1,2,3,{"a", "b", "c"})
    s5 = {"b", "d", "g", "h"}

    assert b1.is_disjoint(b3)
    assert b1.intersection_size(b2) == 1
    assert b1.intersection_size(b4) == 3
    assert b1.intersection_size(s5) == 1
    assert b3.intersection_size(s5) == 2

def test_bounded_set_equals():
    b1 = BoundedSet(1,3,3,{"a", "b", "c"})
    b2 = BoundedSet(1,3,3,{"a", "b", "c"})
    b3 = BoundedSet(1,3,3,{"e", "b", "c"})
    b4 = BoundedSet(1,1,3,{"a", "b", "c"})

    assert b1 == b2
    assert b1 != b3
    assert b1 != b4

def test_bounded_set_phi():
    bs = BoundedSet(2,3,5,{"a", "b", "c", "d", "e", "f", "g"})
    assert bs.phi({"a"}) == 0
    assert bs.phi({"a", "c"}) == 1
    assert bs.phi({"a", "c", "e"}) == 1
    assert bs.phi({"a", "c", "e", "f"}) == 3/4
    assert bs.phi({"a", "c", "e", "f", "g"}) == 3/5
    assert bs.phi({"a", "c", "e", "f", "g", "b"}) == 0




"""
    Tests for Election
"""

def test_search_relevance():
    e = Election(42, "This Year Food Selection: What should be served?", "You decide on Food: Banana, or Fish? Döner?", {"a", "b", "c", "d", "e"}, 3)
    assert e.search_relevance("Food") == 1
    assert e.search_relevance("fOod") == 1
    assert e.search_relevance("Food Selection?") == 2
    assert e.search_relevance("You be or Banana") == 1
    assert e.search_relevance("Apple") == 0
    assert e.search_relevance("be") == 0 # short words are ignored
    assert e.search_relevance("döner") == 1
    assert e.search_relevance("What should be served? Banana or Fish?") == 5
    assert e.search_relevance("42") == 100

def test_election_accepts_only_disjoint_sets():
    e = Election(42, "Test", "Testo", {"a", "b", "c", "e", "f", "g", "h", "w", "x", "y"}, 3)
    b1 = BoundedSet(1,1,3,{"a", "b", "c"})
    b2 = BoundedSet(1,2,3,{"e", "f", "g", "h"})
    b3 = BoundedSet(1,3,4,{"w", "x", "y"})
    b4 = BoundedSet(1,1,1,{"a", "e", "g"})
    with pytest.raises(Exception):
        e.add_ballot([b1, b2, b4])
    e.add_ballot([b1, b2, b3])

def test_score():
    e = Election(42, "Test", "Testo", {"a", "b", "c", "e", "f", "g", "h", "w", "x", "y", "z"}, 3)
    b1 = BoundedSet(1,1,3,{"a", "b", "c"})
    b2 = BoundedSet(1,2,3,{"e", "f", "g", "h"})
    b3 = BoundedSet(2,2,3,{"w", "x", "y", "z"})
    e.add_ballot([b1, b2, b3])

    assert e.score({"a", "b", "c"}) == 1
    assert e.score({"a", "b", "y", "z", "e"}) == 4
    assert e.score({"a", "b", "y", "e"}) == 2
    assert e.score({"a", "w", "x", "y"}) == 3
    assert e.score({"a", "w", "x", "y", "z"}) == 1

def test_stop_election():
    e = Election(42, "Test", "Testo", {"a", "b", "c", "d"}, 2)
    b1 = BoundedSet(1,1,2,{"a", "b"})
    b2 = BoundedSet(1,2,2,{"c", "d"})
    e.add_ballot([b1, b2])
    e.stop()

    with pytest.raises(Exception):
        e.add_ballot([b1, b2])


"""
    Tests for User
"""

def test_password_auth():
    u = User("admin", "Administrator Rex", "admin123")
    assert u.check_password("admin123")
    assert not u.check_password("armin1234")

def test_password_length():
    with pytest.raises(Exception):
        u = User("admin", "Administrator Rex", "n123") # too short
    with pytest.raises(Exception):
        u = User("admin", "Administrator Rex", "1234567890a1234567890a1234567890a1234567890a") # too long


"""
    Tests for Service
"""

def test_import_export_election():
    e = Election(42, "This Year Food Selection: What should be served?", "You decide on Food: Banana, or Fish? Döner?", {"a", "b", "c", "d", "e", "f", "g"}, 3)
    e.add_ballot([BoundedSet(1,2,4,{"a", "b", "c", "f"}), BoundedSet(1,1,2,{"d", "g"})])
    e.add_ballot([BoundedSet(1,1,1,{"a", "b", "c"})])
    save_election_to_file(e)
    e2 = load_election_from_file(election_storage_path + "42.json")
    os.remove(election_storage_path + "42.json")
    assert e2.name == e.name
    assert e2.eid == e.eid
    assert e2.description == e.description
    assert e2.K == e.K
    assert e2.candidates == e.candidates

def test_import_export_user():
    u = User("admin", "Administrator Rex", "admin123")
    save_user_to_file(u)
    u2 = load_user_from_file(user_storage_path + "admin.json")
    os.remove(user_storage_path + "admin.json")
    assert u2.name == u.name
    assert u2.username == u.username
    assert u2.password_hash == u.password_hash
    assert u2.salt == u.salt

def test_register_delete_election():
    u = User("admin", "Administrator Rex", "admin123")
    e1 = register_election("Test 42", "A test election.", ["a", "b", "c", "d"], 3, u)
    assert str(e1.eid) + ".json" in [f for f in os.listdir(election_storage_path) if f.endswith(".json")]

    with pytest.raises(Exception):
        e2 = register_election("Test 43", "A second test election.", ["a", "b", "c"], 3, u) # should fail because too small K
    
    delete_election(e1.eid, u)
    os.remove(user_storage_path + "admin.json")
    assert str(e1.eid) + ".json" not in [f for f in os.listdir(election_storage_path) if f.endswith(".json")]

def test_register_delete_user():
    u1 = register_user("aDmin", "Testosaurus", "adminiissttr")

    with pytest.raises(Exception):
        u2 = register_user("admin", "Mr Smith", "kjfhnasdjjnj") # should fail because same username
    
    assert u1 == get_user("AdMIN") # lower/upper case doesn't matter
    
    delete_user("admin")
    assert "admin.json" not in [f for f in os.listdir(user_storage_path) if f.endswith(".json")]

def test_election_not_exists():
    with pytest.raises(Exception):
        e = get_election("abcdef")

def test_wrong_user():
    u1 = register_user("aDmin", "Testosaurus", "adminiissttr")
    u2 = register_user("peter", "Testosaurus", "adminiissttr")
    e1 = register_election("Test 42", "A test election.", ["a", "b", "c", "d"], 3, u1)
    with pytest.raises(Exception):
        delete_election(e1.eid, u2)
    delete_election(e1.eid, u1)
    delete_user("admin")
    delete_user("peter")


def test_search():
    u = register_user("aDmin", "Testosaurus", "adminiissttr")
    e1 = register_election("Test Election Major 2023", "A test election for who will become major!", ["a", "b", "c", "d"], 2, u)
    e2 = register_election("Election Junior", "Who will become junior in our test?", ["a", "b", "c", "d"], 2, u)
    e3 = register_election("Is Gollum an animal?", "New date received: DNA Test positive!", ["a", "b", "c", "d"], 2, u)
    e4 = register_election("What to take on mars", "New Mars mission!", ["a", "b", "c", "d"], 2, u)

    search_res = search("Major test election")
    assert len(search_res) == 3
    assert search_res[0] == e1 # Keywords: "Major", "Test", "Election"
    assert search_res[1] == e2 # Keywords: "Election", "Test"
    assert search_res[2] == e3 # Keyword: "Test"
    assert e4 not in search_res # No keywords
    
    delete_election(e1.eid, u)
    delete_election(e2.eid, u)
    delete_election(e3.eid, u)
    delete_election(e4.eid, u)
    delete_user("admin")
