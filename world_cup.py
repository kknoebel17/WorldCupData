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
data = get_all_players()
data_load_state.text("Done! All 2026 FIFA World Cup players are here.")


if st.checkbox('Show player summaries'):
    st.subheader('Player summaries')
    st.dataframe(data)

if player_name is not None:
    header = f"World Cup 2026 statistics for {player_name}"
    st.title(header)
    players = Players()
    player_det = players.get_player_by_name(player_name)
    st.dataframe(player_det)