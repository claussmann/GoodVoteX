# -*- coding: utf-8 -*-
import itertools
import json
import random
import re

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .. import db


class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    committeesize = db.Column(db.Integer)
    is_stopped = db.Column(db.Boolean, default=False)
    votecount = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('elections', lazy=True))
    ballot_type = db.Column(db.String(60), nullable=False)

    def __eq__(self, other):
        try:
            return self.id == other.id
        except:
            return False
        return False

    def add_ballot(self, ballot):
        if self.is_stopped:
            raise Exception("The creator stopped the voting process. You can no longer vote.")
        self.ballots.append(ballot)
        if not ballot.is_of_type(self.ballot_type):
            raise Exception("This election does not accept this type of ballot.")
        if len(ballot.get_involved_candidates().difference([str(c.id) for c in self.candidates])) > 0:
            self.ballots.remove(ballot)
            raise Exception("Ballot seems to involve candidates not participating in this election.")
        self.votecount += 1

    def recompute_current_winner(self):
        for c in self.candidates:
            c.is_winner = False
        for w in self.__compute_winner__():
            w.is_winner = True

    def get_winners(self):
        return [c for c in self.candidates if c.is_winner]

    def stop(self):
        self.is_stopped = True

    def restart(self):
        self.is_stopped = False

    def __compute_winner__(self):
        best_score = 0
        committees_with_score = list()
        for committee in itertools.combinations(self.candidates, self.committeesize):
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
        return sum(ballot.score({str(c.id) for c in committee}) for ballot in self.ballots)

    def search_relevance(self, search_string):
        search_string = search_string.lower()
        if search_string == str(self.id):
            return 100
        search_string = re.sub('[^a-zA-Z0-9äöüß]', ' ', search_string)
        words = set(search_string.split())
        if len(words) < 1:
            raise Exception("Search is empty.")
        return len(words.intersection(self.__get_keywords()))

    def __get_keywords(self):
        if not hasattr(self, 'keywords'):
            keywords = self.title.lower() + " " + self.description.lower() + " " + str(self.id)
            keywords = re.sub('[^a-zA-Z0-9äöüß]', ' ', keywords)
            keywords = re.sub(r'\b\w{1,3}\b', '', keywords)  # Remove short words.
            keywords = set(keywords.split())
            keywords.add(self.title.lower())
            self.keywords = keywords
        return self.keywords


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    election = db.relationship('Election', backref=db.backref('candidates', lazy=True))
    is_winner = db.Column(db.Boolean, default=False)


class Ballot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type: Mapped[str]
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'),
                            nullable=False)
    election = db.relationship('Election', backref=db.backref('ballots', lazy=True))

    __mapper_args__ = {
        "polymorphic_identity": "ballot",
        "polymorphic_on": "type",
    }

    def __init__(self, json_content, **kwargs):
        super(Ballot, self).__init__(**kwargs)
        self.parse_from_json(json_content)
        if not self.check_validity():
            raise Exception("Ballot does not seem to be valid.") 

    # Overwrite!
    def score(self, committee):
        pass

    # Optional Overwrite.
    def check_validity(self):
        return True
    
    # Overwrite!
    def is_of_type(self, ballot_type):
        pass
    
    # Overwrite!
    def parse_from_json(self, json_content):
        pass
    
    # Overwrite!
    def get_involved_candidates(self):
        pass






#################################################################################
#                 Bounded Approval Ballots
#################################################################################

class BoundedApprovalBallot(Ballot):
    id: Mapped[int] = mapped_column(ForeignKey("ballot.id"), primary_key=True)
    json_encoded = db.Column(db.String(1000), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "boundedApprovalBallot",
    }

    def score(self, committee):
        sets = self._decode()
        return sum(bs.phi(committee) * bs.intersection_size(committee) for bs in sets)

    def check_validity(self):
        sets = self._decode()
        for i in range(1, len(sets)):
            for j in range(i):
                if not sets[i].is_disjoint(sets[j]):
                    return False
        return True
    
    def is_of_type(self, ballot_type):
        return ballot_type == "boundedApprovalBallot"

    def parse_from_json(self, json_content):
        sets = json_content["sets"]
        bounds = json_content["bounds"]
        bounded_sets = list()
        for s in sets:
            items_in_set = set(sets[s])
            if len(items_in_set) == 0:
                continue
            bounded_sets.append(BoundedSet(bounds[s][0], bounds[s][1], bounds[s][2], items_in_set))
        bounded_sets_encoded = {"bsets": [bs.serialize() for bs in bounded_sets]}
        self.json_encoded = json.dumps(bounded_sets_encoded)

    def _decode(self):
        raw_obj = json.loads(self.json_encoded)
        ret = list()
        for bs in raw_obj["bsets"]:
            ret.append(BoundedSet(bs["lower"], bs["saturation"], bs["upper"], *bs["set"]))
        return ret
    
    def get_involved_candidates(self):
        ret = set()
        sets = self._decode()
        for s in sets:
            ret = ret.union(s)
        return ret


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
    
    def __str__(self):
        items = str(sorted(self)) # sort alternatives (easier debugging)
        items = items[1:-1] # cut breakets
        return "<{%s}, %d, %d, %d>" %(items, self.lower, self.saturation, self.upper)

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_disjoint(self, other):
        return len(self.intersection(other)) == 0

    def intersection_size(self, committee):
        return len(self.intersection(committee))

    def phi(self, committee):
        intersect_size = self.intersection_size(committee)
        if intersect_size < self.lower or intersect_size > self.upper:
            return 0
        if intersect_size > self.saturation:
            return self.saturation / intersect_size
        return 1

    def serialize(self):
        return {"set": list(self), "lower": self.lower, "saturation": self.saturation, "upper": self.upper}


#################################################################################
#                 Regular Approval Ballots
#################################################################################

class ApprovalBallot(Ballot):
    id: Mapped[int] = mapped_column(ForeignKey("ballot.id"), primary_key=True)
    json_encoded = db.Column(db.String(1000), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "approvalBallot",
    }

    def score(self, committee):
        app_candidates = self._decode()
        return len(app_candidates.intersection(committee))
    
    def is_of_type(self, ballot_type):
        return ballot_type == "approvalBallot"

    def parse_from_json(self, json_content):
        app_candidates = json_content["app_candidates"]
        self.json_encoded = json.dumps({"app_candidates" : app_candidates})


    def _decode(self):
        raw_obj = json.loads(self.json_encoded)
        return set(raw_obj["app_candidates"])
    
    def get_involved_candidates(self):
        return self._decode()
