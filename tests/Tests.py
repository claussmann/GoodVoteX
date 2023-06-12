from pathlib import Path

from .context import goodvotex
from goodvotex.voting.models import *
from goodvotex.auth.models import *

import pytest
import os

from .test_voting_models import *






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
