# -*- coding: utf-8 -*-
import itertools
import json
import random
import re

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .. import db



#################################################################################
#                 Elections
#################################################################################


class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    committeesize = db.Column(db.Integer)
    is_stopped = db.Column(db.Boolean, default=False)
    votecount = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('elections', lazy=True))
    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "election",
        "polymorphic_on": "type",
    }

    def __eq__(self, other):
        try:
            return self.id == other.id
        except:
            return False

    def add_ballot(self, ballot):
        """
        Adds a ballot to this election.

        :param ballot:
        :return:
        """
        if self.is_stopped:
            raise Exception("The creator stopped the voting process. You can no longer vote.")
        if self._check_validity(ballot):
            self.ballots.append(ballot)
            self.votecount += 1
        else:
            raise Exception("The ballot doesn't seem to be valid.")

    def recompute_current_winner(self):
        """
        Recomputes the currently best committee.
        Note that this should be called as rarely as possible, as it checks
        all ( |candidates| choose committeesize ) many committees' scores.

        :return:
        """
        if len(self.ballots) == 0:
            return
        for c in self.candidates:
            c.is_winner = False
        for w in self._compute_winners():
            w.is_winner = True

    def get_winners(self):
        """
        Get the (current) winners of this election.

        :return: List of candidates
        """
        return [c for c in self.candidates if c.is_winner]
        

    def stop(self):
        """
        Prevent further votes from being submitted.

        :return:
        """
        self.is_stopped = True

    def restart(self):
        """
        Allow votes to be submitted again.

        :return:
        """
        self.is_stopped = False
    
    def search_relevance(self, search_string):
        """
        Compute how likely this election fits the search string.

        :param search_string:
        :return: an integer
        """
        search_string = search_string.lower()
        if search_string == str(self.id):
            return 100
        search_string = re.sub('[^a-zA-Z0-9äöüß]', ' ', search_string)
        words = set(search_string.split())
        if len(words) < 1:
            raise Exception("Search is empty.")
        return len(words.intersection(self._get_keywords()))

    def _get_keywords(self):
        if not hasattr(self, 'keywords'):
            keywords = self.title.lower() + " " + self.description.lower() + " " + str(self.id)
            keywords = re.sub('[^a-zA-Z0-9äöüß]', ' ', keywords)
            keywords = re.sub(r'\b\w{1,3}\b', '', keywords)  # Remove short words.
            keywords = set(keywords.split())
            keywords.add(self.title.lower())
            self.keywords = keywords
        return self.keywords
    
    # Overwrite!
    def _compute_winners(self):
        """
        Overwrite this function.
        This function should compute a committee of winners.

        :return: Set
        """
        pass

    # Overwrite!
    def _check_validity(self, ballot):
        """
        Overwrite this function.
        This function should check if the given ballot is valid.

        :return: True/False
        """
        pass

    # Overwrite!
    def get_ballot_type(self):
        """
        Overwrite this function.
        This function should return one of approvalBallot, ordinalBallot, cardinalBallot,
        and boundedApprovalBallot.

        :return: String
        """
        pass


class ApprovalElection(Election):
    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "approvalElection",
    }

    def _compute_winners(self):
        mapping = {str(c.id): c for c in self.candidates}
        scores = {c: 0 for c in [str(x.id) for x in self.candidates]}
        for ballot in self.ballots:
            for c in ballot.get_involved_candidates():
                scores[c] += 1
        ret = set()
        for i in range(self.committeesize):
            best = max(scores.keys(), key=scores.get)
            scores[best] = -1
            ret.add(best)
        return {mapping[c] for c in ret}

    def _check_validity(self, ballot):
        ids = [str(c.id) for c in self.candidates]
        for id in ballot.get_involved_candidates():
            if id not in ids:
                return False
        return ballot.type == "approvalBallot"
    
    def get_ballot_type(self):
        return "approvalBallot"

