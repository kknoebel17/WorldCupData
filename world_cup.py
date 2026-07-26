"""Webpage for FIFA World Cup 226 data using streamlit."""

from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_pydantic as sp

from get.players import Players
from models.players import PlayerBase, FieldPlayer, GoalKeeper


# Globals
IMAGE_PATH = Path('images.jpeg')
PLAYER_SUMM_TEXT = (
    "Click on a player's name to see statistics for that"
    " player below this table. You can also search for a player"
    " by name in the Navigation Panel to the left."
)

# Helper functions
def get_autosized_columns(df, min_px=80, max_px=400, char_multiplier=9):
    """
    Scans a DataFrame to calculate pixel widths based on text length.
    Safely converts NumPy int64 values to standard Python integers for JSON serialization.
    """
    column_config = {}
    for col in df.columns:
        # Check max string length of the data rows
        max_cell_len = df[col].apply(str).map(len).max() if not df.empty else 0
        # Check string length of the column header itself
        max_header_len = len(str(col))

        # Determine the longest string footprint
        longest_len = max(max_cell_len, max_header_len)

        # Calculate visual pixel width (adding ~25px buffer for cell padding/icons)
        calculated_width = (longest_len * char_multiplier) + 25
        final_width = max(min_px, min(max_px, calculated_width))

        # Cast final_width to a native Python int so Streamlit can serialize it to JSON
        column_config[col] = st.column_config.Column(width=int(final_width))

    return column_config

# State
if "active_player_name" not in st.session_state:
    st.session_state.active_player_name = ""


def handle_selection():
    # Access the widget's internal state dict via its assigned key
    selection_data = st.session_state.my_df_selection_key
    selected_cells = selection_data.get("selection", {}).get("cells", [])

    if selected_cells:
        try:
            inner_coordinate = selected_cells[0]
            row_idx = int(inner_coordinate[0])
            column_identifier = inner_coordinate[1]

            # Get the correct filtered dataframe instance
            current_reset_df = filtered_df.reset_index(drop=True)

            if isinstance(column_identifier, int):
                column_name = current_reset_df.columns[column_identifier]
            else:
                column_name = str(column_identifier)

            if column_name == "Player Name":
                clicked_cell_value = current_reset_df.iloc[row_idx]["Player Name"]
                st.session_state.active_player_name = str(clicked_cell_value)
        except Exception as e:
            st.error(f"Selection Callback Error: {e}")


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
with st.sidebar:
    st.header("Navigation Panel")

    # Bundle into a Form to force click execution every single time
    with st.form(key="sidebar_search_form", clear_on_submit=False):
        search_value = st.text_input(
            label='Search for Player',
            value=st.session_state.active_player_name,  # Keeps the current active name synced visually
            key="sidebar_search_input"
        )
        submit_button = st.form_submit_button(label="Search / Reset Grid")

    # If the user clicks the button or
    # presses Enter inside the form input box
    if submit_button:
        if search_value:
            st.session_state.active_player_name = search_value

            # Wipe out the DataFrame grid selection array instantly
            st.session_state.my_df_selection_key = {"selection": {"rows": [], "cells": []}}
            st.rerun()

# Header image
st.image(IMAGE_PATH)

# Tables
st.title('Players of the 2026 FIFA World Cup')
st.subheader('Player summaries')

# All players table

st.caption(PLAYER_SUMM_TEXT)
# Create a multi-column horizontal row layout to contain your text inputs
filter_cols = st.columns(len(st.session_state.my_data.columns))
filtered_df = st.session_state.my_data.copy()

# Dynamically generate text filter input boxes for every column header profile
for i, col_name in enumerate(st.session_state.my_data.columns):
    with filter_cols[i]:
        search_term = st.text_input(
            label=f"Filter {col_name}",
            label_visibility="collapsed",  # Hides label to look like a clean grid row
            placeholder=f"Filter {col_name}...",
            key=f"filter_input_{col_name}"
        )
        if search_term:
            # Drop down matching records using non-case-sensitive string evaluations
            filtered_df = filtered_df[
                filtered_df[col_name].astype(str).str.contains(search_term, case=False, na=False)
            ]

st.divider()

# Generate layout configurations dynamically for the main table
main_table_configs = get_autosized_columns(st.session_state.my_data)

# FIXED: Replaced on_select="rerun" with our safe state logic callback execution handler
st.dataframe(
    filtered_df.reset_index(drop=True),
    hide_index=True,
    on_select=handle_selection,
    selection_mode="single-cell",
    key="my_df_selection_key",
    column_config=main_table_configs,
)

# Single player table
player_name = st.session_state.active_player_name

if player_name and str(player_name).strip() != "":
    st.divider()
    st.subheader('Single player statistics')
    header = f"World Cup 2026 statistics for {player_name}"

    players = Players()
    player_model = players.get_player_by_name(player_name)

    if player_model is not None:
        try:
            # Convert Pydantic model to a standard python dictionary
            player_dict = player_model.dict()

            # Build a clean 2-column DataFrame (Metric Name vs Value)
            sp.pydantic_output(player_model)
            # if player_det_display:
            #     st.json(player_det_display.model_dump())

            # # 3. Format metric names for cleaner visual display (Optional but recommended)
            # player_det_display["Metric"] = player_det_display["Metric"].str.replace("_", " ").str.title()
            #
            # # 4. Generate configurations and render
            # details_table_configs = get_autosized_columns(player_det_display)
            # st.data_editor(
            #     player_det_display,
            #     column_config=details_table_configs,
            #     hide_index=True,
            #     num_rows="dynamic",
            #     key=f"editor_{player_name}"
            # )
        except Exception as e:
            st.error(f"Display Error: {e}")
    else:
        st.warning(f"No database records found matching: {player_name}")

