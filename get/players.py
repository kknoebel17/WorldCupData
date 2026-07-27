"""Single location for database interaction the Players class."""

from dataclasses import asdict
from typing import Dict, List, Union

import pandas as pd

import constants as const
import get.helpers as helpers
from access.relational import SQLAccess
from models.players import PlayerBase, FieldPlayer, GoalKeeper

# Globals
GK_POS_CODE: str = 'GK'

class Players:
    def __init__(self):
        self.sa = SQLAccess()
        cursor = self.sa.create_connection()
        self.cursor = cursor
        self.cursor.execute("SELECT * FROM worldcup26.players;")
        self.all_players = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        # Lower player names and remove accents
        self.all_players = helpers.clean_player_name(self.all_players)
        self.all_players = self.all_players.drop(columns=const.PLAYER_COLS_TO_DROP)
        self.sa.close_connection(self.cursor)

    def get_player_summaries(self) -> pd.DataFrame:
        """Get summary information for all players in the database."""
        df_players_summary = self.all_players
        rename_dict = const.PLAYER_COLS
        cols_to_use = list(const.PLAYER_COLS.values())[:5]
        df_players_summary = df_players_summary.rename(columns=rename_dict)
        df_players_summary = df_players_summary[cols_to_use]

        return df_players_summary

    def get_player_by_name(self, player_name: str) -> Union[None, pd.DataFrame]:
        """Get player details by name."""
        # Clean user inputs
        player_name = helpers.remove_accents(player_name)
        player_name = player_name.lower()
        player_detail = self.all_players[
            # Lower case to normalize unput from user
            self.all_players['player'].str.lower() == player_name
        ]
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
            # Grab correct data types from model
            player_data_type = {
                const.PLAYER_COLS[k]: v
                for k, v in GoalKeeper.__annotations__.items()
            }
        else:
            for val in player_detail.columns:
                if (val in const.FIELD_PLAYER_COLS) or (val in const.BASE_COLS):
                    detail_map[val] = player_detail[val].values[0]
            player_detail = asdict(FieldPlayer(**detail_map))
            # Grab correct data types from model
            player_data_type = {
                const.PLAYER_COLS[k]: v
                for k, v in FieldPlayer.__annotations__.items()
            }

        # Reset column names
        player_detail_corr = {
            const.PLAYER_COLS[key]: value for key, value
            in player_detail.items()
        }
        df_det_corr = pd.DataFrame(
            index=[0],
            data=player_detail_corr,
        )
        # Merge player data types with base type
        base_data_type = {
            const.PLAYER_COLS[k]: v
            for k, v in PlayerBase.__annotations__.items()
        }
        total_player_dtype = base_data_type | player_data_type
        try:
            df_det_corr = df_det_corr.astype(total_player_dtype, errors='ignore')
        except TypeError:
            print(f"Bad data types for {player_name}")
        # Sort columns from A to Z
        df_det_corr = df_det_corr.sort_index(axis='columns')

        return df_det_corr.T