class SAVElection(Election):
    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "savElection",
    }

    def _compute_winners(self):
        mapping = {str(c.id): c for c in self.candidates}
        scores = {c: 0 for c in [str(x.id) for x in self.candidates]}
        for ballot in self.ballots:
            for c in ballot.get_involved_candidates():
                scores[c] += 1/len(ballot.get_involved_candidates())
        ret = set()
        for i in range(self.committeesize):
            best = max(scores.keys(), key=scores.get)
            scores[best] = -1
            ret.add(best)
        return {mapping[c] for c in ret}

    def _check_validity(self, ballot):
        ids = [str(c.id) for c in self.candidates]
        for id in ballot.get_involved_candidates():
            if id not in ids:
                return False
        return ballot.type == "approvalBallot"
    
    def get_ballot_type(self):
        return "approvalBallot"

class PAVElection(Election):
    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "pavElection",
    }

    def _compute_winners(self):
        ids = [str(c.id) for c in self.candidates]
        mapping = {str(c.id): c for c in self.candidates}
        best_committee = None
        best_score = -1
        for committee in itertools.combinations(ids, self.committeesize):
            curr_score = 0
            for ballot in self.ballots:
                intersec_size = len(ballot.get_involved_candidates().intersection(set(committee)))
                curr_score += sum(1/(i+1) for i in range(intersec_size))
            if curr_score > best_score:
                best_score = curr_score
                best_committee = committee
        return [mapping[c] for c in best_committee]

    def _check_validity(self, ballot):
        ids = [str(c.id) for c in self.candidates]
        for id in ballot.get_involved_candidates():
            if id not in ids:
                return False
        return ballot.type == "approvalBallot"
    
    def get_ballot_type(self):
        return "approvalBallot"

class BoundedApprovalElection(Election):
    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "boundedApprovalElection",
    }

    def _compute_winners(self):
        ids = [str(c.id) for c in self.candidates]
        mapping = {str(c.id): c for c in self.candidates}
        best_committee = None
        best_score = -1
        for committee in itertools.combinations(ids, self.committeesize):
            curr_score = sum(ballot.score(committee) for ballot in self.ballots)
            if curr_score > best_score:
                best_score = curr_score
                best_committee = committee
        return [mapping[c] for c in best_committee]

    def _check_validity(self, ballot):
        ids = [str(c.id) for c in self.candidates]
        for id in ballot.get_involved_candidates():
            if id not in ids:
                return False
        return ballot._check_validity() and ballot.type == "boundedApprovalBallot"
    
    def get_ballot_type(self):
        return "boundedApprovalBallot"

class BordaElection(Election):
    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "bordaElection",
    }

    def _compute_winners(self):
        mapping = {str(c.id): c for c in self.candidates}
        scores = {c: 0 for c in [str(x.id) for x in self.candidates]}
        m = len(self.candidates)
        for ballot in self.ballots:
            for c in scores:
                scores[c] += m - ballot.position_of(c)
        ret = set()
        for i in range(self.committeesize):
            best = max(scores.keys(), key=scores.get)
            scores[best] = -1
            ret.add(best)
        return {mapping[c] for c in ret}

    def _check_validity(self, ballot):
        ids = [str(c.id) for c in self.candidates]
        for id in ballot.get_involved_candidates():
            if id not in ids:
                return False
        if ballot.type != "cardinalBallot":
            return False
        return len(ballot.get_involved_candidates()) == len(ids)
    
    def get_ballot_type(self):
        return "ordinalBallot"

class BordaCCElection(Election):
    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "bordaCCElection",
    }

    def _compute_winners(self):
        ids = [str(c.id) for c in self.candidates]
        mapping = {str(c.id): c for c in self.candidates}
        m = len(ids)
        best_committee = None
        best_score = -1
        for committee in itertools.combinations(ids, self.committeesize):
            curr_score = sum(max(m - ballot.position_of(c) for c in ids) for ballot in self.ballots)
            if curr_score > best_score:
                best_score = curr_score
                best_committee = committee
        return [mapping[c] for c in best_committee]

    def _check_validity(self, ballot):
        ids = [str(c.id) for c in self.candidates]
        for id in ballot.get_involved_candidates():
            if id not in ids:
                return False
        if ballot.type != "cardinalBallot":
            return False
        return len(ballot.get_involved_candidates()) == len(ids)
    
    def get_ballot_type(self):
        return "ordinalBallot"


