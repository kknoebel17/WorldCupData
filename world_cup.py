import streamlit as st
import pandas as pd
import numpy as np

from access.relational import SQLAccess
from get.players import Players

@st.cache_data
def get_all_players():
    players = Players()
    all_players = players.get_player_summaries()

    return all_players

st.title('Players of the 2026 FIFA World Cup')

with st.sidebar:
    st.header("Navigation Panel")
    player_name = st.sidebar.text_input(
        label='Search for Player',
    )

data_load_state = st.text('Getting stats for all players...')
all_players = get_all_players()
data_load_state.text("Done! All 2026 FIFA World Cup players are here.")


if st.checkbox('Show player summaries'):
    st.subheader('Player summaries')
    st.dataframe(all_players, hide_index=True)

if player_name is not None:
    header = f"World Cup 2026 statistics for {player_name}"
    players = Players()
    player_det = players.get_player_by_name(player_name)
    try:
        player_det = player_det.rename(columns={0: header})
        event = st.data_editor(
            player_det,
            column_config={
                "widgets": st.column_config.Column(
                    f"World Cup 2026 statistics for {player_name}",
                    width="large",
                    required=True,
                )
            },
            hide_index=True,
            num_rows="dynamic",
        )
    except AttributeError:
        pass


