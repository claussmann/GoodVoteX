from .context import goodvotex
from goodvotex.voting import service
from goodvotex.voting.models import *

import pytest
from unittest.mock import Mock, patch

service.db = Mock()
service.db.session.add.return_value = 0
service.db.session.commit.return_value = 0

class Mock_User():
    def __init__(self):
        self.elections = list()
    
    def owns_election(self, election):
        return election in self.elections

def test_register_election():
    u = Mock_User()
    service.register_election('savElection', 'Foo', 'Bar', ['a', 'b', 'c'], 2, u)
    e = u.elections[0]
    assert e.title == "Foo"
    assert len(e.candidates) == 3
    assert e.type == "savElection"
    assert service.db.session.add.called
    assert service.db.session.commit.called

@patch('goodvotex.voting.service.get_all_elections')
def test_service_search(mock_get_elections):
    mock_get_elections.return_value = [
        Election(id=42, title="Food Competition", description="Banana, or Apples? Pineapple?"),
        Election(id=43, title="This Year Food Selection: What should be served?", description="You decide on Food: Banana, or Fish? Döner?"),
        Election(id=44, title="Conference Dinner: What should be served?", description="You decide.")]
    
    results = service.search("Food Selection")
    assert results[0].id == 43
    assert results[1].id == 42
    assert len(results) == 2

    with pytest.raises(Exception): # Search string too long
        service.search("A"*70)

@patch('goodvotex.voting.service.get_election')
def test_service_add_vote(mock_get_election):
    e = ApprovalElection(id=42, candidates=[Candidate(id='a'), Candidate(id='b'), Candidate(id='c')], ballots=list(), votecount=0)
    mock_get_election.return_value = e
    service.add_vote_from_json(42, {'type' : 'approvalBallot', 'app_candidates' : ['a', 'b']})
    assert e.ballots[0].get_involved_candidates() == {'a', 'b'}

@patch('goodvotex.voting.service.get_election')
def test_service_add_invalid_vote(mock_get_election):
    e = ApprovalElection(id=42, candidates=[Candidate(id='a'), Candidate(id='b'), Candidate(id='c')], ballots=list(), votecount=0)
    mock_get_election.return_value = e
    with pytest.raises(Exception): # wrong ballot type
        service.add_vote_from_json(42, {'type' : 'cardinalBallot', 'order' : ['a', 'b']})

    with pytest.raises(Exception): # Candidate not in election
        service.add_vote_from_json(42, {'type' : 'approvalBallot', 'app_candidates' : ['a','e']})

@patch('goodvotex.voting.service.get_election')
def test_service_stop_election(mock_get_election):
    e = Election(id=42, is_stopped=False)
    mock_get_election.return_value = e
    u = Mock_User()
    u.elections.append(e)
    service.stop_election(42, u)
    assert service.db.session.add.called
    assert service.db.session.commit.called

@patch('goodvotex.voting.service.get_election')
def test_service_stop_election_invalid_user(mock_get_election):
    e = Election(id=42, is_stopped=False)
    mock_get_election.return_value = e
    u = Mock_User() # user does not own election
    with pytest.raises(Exception):
        service.stop_election(42, u)


@patch('goodvotex.voting.service.get_election')
def test_service_evaluate_election(mock_get_election):
    e = ApprovalElection(id=42, committeesize=2, candidates=[Candidate(id='a'), Candidate(id='b'), Candidate(id='c')], ballots=list(), votecount=0)
    e.ballots.append(ApprovalBallot({'app_candidates' : ['a', 'c'], 'type' : 'approvalBallot'}))
    mock_get_election.return_value = e
    u = Mock_User()
    u.elections.append(e)
    service.evaluate(42, u)
    assert service.db.session.add.called
    assert service.db.session.commit.called
    assert {str(c.id) for c in e.get_winners()} == {'a', 'c'}

@patch('goodvotex.voting.service.get_election')
def test_service_delete_election_invalid_user(mock_get_election):
    e = Election(id=42, is_stopped=False)
    mock_get_election.return_value = e
    u = Mock_User() # user does not own election
    with pytest.raises(Exception):
        service.delete_election(42, u)
