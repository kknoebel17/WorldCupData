import streamlit as st
import pandas as pd
import numpy as np

from access.relational import SQLAccess
from get.players import Players

# State
if "active_player_name" not in st.session_state:
    st.session_state.active_player_name = ""


# Resources
@st.cache_data
def get_all_players():
    players = Players()
    all_players = players.get_player_summaries()
    return all_players


data_load_state = st.text('Getting stats for all players...')
all_players = get_all_players()
data_load_state.text("Done! All 2026 FIFA World Cup players are here.")

if "my_data" not in st.session_state:
    st.session_state.my_data = all_players.reset_index(drop=True)


# Widgets
def handle_sidebar_search():
    """Triggered only when a user types a name in the sidebar and hits Enter"""
    search_value = st.session_state.sidebar_search_input
    if search_value:
        st.session_state.active_player_name = search_value


with st.sidebar:
    st.header("Navigation Panel")
    st.text_input(
        label='Search for Player',
        key="sidebar_search_input",
        on_change=handle_sidebar_search
    )

# Tables
st.title('Players of the 2026 FIFA World Cup')
st.subheader('Player summaries')

# All players table
event = st.dataframe(
    st.session_state.my_data,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-cell",
    key="my_df_selection_key"
)

# Inspect click metadata from the selection wrapper
selection = event.get("selection", {})
selected_cells = selection.get("cells", [])

if selected_cells:
    try:
        # Unpack your coordinate layout structure: (row_idx, column_name)
        inner_coordinate = selected_cells[0]
        row_idx = inner_coordinate[0]
        column_name = inner_coordinate[1]

        # Explicitly verify the selected column name
        if column_name == "Player Name":
            # Extract player value directly using the row number index mapping
            clicked_cell_value = st.session_state.my_data.iloc[int(row_idx)]["Player Name"]

            # Save the value securely to state before triggering any rerun
            st.session_state.active_player_name = str(clicked_cell_value)

    except Exception as e:
        st.error(f"Unpacking Error: {e} | Raw Data Structure: {selected_cells}")

# Single player table
player_name = st.session_state.active_player_name

if player_name and str(player_name).strip() != "":
    st.divider()  # Visual break for clarity
    header = f"World Cup 2026 statistics for {player_name}"
    players = Players()
    player_det = players.get_player_by_name(player_name)

    try:
        player_det = player_det.rename(columns={0: header})
        st.data_editor(
            player_det,
            column_config={
                header: st.column_config.Column(
                    header,
                    width="large",
                    required=True,
                )
            },
            hide_index=True,
            num_rows="dynamic",
            key=f"editor_{player_name}"  # Unique key prevents widget state collisions on player swap
        )
    except AttributeError:
        pass
