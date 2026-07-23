"""Single location for tests related to the Player class."""

from constants import PLAYER_COLS
from get.players import Players

def  test_get_all_players():
    unique_players = 1248
    pls = Players()
    all_pls = pls.get_all_players()
    assert all_pls.columns.tolist() == list(PLAYER_COLS.values())[:7]
    assert len(all_pls) == unique_players