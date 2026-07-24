"""Single location for database interaction the Players class."""

from dataclasses import asdict
from typing import Dict, List, Union

import pandas as pd

import constants as const
from access.relational import SQLAccess
from models.players import FieldPlayer, GoalKeeper

# Globals
GK_POS_CODE: str = 'GK'

class Players:
    def __init__(self):
        self.sa = SQLAccess()
        self.sa.__int__()
        cursor = self.sa.create_connection()
        self.cursor = cursor
        self.cursor.execute("SELECT * FROM worldcup26.players;")
        self.all_players = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        self.sa.close_connection(self.cursor)

    def get_player_summaries(self) -> pd.DataFrame:
        """Get summary information for all players in the database."""
        players_summary = []
        # Only grab summary information
        for player in self.all_players:
            this_entry = player[:7]
            players_summary.append(this_entry)
        player_cols = list(const.PLAYER_COLS.values())
        cols_to_use = player_cols[:len(players_summary[0])]
        df_players_summary = pd.DataFrame(
            data=players_summary,
            columns=cols_to_use,
        )

        return df_players_summary

    def get_player_by_name(self, player_name: str) -> Union[None, pd.DataFrame]:
        """Get player details by name."""
        player_detail = self.all_players[self.all_players['player'] == player_name]
        player_detail = player_detail.fillna('')
        if len(player_detail) == 0:
            return None
        # Create player detail
        detail_map: Dict[str, str] = {}
        keys: List[str] = list(const.PLAYER_COLS.keys())
        # Inspect to find goalkeeper or field player
        is_gk: bool = player_detail['position'].values[0] == GK_POS_CODE
        if is_gk:  # Assign data to correct type
            for val in player_detail.columns:
                if (val in const.GOALKEEPER_COLS) or (val in const.BASE_COLS):
                    detail_map[val] = player_detail[val].values[0]
            player_detail = asdict(GoalKeeper(**detail_map))
        else:
            for val in player_detail.columns:
                if (val in const.FIELD_PLAYER_COLS) or (val in const.BASE_COLS):
                    detail_map[val] = player_detail[val].values[0]
            player_detail = asdict(FieldPlayer(**detail_map))

        # Reset column names
        player_detail_corr = {
            const.PLAYER_COLS[key]: value for key, value
            in player_detail.items()
        }
        df_det_corr = pd.DataFrame(
            index=[0],
            data=player_detail_corr,
        )

        return df_det_corr




