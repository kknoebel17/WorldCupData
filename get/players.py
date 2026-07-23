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

    def get_all_players(self):
        """Get all unique players in the database."""
        all_players = []
        self.cursor.execute("SELECT * FROM worldcup26.players;")
        all_entries = self.cursor.fetchall()
        self.sa.close_connection(self.cursor)

        for entry in all_entries:
            this_entry = entry[:7]
            all_players.append(this_entry)
        player_cols = list(PLAYER_COLS.values())
        cols_to_use = player_cols[:len(all_players[0])]
        df_all_players = pd.DataFrame(
            data=all_players,
            columns=cols_to_use,
        )

        return df_all_players


