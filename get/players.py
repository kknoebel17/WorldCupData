"""Single location for database interaction the Players class."""

import pandas as pd

from access.relational import SQLAccess
from constants import PLAYER_COLS

class Players:
    def __init__(self):
        self.sa = SQLAccess()
        self.sa.__int__()
        cursor = self.sa.create_connection()
        self.cursor = cursor
        self.cursor.execute("SELECT * FROM worldcup26.players;")
        self.all_players = self.cursor.fetchall()
        self.sa.close_connection(self.cursor)

    def get_player_summaries(self) -> pd.DataFrame:
        """Get summary information for all players in the database."""
        players_summary = []
        # Only grab summary information
        for player in self.all_players:
            this_entry = player[:7]
            players_summary.append(this_entry)
        player_cols = list(PLAYER_COLS.values())
        cols_to_use = player_cols[:len(players_summary[0])]
        df_players_summary = pd.DataFrame(
            data=players_summary,
            columns=cols_to_use,
        )

        return df_players_summary


