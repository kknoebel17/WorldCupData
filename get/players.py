"""Single location for database interaction the Players class."""

from dataclasses import asdict
from typing import Dict, List, Union

import numpy as np
import pandas as pd
import pydantic

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
        # Drop Country column as it always matches Team column
        self.all_players = self.all_players.drop(columns=['team_country'])
        self.sa.close_connection(self.cursor)

    def get_player_summaries(self) -> pd.DataFrame:
        """Get summary information for all players in the database."""
        df_players_summary = self.all_players
        rename_dict = const.PLAYER_COLS
        cols_to_use = list(const.PLAYER_COLS.values())[:6]
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
                    detail_map[val] = self._clean_data_types(
                        data_input=player_detail[val].values[0],
                        key_str=val,
                        model=GoalKeeper,
                    )
            player_model = GoalKeeper(**detail_map)
        else:
            for val in player_detail.columns:
                if (val in const.FIELD_PLAYER_COLS) or (val in const.BASE_COLS):
                    detail_map[val] = self._clean_data_types(
                        data_input=player_detail[val].values[0],
                        key_str=val,
                        model=FieldPlayer,
                    )
            player_model = FieldPlayer(**detail_map)

        # Reset column names
        player_detail_corr = {
            const.PLAYER_COLS[key]: value for key, value
            in player_detail.items()
        }
        df_det_corr = pd.DataFrame(
            index=[0],
            data=player_detail_corr,
        )

        return player_model

    # Helper methods
    def _clean_data_types(
            self,
            data_input: Union[str, float, int],
            key_str: str,
            model,
    ) -> Union[str, float, int]:
        try:
            base_annotations = PlayerBase.__annotations__
            annotations = model.__annotations__
            total_annotations = base_annotations | annotations
            if isinstance(data_input, total_annotations[key_str]):
                return data_input
            else:
                if total_annotations[key_str] is float:
                    try:
                        return float(data_input)
                    except ValueError:
                        return 0
                elif total_annotations[key_str] is int:
                    try:
                        return int(data_input)
                    except ValueError:
                        return 0
                else:  # string
                    try:
                        return str(data_input)
                    except ValueError:
                        return ""
        except AttributeError:
            error_msg = f"{key_str} is not a sting, float, or int."
            raise AttributeError(error_msg)







