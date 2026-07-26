"""Webpage for FIFA World Cup 226 data using streamlit."""

from pathlib import Path

import streamlit as st
from st_aggrid import (
    AgGrid,
    ColumnsAutoSizeMode,
    GridOptionsBuilder,
    GridUpdateMode,
)

from get.players import Players

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

            # Force the grid to redraw from scratch without old selections
            # By changing the version key, it wipes any
            # active row clicks out of AgGrid memory
            if "grid_version" not in st.session_state:
                st.session_state.grid_version = 1
            st.session_state.grid_version += 1

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

# Build aggrid table
grid_builder = GridOptionsBuilder.from_dataframe(filtered_df)
grid_builder.configure_default_column(filterable=True, sortable=True)
grid_builder.configure_selection(
    selection_mode="single",
    use_checkbox=False,
)
gridOptions = grid_builder.build()

# Fallback initializer for our dynamic cache buster key
if "grid_version" not in st.session_state:
    st.session_state.grid_version = 1

event  = AgGrid(
    filtered_df,
    gridOptions=gridOptions,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    key=f"main_player_grid_v{st.session_state.grid_version}",
)

# Parse selected row safely using ag-grid standard format
selected_rows = event.get("selected_rows", [])

# Handle varying AgGrid structure variants across library versions
if selected_rows is not None and len(selected_rows) > 0:
    # If the version returns a dataframe context structure
    if hasattr(selected_rows, "to_dict"):
        selected_player = selected_rows.iloc[0]["Player Name"]
    # If the version returns a list of dictionaries format
    elif isinstance(selected_rows, list):
        selected_player = selected_rows[0]["Player Name"]
    else:
        selected_player = selected_rows["Player Name"]

    # Trigger an immediate visual refresh if a new candidate is targeted
    if selected_player != st.session_state.active_player_name:
        st.session_state.active_player_name = selected_player
        st.rerun()

# Single player table
player_name = st.session_state.active_player_name

if player_name and str(player_name).strip() != "":
    st.divider()  # Visual break for clarity
    st.subheader('Single player statistics')
    header = f"World Cup 2026 statistics for {player_name}"
    players = Players()
    player_det = players.get_player_by_name(player_name)

    try:
        player_det = player_det.rename(columns={0: header})

        # Force the stats column values to
        # strings to prevent PyArrow serialization errors
        player_det[header] = player_det[header].astype(str)

        # Move the index into a standard data column so our autosizer can see it
        index_name = player_det.index.name if player_det.index.name else "Metric"
        player_det_display = player_det.reset_index(names=index_name)

        grid_builder = GridOptionsBuilder.from_dataframe(player_det_display)
        grid_builder.configure_default_column(filterable=True, sortable=True)
        gridOptions = grid_builder.build()
        event = AgGrid(
            player_det_display,
            gridOptions=gridOptions,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,  # Keeps column styling clean
            key=f"single_player_grid_{player_name}",  # Prevents cross-player state collisions
        )
    except AttributeError:
        pass
