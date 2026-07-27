"""Webpage for FIFA World Cup 226 data using streamlit."""

from pathlib import Path

import streamlit as st
from st_aggrid import (
    AgGrid,
    ColumnsAutoSizeMode,
    GridOptionsBuilder,
)

from get.players import Players

# Globals
st.set_page_config(
    page_title=None,
    page_icon=None,
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None
)
AGGRID_THEME = 'material' # options: balham, streamlit, alpine, balham, material
PLAYER_SUMM_TEXT = (
    "Click on a player's name to see statistics for that"
    " player below this table. You can also search for a player"
    " by name in the Navigation Panel to the left."
)

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
            label='🏃🏻‍♂️ Search for Player',
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

# Tables
st.title('Players of the 2026 FIFA World Cup')
st.subheader('Player summaries')

# All players table
st.caption(PLAYER_SUMM_TEXT)

# Provide an elegant multi-select dropdown
# for categorical text columns
col1, col2, col3 = st.columns(3)
with col1:
    # Extracts all non-null, unique teams sorted alphabetically
    unique_teams = sorted(st.session_state.my_data["Team"].dropna().unique())
    selected_teams = st.multiselect(
        "Filter by Team",
        options=unique_teams,
        default=[] # Empty means "Show all"
    )
with col2:
    # Extracts all non-null, unique positions sorted alphabetically
    unique_positions = sorted(st.session_state.my_data["Position"].dropna().unique())
    selected_positions = st.multiselect(
        "Filter by Position",
        options=unique_positions,
        default=[]
    )
with col3:
    # Extracts all non-null, unique clubs sorted alphabetically
    unique_clubs = sorted(st.session_state.my_data["Club"].dropna().unique())
    selected_clubs = st.multiselect(
        "Filter by Club",
        options=unique_clubs,
        default=[]
    )

# Filter down your dataframe behind the scenes using standard Python logic
filtered_df = st.session_state.my_data.copy()

if selected_teams:
    filtered_df = filtered_df[filtered_df["Team"].isin(selected_teams)]
if selected_positions:
    filtered_df = filtered_df[filtered_df["Position"].isin(selected_positions)]
if selected_clubs:
    filtered_df = filtered_df[filtered_df["Club"].isin(selected_clubs)]

st.divider()

# Build aggrid table
grid_builder = GridOptionsBuilder.from_dataframe(filtered_df)
grid_builder.configure_default_column(
    filterable=True,
    sortable=True,
)
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
    update_on=['selectionChanged'],
    key=f"main_player_grid_v{st.session_state.grid_version}",
    theme=AGGRID_THEME,
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
    st.divider()
    st.subheader('Single player statistics')
    header = f"World Cup 2026 statistics for {player_name}"
    players = Players()
    player_det = players.get_player_by_name(player_name)

    try:
        # Transpose or pivot your data if it's stored vertically,
        # but for clean dictionary lookups, we convert it to a Series/Dict:
        # Assumes player_det has 'Metric' as index and values in the first column
        stats = player_det.iloc[:, 0].to_dict()

        # 1. HEADER (Name + Picture Side-by-Side)
        # Adjust widths (e.g., 3 parts name, 1 part image)
        top_col1, top_col2 = st.columns([3, 1])

        with top_col1:
            st.markdown(f"## {player_name}")
            player_team = stats.get("Team")
            position = stats.get("Position")
            st.markdown(f"### {player_team}")
            st.markdown(f"### {position}")


        with top_col2:
            # Replace with your actual image logic (URL column, file path, or default fallback)
            image_path = Path('images.png')
            st.image(image_path, width=100)

        st.divider()

        # 2. Summary Metrics (3 cols)

        # Need to define first and third summary
        # metric for field players vs. goalkeepers
        first_label = (
            'Clean Sheets' if stats.get('Position') == 'GK'
            else 'Total Goals Scored'
        )
        first_metric = (
            stats.get('Clean Sheets') if stats.get('Position') == 'GK'
            else stats.get('Goals Scored')
        )
        third_metric = (
            stats.get('Goalkeeper Minutes Played') if stats.get('Position') == 'GK'
            else stats.get('Total Minutes Played')
        )
        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric(label=first_label, value=first_metric)
        with metric_col2:
            st.metric(label="Plus / Minus", value=stats.get("Plus/Minus", "0"))
        with metric_col3:
            st.metric(label="Total Minutes Played", value=third_metric)

        st.divider()

        # 3. Remainder of metrics (2 cols)

        # Dynamically split the remaining items into two columns
        bottom_col1, bottom_col2 = st.columns(2)
        # Display Age and Club first
        age_metric = stats.get("Age", "0")
        club_metric = stats.get("Club", "0")
        wins_metric = stats.get("Wins", "0")
        losses_metric = stats.get("Losses", "0")
        yc_metric = stats.get("Yellow Cards", "0")
        rc_metric = stats.get("Red Cards", "0")
        with bottom_col1:
            st.text(f"Age | {age_metric}")
            st.text(f"Wins | {wins_metric}")
            st.text(f"Yellow Cards | {yc_metric}")
        with bottom_col2:
            st.text(f"Club | {club_metric}")
            st.text(f"Losses | {losses_metric}")
            st.text(f"Red Cards | {rc_metric}")

        # Exclude the keys we already displayed above
        displayed_keys = [
            "Goals Scored", "Plus/Minus", "Total Minutes Played",
            "Team", "Position", "Player Name", "Age", "Club",
            "Yellow Cards", "Red Cards", "Wins", "Losses",
        ]
        remaining_metrics = {k: v for k, v in stats.items() if k not in displayed_keys}

        for index, (metric_name, value) in enumerate(remaining_metrics.items()):
            # Alternates items between column 1 and column 2
            if index % 2 == 0:
                with bottom_col1:
                    st.text(f"{metric_name} | {value}")
            else:
                with bottom_col2:
                    st.text(f"{metric_name} | {value}")

    except Exception as e:
        st.error(f"Player {player_name} not found.")

