import random
import json
import os
import itertools
import re

"""
The following lines are needed to initialize the database.
"""
storage_path = "../DB/"
elections = dict()







# ================================================================================
# ========================    Service Functions   ================================
# ================================================================================

"""
Registers a new election.

@return: When registration successful, returns the election object.
"""
def register_election(name, description, candidates, K):
    if len(elections) > 0xFFF:
        raise Exception("Election stroage is full.")
    new_id = "%04x" % random.randint(0, 0xFFFF)
    while new_id in elections:
        new_id = "%04x" % random.randint(0, 0xFFFF)
    e = Election(new_id, name, description, candidates, K)
    elections[new_id] = e
    save_to_file(e)
    return e

"""
@return: The election object with the given ID (if exists).
"""
def get_election(election_id):
    if election_id not in elections:
        raise Exception("This election doesn't exist: %s" % str(election_id))
    return elections[election_id]

"""
Raises an exception if token is incorrect.
"""
def verify_token(election, token):
    if token != election.evaluation_token:
        raise Exception("Incorrect Token.")

"""
Searches the database for elections which match the search string. The results are
ordered by relevance.

@return: A list of election objects.
"""
def search(search_string):
    if len(search_string) > 60: raise Exception("Search is too long.")
    ret = list()
    for election in elections.values():
        search_relevance = election.search_relevance(search_string)
        if search_relevance > 0:
            ret.append((search_relevance, election))
    return [x[1] for x in sorted(ret, key = lambda e : e[0], reverse=True)] # Sort results by relevance

"""
Adds a ballot to the given election.
"""
def add_vote(election_id, ballot):
    e = get_election(election_id)
    e.add_ballot(ballot)
    save_to_file(e)

"""
Deletes the given election. This will also delete it from the persistent storage!
"""
def delete(election_id, token):
    e = get_election(election_id)
    verify_token(e, token)
    elections.pop(election_id)
    os.remove(storage_path + election_id + ".json")

"""
Evaluates an election, i.e. computes the current winners.

@return: A dict mapping a committee-ID to committee members. Each committee
         in the dict is a winner committee (due to ties we do not always
         have a unique winner committee). The committee-IDs are known to the
         system, and can be referenced e.g. for tie-breaking in the final
         outcome.
"""
def evaluate_current_winners(election_id, token):
    e = get_election(election_id)
    verify_token(e, token)
    e.stop()
    ret = e.evaluate()
    e.restart()
    save_to_file(e)
    return ret

"""
Evaluates an election, i.e. computes the final possible winners.

@return: A dict mapping a committee-ID to committee members. Each committee
         in the dict is a winner committee (due to ties we do not always
         have a unique winner committee). The committee-IDs are known to the
         system, and can be referenced e.g. for tie-breaking in the final
         outcome.
"""
def evaluate_final_winners(election_id, token):
    e = get_election(election_id)
    verify_token(e, token)
    e.stop()
    ret = e.evaluate()
    save_to_file(e)
    return ret

"""
After evaluating the election, we can break potential ties between multiple winner-
committees by setting the committee committee-ID as the winner. This ID is retreived
from the "evaluate" function.
Note that this function also stops the election.
"""
def select_winner(election_id, token, committee_id):
    e = get_election(election_id)
    verify_token(e, token)
    e.set_winner(committee_id)
    save_to_file(e)

"""
Saves an election is JSON format to a file.
"""
def save_to_file(election):
    filename = storage_path + election.eid + ".json"
    json_str = json.dumps(election.serialize())
    f = open(filename, "w")
    f.write(json_str)
    f.close()

"""
Reads a JSON-formatted file to an election object.

@return: The election object.
"""
def load_from_file(filename):
    f = open(filename, "r")
    raw_obj = json.loads(f.read())
    e = Election(raw_obj["eid"], raw_obj["name"], raw_obj["description"], set(raw_obj["candidates"]), raw_obj["K"])
    e.evaluation_token = raw_obj["evaluation_token"]
    e.potential_winners = raw_obj["potential_winners"]
    for ballot in raw_obj["__ballots__"]:
        e.add_ballot([BoundedSet(bs["lower"], bs["saturation"], bs["upper"], *bs["set"]) for bs in ballot])
    e.is_stopped = raw_obj["is_stopped"]
    if raw_obj["is_finished"]:
        e.is_finished = True
        e.winner = raw_obj["winner"]        
    f.close()
    return e

"""
Loads all election files from the storage path to election objects in the
elections dict.
"""
def load_all():
    files = [f for f in os.listdir(storage_path) if f.endswith(".json")]
    for f in files:
        e = load_from_file(storage_path + f)
        elections[e.eid] = e












# ================================================================================
# =======================    Election Datatypes   ================================
# ===========    DO ONLY USE VIA THE SERVICE FUNCTIONS ABOVE    ==================
# ================================================================================

