import random
import itertools
import re
from hashlib import sha256
from time import sleep

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
        self.is_stopped = False
        self.current_winner = None
        self.votecount = 0
    
    def __eq__(self, other):
        try:
            return self.eid == other.eid
        except:
            return False
        return False

    
    def add_ballot(self, list_of_bounded_sets):
        if self.is_stopped:
            raise Exception("The creator stopped the voting process. You can no longer vote.")
        for i in range(1, len(list_of_bounded_sets)):
            for j in range(i):
                if not list_of_bounded_sets[i].is_disjoint(list_of_bounded_sets[j]):
                    raise Exception("Bounded sets within a ballot must be disjoint.")
        self.current_winner = None
        self.votecount += 1
        self.__ballots__.append(list_of_bounded_sets)
    
    def compute_current_winner(self):
        tmp = self.is_stopped
        self.is_stopped = True # Prevent further votes (not sure if flask allows parallelism)
        if self.current_winner == None:
            self.current_winner = self.__compute_winner__()
        self.is_stopped = tmp
    
    def stop(self):
        self.is_stopped = True
    
    def restart(self):
        self.is_stopped = False
    
    def __compute_winner__(self):
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
        ret = random.choice(committees_with_score)
        return ret

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
            "is_stopped" : self.is_stopped,
            "votecount" : self.votecount
        }
        if self.current_winner != None:
            ret["current_winner"] = self.current_winner
        return ret

class User():
    def __init__(self, username, name, password):
        if len(name) > 60: raise Exception("Name is too long.")
        if len(name) < 3: raise Exception("Name is too short.")
        self.name = name
        self.salt = "%08x" % random.randint(0, 0xFFFFFFFF)
        self.username = username.lower()
        self.elections = list()
        self.set_password(password)
    
    def set_password(self, new_passwd):
        if len(new_passwd) > 40: raise Exception("Password must be no more than 40 chars")
        if len(new_passwd) < 8: raise Exception("Password must be at least 8 chars")
        self.password_hash = password_hash(new_passwd, self.salt)

    def check_password(self, passwd):
        sleep(0.001*random.randint(1,2000)) # prevent timing attacks
        return self.password_hash == password_hash(passwd, self.salt)
    
    def add_election(self, election):
        self.elections.append(election)
    
    def serialize(self):
        ret = {
            "name" : self.name,
            "username" : self.username,
            "salt" : self.salt,
            "password_hash" : self.password_hash,
            "elections" : [e.eid for e in self.elections]
        }
        return ret

    def owns_election(self, eID):
        return eID in [e.eid for e in self.elections]

def password_hash(passwd, salt):
    tmp = passwd + " " + salt
    return sha256(tmp.encode('utf-8')).hexdigest()