class STVElection(Election):
    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "stvElection",
    }

    def _compute_winners(self):
        mapping = {str(c.id): c for c in self.candidates}
        voting_abilities = {v: 1 for v in self.ballots}
        candidates_left = [str(c.id) for c in self.candidates]

        committee = set()
        quota = len(self.ballots) // (self.committeesize + 1) + 1 # Droop Quota

        def plurality_winner_loser():
            plur_scores = {c: 0 for c in candidates_left}
            for b in self.ballots:
                votes_for = min(candidates_left, key=b.position_of)
                plur_scores[votes_for] += voting_abilities[b]
            best = max(candidates_left, key=plur_scores.get)
            worst = min(candidates_left, key=plur_scores.get)
            return (best, plur_scores[best], worst, plur_scores[worst])
        
        def reduce_voting_ability(elected_candidate, score_of_elected):
            exceed = score_of_elected - quota
            avg_voting_ability_afterwards = exceed / score_of_elected
            for b in self.ballots:
                votes_for = min(candidates_left, key=b.position_of)
                if votes_for == elected_candidate:
                    voting_abilities[b] = voting_abilities[b] * avg_voting_ability_afterwards

        while len(committee) < self.committeesize:
            if sum(voting_abilities.values()) < quota:
                break # This usually happens when there are fewer voters than the committee size.
            winner, win_score, loser, los_score = plurality_winner_loser()
            if win_score >= quota:
                reduce_voting_ability(winner, win_score)
                committee.add(winner)
                candidates_left.remove(winner)
            else:
                candidates_left.remove(loser)
        return [mapping[c] for c in committee]

    def _check_validity(self, ballot):
        ids = [str(c.id) for c in self.candidates]
        for id in ballot.get_involved_candidates():
            if id not in ids:
                return False
        if ballot.type != "cardinalBallot":
            return False
        return len(ballot.get_involved_candidates()) == len(ids)
    
    def get_ballot_type(self):
        return "ordinalBallot"
    

