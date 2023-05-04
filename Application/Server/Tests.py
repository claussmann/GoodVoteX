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
    Tests for Service
"""

def test_import_export():
    e = Election(42, "This Year Food Selection: What should be served?", "You decide on Food: Banana, or Fish? Döner?", {"a", "b", "c", "d", "e", "f", "g"}, 3)
    e.add_ballot([BoundedSet(1,2,4,{"a", "b", "c", "f"}), BoundedSet(1,1,2,{"d", "g"})])
    e.add_ballot([BoundedSet(1,1,1,{"a", "b", "c"})])
    save_to_file(e)
    e2 = load_from_file(storage_path + "42.json")
    os.remove(storage_path + "42.json")
    assert e2.name == e.name
    assert e2.eid == e.eid
    assert e2.description == e.description
    assert e2.K == e.K
    assert e2.candidates == e.candidates

def test_register_delete():
    e1 = register_election("Test 42", "A test election.", ["a", "b", "c", "d"], 3)
    assert str(e1.eid) + ".json" in [f for f in os.listdir(storage_path) if f.endswith(".json")]

    with pytest.raises(Exception):
        e2 = register_election("Test 43", "A second test election.", ["a", "b", "c"], 3) # should fail because too small K
    
    delete(e1.eid, e1.evaluation_token)
    assert str(e1.eid) + ".json" not in [f for f in os.listdir(storage_path) if f.endswith(".json")]

def test_election_not_exists():
    with pytest.raises(Exception):
        e = get_election("abcdef")

def test_wrong_token():
    e1 = register_election("Test 42", "A test election.", ["a", "b", "c", "d"], 3)
    with pytest.raises(Exception):
        verify_token(e1, "379289ehj")
    delete(e1.eid, e1.evaluation_token)

def test_search():
    e1 = register_election("Test Election Major 2023", "A test election for who will become major!", ["a", "b", "c", "d"], 2)
    e2 = register_election("Election Junior", "Who will become junior in our test?", ["a", "b", "c", "d"], 2)
    e3 = register_election("Is Gollum an animal?", "New date received: DNA Test positive!", ["a", "b", "c", "d"], 2)
    e4 = register_election("What to take on mars", "New Mars mission!", ["a", "b", "c", "d"], 2)

    search_res = search("Major test election")
    assert len(search_res) == 3
    assert search_res[0] == e1 # Keywords: "Major", "Test", "Election"
    assert search_res[1] == e2 # Keywords: "Election", "Test"
    assert search_res[2] == e3 # Keyword: "Test"
    assert e4 not in search_res # No keywords
    
    delete(e1.eid, e1.evaluation_token)
    delete(e2.eid, e2.evaluation_token)
    delete(e3.eid, e3.evaluation_token)
    delete(e4.eid, e4.evaluation_token)