class BoundedSet(frozenset):
    def __new__(cls, lower, saturation, upper, *items):
        if len(items) == 1 and type(*items) == type(set()):
            this_set = super(BoundedSet, cls).__new__(cls, *items)
        else:
            this_set = super(BoundedSet, cls).__new__(cls, items)
        this_set.lower = lower
        this_set.saturation = saturation
        this_set.upper = upper
        return this_set
    
    def __str__(self):
        items = str(sorted(self)) # sort alternatives (easier debugging)
        items = items[1:-1] # cut breakets
        return "<{%s}, %d, %d, %d>" %(items, self.lower, self.saturation, self.upper)
    
    def __eq__(self, other):
        if type(other) != type(self):
            return False
        if self.lower != other.lower or self.upper != other.upper or self.saturation != other.saturation:
            return False
        if len(other) != len(self):
            return False
        for a in self:
            if a not in other:
                return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def is_disjoint(self, other):
        return len(self.intersection(other)) == 0

    def intersection_size(self, committee):
        return len(self.intersection(committee))
    
    def phi(self, committee):
        intersect_size = len(self.intersection(committee))
        if intersect_size < self.lower or intersect_size > self.upper:
            return 0
        if intersect_size > self.saturation:
            return self.saturation / intersect_size
        return 1
    
    def serialize(self):
        return {"set" : list(self), "lower" : self.lower, "saturation" : self.saturation, "upper" : self.upper}


class Election():
    def __init__(self, eid, name, description, candidates, K):
        if len(name) > 60: raise Exception("Name is too long.")
        if len(name) < 3: raise Exception("Name is too short.")
        if len(description) > 500: raise Exception("Description is too long.")
        if len(candidates) > 12: raise Exception("Too many candidates.")
        for c in candidates:
            if len(c) > 30: raise Exception("Candidate name too long: %s."%c)
        if K >= len(candidates): raise Exception("Committe size too large.")
        self.name = name
        self.eid = str(eid)
        self.description = description
        self.candidates = candidates
        self.K = K
        self.evaluation_token = "%08x" % random.randint(0, 0xFFFFFFFF)
        self.__ballots__ = list()
        keywords = name.lower() + " " + description.lower() + " " + self.eid
        keywords = re.sub('[^a-zA-Z0-9äöüß]', ' ', keywords)
        keywords = re.sub(r'\b\w{1,3}\b', '', keywords) # Remove short words.
        self.keywords = set(keywords.split())
        self.keywords.add(name.lower())
        self.is_finished = False
        self.is_stopped = False
        self.winner = None
        self.potential_winners = None
        self.votecount = 0
    
    def add_ballot(self, list_of_bounded_sets):
        if self.is_stopped:
            raise Exception("The creator stopped the voting process. You can no longer vote.")
        for i in range(1, len(list_of_bounded_sets)):
            for j in range(i):
                if not list_of_bounded_sets[i].is_disjoint(list_of_bounded_sets[j]):
                    raise Exception("Bounded sets within a ballot must be disjoint.")
        self.potential_winners = None
        self.votecount += 1
        self.__ballots__.append(list_of_bounded_sets)
    
    def evaluate(self):
        if self.is_finished:
            raise Exception("This election has already a winner.")
        if self.potential_winners == None:
            self.potential_winners = self.compute_winners()
        return self.potential_winners
    
    def stop(self):
        self.is_stopped = True
    
    def restart(self):
        self.is_stopped = False
    
    def compute_winners(self):
        best_score = 0
        committees_with_score = list()
        for committee in itertools.combinations(self.candidates, self.K):
            current_score = self.score(committee)
            if current_score > best_score:
                best_score = current_score
                committees_with_score = list()
                committees_with_score.append(committee)
            elif current_score == best_score:
                committees_with_score.append(committee)
        ret = dict()
        for i in range(len(committees_with_score)):
            ret["cid" + str(i)] = committees_with_score[i]
        return ret
    
    def set_winner(self, committee_id):
        if self.is_finished:
            raise Exception("This election has already a winner.")
        if committee_id not in self.potential_winners.keys():
            raise Exception("This committee id doesn't exist:%s"%committee_id)
        self.is_finished = True
        self.is_stopped = True
        self.winner = self.potential_winners[committee_id]
        self.potential_winners = None

    def score(self, committee):
        return sum(
            sum(bs.phi(committee) * bs.intersection_size(committee) for bs in ballot)
            for ballot in self.__ballots__
            )
    
    def search_relevance(self, search_string):
        search_string = search_string.lower()
        if search_string == str(self.eid):
            return 100
        search_string = re.sub('[^a-zA-Z0-9äöüß]', ' ', search_string)
        words = set(search_string.split())
        if len(words) < 1: raise Exception("Search is empty.")
        return len(words.intersection(self.keywords))
    
    def serialize(self):
        ret = {
            "name" : self.name,
            "eid" : self.eid,
            "description" : self.description,
            "candidates" : list(self.candidates),
            "K" : self.K,
            "evaluation_token" : self.evaluation_token,
            "__ballots__" : [[bs.serialize() for bs in b] for b in self.__ballots__],
            "is_stopped" : False,
            "is_finished" : False,
            "potential_winners" : self.potential_winners,
            "is_stopped" : self.is_stopped,
            "votecount" : self.votecount
        }
        
        if self.is_finished:
            ret["is_finished"] = True
            ret["winner"] = self.winner
        return ret