class UtilitarianElection(Election):
    id: Mapped[int] = mapped_column(ForeignKey("election.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "utilitarianElection",
    }

    def _compute_winners(self):
        mapping = {str(c.id): c for c in self.candidates}
        scores = {c: 0 for c in [str(x.id) for x in self.candidates]}
        m = len(self.candidates)
        for ballot in self.ballots:
            for c in scores:
                scores[c] += ballot.utility_for(c)
        ret = set()
        for i in range(self.committeesize):
            best = max(scores.keys(), key=scores.get)
            scores[best] = -1
            ret.add(best)
        return {mapping[c] for c in ret}

    def _check_validity(self, ballot):
        ids = [str(c.id) for c in self.candidates]
        for id in ballot.get_involved_candidates():
            if id not in ids:
                return False
        return ballot._check_validity() and ballot.type == "cardinalBallot"
    
    def get_ballot_type(self):
        return "cardinalBallot"







#################################################################################
#                 Candidate
#################################################################################

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    election = db.relationship('Election', backref=db.backref('candidates', lazy=True))
    is_winner = db.Column(db.Boolean, default=False)






#################################################################################
#                 Ballots
#################################################################################

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
        self._parse_from_json(json_content)

    # Optional Overwrite.
    def _check_validity(self):
        """
        Check whether this ballot is valid (e.g. any conditions are violated).
        This will be called at the end of constucting this object.

        :return: True/False
        """
        return True
    
    # Overwrite!
    def _parse_from_json(self, json_content):
        """
        Compute the score for committee. The score is a numerical value. The 
        interpretation is: higher the score <=> better the committee. Note that
        this is only the score according to this ballot. The total score for
        a committee will be computed within the Election class as the sum over
        the scores for all committees.

        :param committee: a set of candidate ids
        :return: an integer
        """
        pass


class ApprovalBallot(Ballot):
    id: Mapped[int] = mapped_column(ForeignKey("ballot.id"), primary_key=True)
    json_encoded = db.Column(db.String(1000), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "approvalBallot",
    }

    def get_involved_candidates(self):
        return set(self._decode())

    def _parse_from_json(self, json_content):
        app_candidates = json_content["app_candidates"]
        self.json_encoded = json.dumps({"app_candidates" : app_candidates})
    
    def _decode(self):
        raw_obj = json.loads(self.json_encoded)
        return set(raw_obj["app_candidates"])


class OrdinalBallot(Ballot):
    id: Mapped[int] = mapped_column(ForeignKey("ballot.id"), primary_key=True)
    json_encoded = db.Column(db.String(1000), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "ordinalBallot",
    }

    def get_involved_candidates(self):
        return set(self._decode())
    
    def position_of(self, candidate):
        order = self._decode()
        return order.index(candidate) + 1

    def _parse_from_json(self, json_content):
        order = json_content["order"]
        self.json_encoded = json.dumps({"order" : order})
    
    def _decode(self):
        raw_obj = json.loads(self.json_encoded)
        return list(raw_obj["order"])


class CardinalBallot(Ballot):
    id: Mapped[int] = mapped_column(ForeignKey("ballot.id"), primary_key=True)
    json_encoded = db.Column(db.String(1000), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "cardinalBallot",
    }

    def utility_for(self, candidate):
        rating = self._decode()
        if candidate in rating:
            return rating[candidate]
        return 0
    
    def get_involved_candidates(self):
        return set(self._decode())

    def _check_validity(self):
        rating = self._decode()
        for candidate in rating:
            if rating[candidate] > 10 or rating[candidate] < -10:
                return False
        return True

    def _parse_from_json(self, json_content):
        ratings = json_content["ratings"]
        for c in ratings:
            ratings[c] = int(ratings[c])
        self.json_encoded = json.dumps({"ratings" : ratings})
    
    def _decode(self):
        raw_obj = json.loads(self.json_encoded)
        return raw_obj["ratings"]
    

class BoundedApprovalBallot(Ballot):
    id: Mapped[int] = mapped_column(ForeignKey("ballot.id"), primary_key=True)
    json_encoded = db.Column(db.String(1000), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "boundedApprovalBallot",
    }

    def score(self, committee):
        def phi(bset, bound, committee):
            intersect_size = len(bset.intersection(committee))
            if intersect_size < bound[0] or intersect_size > bound[2]:
                return 0 # out of lower or upper bound
            if intersect_size > bound[1]:
                return bound[1] / intersect_size # in substitution area
            return 1 # in approval area
        
        pairs = self._decode()
        return sum(phi(set(s), b, committee) * len(set(s).intersection(committee)) for s,b in pairs)

    def _check_validity(self):
        pairs = self._decode()
        sets = [set(pair[0]) for pair in pairs]
        bounds = [pair[1] for pair in pairs]
        # Check for disjointness
        for i,j in itertools.combinations(sets, 2):
            if i.intersection(j) != set():
                print(i.intersection(j))
                return False
        # Check all bounds are present
        for b in bounds:
            if len(b) != 3:
                return False
        # Check ballot is satisfiable
        for s,b in pairs:
            if len(s) < b[0]:
                return False
            if b[0] > b[1] or b[1] > b[2] or b[0] > b[2]:
                return False
        return True
    
    def _parse_from_json(self, json_content):
        sets = json_content["sets"]
        bounds = json_content["bounds"]
        re_encoded = []
        for name,s in sets.items():
            s = list(set(s)) # make sure no element is dublicate
            re_encoded.append([s, bounds[name]])
        self.json_encoded = json.dumps(re_encoded)
    
    def get_involved_candidates(self):
        pairs = self._decode()
        ret = set()
        for s in [set(pair[0]) for pair in pairs]:
            ret = ret.union(s)
        return ret
    
    def _decode(self):
        return json.loads(self.json_encoded)
