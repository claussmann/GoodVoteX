import random
import itertools
import re
from hashlib import sha256

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

class User():
    def __init__(self, username, name, password):
        if len(name) > 60: raise Exception("Name is too long.")
        if len(name) < 3: raise Exception("Name is too short.")
        if len(password) > 40: raise Exception("Password must be no more than 40 chars")
        if len(password) < 8: raise Exception("Password must be at least 8 chars")
        self.name = name
        self.salt = "%08x" % random.randint(0, 0xFFFFFFFF)
        self.password_hash = password_hash(password, self.salt)
        self.username = username.lower()
        self.elections = list()
    
    def check_password(self, passwd):
        return self.password_hash == password_hash(passwd, self.salt)
    
    def add_election(self, election):
        self.elections.append(election.eid)
    
    def serialize(self):
        ret = {
            "name" : self.name,
            "username" : self.username,
            "salt" : self.salt,
            "password_hash" : self.password_hash,
            "elections" : self.elections
        }
        return ret


def password_hash(passwd, salt):
    tmp = passwd + " " + salt
    return sha256(tmp.encode('utf-8')).hexdigest()