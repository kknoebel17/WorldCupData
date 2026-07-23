"""Single location for tests related to the Player class."""

from constants import PLAYER_COLS
from get.players import Players

# Globals
UNIQUE_PLAYERS = 1248

def test_init():
    pls = Players()
    assert len(pls.all_players) == UNIQUE_PLAYERS

def test_get_player_summaries():
    pls = Players()
    all_pls = pls.get_player_summaries()
    assert all_pls.columns.tolist() == list(PLAYER_COLS.values())[:7]
    assert len(all_pls) == UNIQUE_PLAYERS