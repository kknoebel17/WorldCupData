"""Single location for tests related to the Player class."""

import pandas as pd
import pytest
from pathlib import Path

import constants as const
from get.players import Players

# Globals
UNIQUE_PLAYERS = 1248

def test_init():
    pls = Players()
    assert len(pls.all_players) == UNIQUE_PLAYERS

def test_get_player_summaries():
    pls = Players()
    all_pls = pls.get_player_summaries()
    assert all_pls.columns.tolist() == list(const.PLAYER_COLS.values())[:6]
    assert len(all_pls) == UNIQUE_PLAYERS

@pytest.mark.parametrize(
    'player_name, position', [
        ('Amine Gouiri', 'FW'),
        ('Luca Zidane', 'GK'),
        ('None', 'None'),
        ('Carlos Santana', 'None'),  # Random name not in database
        ('amine gouiri', 'FW'),  # Test lower case
        ('LUCA ZIDANE', 'GK'),  # Test upper case
        ('lUCa zIdANE', 'GK'),  # Test random case
])
def test_get_player_by_name(player_name, position):
    test_data_path = Path('tests/resources/sample_player_data.csv')
    test_data = pd.read_csv(test_data_path)
    # Capitalize to match test resources
    pn = [name.capitalize() for name in player_name.split(' ')]
    pn_formatted = ' '.join(pn)
    test_row = test_data[test_data['player'] == pn_formatted].fillna('')
    # Reset column names to match output of get_player_by_name()
    rename_dict = const.PLAYER_COLS
    test_row = test_row.rename(columns=rename_dict)
    if position == 'FW':
        target_cols = list(const.BASE_COLS.values()) + list(const.FIELD_PLAYER_COLS.values())
        to_test = test_row[target_cols]
    elif position == 'GK':
        target_cols = list(const.BASE_COLS.values()) + list(const.GOALKEEPER_COLS.values())
        to_test = test_row[target_cols]
    else:
        to_test = None
    pls = Players()
    player_det = pls.get_player_by_name(player_name)
    if player_det is None:  # Test null return
        assert player_det == to_test
    else:
        for col in to_test.columns:
            assert player_det.loc[col].values[0] == to_test[col].values[0]

@pytest.mark.parametrize(
    'player_name', [
        ('Luka Modrić'),
        ('Luka Modric'),
])
def test_get_player_by_name_accents(player_name):
    name_in_test_file = 'Luka Modrić'
    name_to_test = 'Luka Modric'
    test_data_path = Path('tests/resources/sample_player_data.csv')
    test_data = pd.read_csv(test_data_path)
    test_row = test_data[test_data['player'] == name_in_test_file].fillna('')
    # Reset column names to match output of get_player_by_name()
    rename_dict = const.PLAYER_COLS
    test_row = test_row.rename(columns=rename_dict)
    target_cols = list(const.BASE_COLS.values()) + list(const.FIELD_PLAYER_COLS.values())
    to_test = test_row[target_cols]
    pls = Players()
    player_det = pls.get_player_by_name(player_name)
    for col in to_test.columns:
        # Test for unaccented name as this is what is shown to user
        if col == 'Player Name':
            assert player_det.loc[col].values[0] == name_to_test
        else:
            assert player_det.loc[col].values[0] == to_test[col].values[0]
