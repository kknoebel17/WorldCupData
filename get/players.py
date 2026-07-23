"""Single location for database interaction the Players class."""

from access.relational import SQLAccess

class Players:
    def __init__(self):
        self.sa = SQLAccess()
        self.sa.__int__()
        cursor = self.sa.create_connection()
        self.cursor = cursor

    def get_all_players(self):
        """Get all unique players in the database."""
        all_players = []
        self.cursor.execute("SELECT player_id FROM players.fifa_world_cup_26;")
        all_entries = self.cursor.fetchall()
        for entry in all_entries:
            this_entry = entry[0].strip()
            all_players.append(this_entry)
        self.sa.close_connection(self.cursor)
        all_players_un = set(all_players)

        return all_players_un


