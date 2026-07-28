"""Webpage for FIFA World Cup 2026 data using streamlit."""

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
    layout="wide",  # Wide layout is required to prevent side-by-side distortion
    initial_sidebar_state="expanded",
    menu_items=None
)
AGGRID_THEME = 'material' # options: balham, streamlit, alpine, balham, material
PLAYER_SUMM_TEXT = (
    "Click on a player's name to see statistics for that"
    " player below this table. You can also search for a player"
    " by name in the Navigation Panel to the left. A second player"
    " card can be added next to the first for comparison. This second"
    " player can be added through table selection or search."
)

# State
if "active_player_name" not in st.session_state:
    st.session_state.active_player_name = ""
if "compare_player_name" not in st.session_state:
    st.session_state.compare_player_name = ""
if "grid_version" not in st.session_state:
    st.session_state.grid_version = 1

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
        if search_value and search_value.strip():
            # Cascade selection to slot 2 if slot 1 contains data
            if st.session_state.active_player_name and st.session_state.active_player_name != search_value:
                st.session_state.compare_player_name = st.session_state.active_player_name
            st.session_state.active_player_name = search_value
            st.session_state.grid_version += 1
            st.rerun()

# Tables
st.title('Players of the 2026 FIFA World Cup')
st.subheader('Player summaries')

# All players table
st.caption(PLAYER_SUMM_TEXT)

# Categorical drop-down filters
col1, col2, col3 = st.columns(3)
with col1:
    unique_teams = sorted(st.session_state.my_data["Team"].dropna().unique())
    selected_teams = st.multiselect("Filter by Team", options=unique_teams, default=[])
with col2:
    unique_positions = sorted(st.session_state.my_data["Position"].dropna().unique())
    selected_positions = st.multiselect("Filter by Position", options=unique_positions, default=[])
with col3:
    unique_clubs = sorted(st.session_state.my_data["Club"].dropna().unique())
    selected_clubs = st.multiselect("Filter by Club", options=unique_clubs, default=[])

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
grid_builder.configure_default_column(filterable=True, sortable=True)
grid_builder.configure_selection(selection_mode="single", use_checkbox=False)
gridOptions = grid_builder.build()

event = AgGrid(
    filtered_df,
    gridOptions=gridOptions,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    update_on=['selectionChanged'],
    key=f"main_player_grid_v{st.session_state.grid_version}",
    theme=AGGRID_THEME,
)

# Intercept selections cleanly
selected_rows = event.get("selected_rows", [])

if selected_rows is not None and len(selected_rows) > 0:
    if hasattr(selected_rows, "to_dict"):
        selected_player = selected_rows.iloc[0]["Player Name"]
    elif isinstance(selected_rows, list):
        selected_player = selected_rows[0]["Player Name"]
    else:
        selected_player = selected_rows["Player Name"]

    if selected_player != st.session_state.active_player_name:
        if st.session_state.active_player_name:
            st.session_state.compare_player_name = st.session_state.active_player_name
        st.session_state.active_player_name = selected_player
        st.session_state.grid_version += 1
        st.rerun()


# Player rest button
if st.button("Reset Comparison Views"):
    st.session_state.active_player_name = ""
    st.session_state.compare_player_name = ""
    st.session_state.grid_version += 1
    st.rerun()

# Setup row layout allocation dynamically based on the dual layout state
if st.session_state.active_player_name and st.session_state.compare_player_name:
    row_layout_cols = st.columns(2)
else:
    row_layout_cols = st.columns(1)

# First single player container
with row_layout_cols[0]:
    num_player_conts = 0
    with st.container(
            border=True,
            key=f"single_player_conts_{num_player_conts}",
            width='content',
            horizontal_alignment='distribute',
    ):
        player_name = st.session_state.active_player_name

        if player_name and str(player_name).strip() != "":
            st.divider()
            st.subheader('Single player statistics')
            header = f"World Cup 2026 statistics for {player_name}"
            players = Players()
            player_det = players.get_player_by_name(player_name)

            try:
                # For clean dictionary lookups, we convert table to a Series/Dict:
                # Assumes player_det has 'Metric' as index and values in the first column
                stats = player_det.iloc[:, 0].to_dict()

                # 1. Header (Name + Picture Side-by-Side)
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
                    if position == 'GK':
                        st.text(f"Wins | {wins_metric}")
                    st.text(f"Yellow Cards | {yc_metric}")
                with bottom_col2:
                    st.text(f"Club | {club_metric}")
                    if position == 'GK':
                        st.text(f"Losses | {losses_metric}")
                    st.text(f"Red Cards | {rc_metric}")

                # Exclude the keys we already displayed above
                displayed_keys = [
                    "Goals Scored", "Plus/Minus", "Total Minutes Played",
                    "Team", "Position", "Player Name", "Age", "Club",
                    "Yellow Cards", "Red Cards", "Wins", "Losses",
                    "Clean Sheets", "Goalkeeper Minutes Played"
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
                # Increment num of containers
                num_player_conts += 1

            except Exception as e:
                st.error(f"Player {player_name} not found.")

# Second player container
if st.session_state.active_player_name and st.session_state.compare_player_name:
    with row_layout_cols[1]:
        num_player_conts = 1
        with st.container(
                border=True,
                key=f"single_player_conts_{num_player_conts}",
                width='content',
                horizontal_alignment='distribute',
        ):
            player_name_comp = st.session_state.compare_player_name

            if player_name_comp and str(player_name_comp).strip() != "":
                st.divider()
                st.subheader('Single player statistics')
                header_comp = f"World Cup 2026 statistics for {player_name_comp}"
                players_comp = Players()
                player_det_comp = players_comp.get_player_by_name(player_name_comp)

                try:
                    stats_comp = player_det_comp.iloc[:, 0].to_dict()

                    # 1. HEADER (Name + Picture Side-by-Side)
                    top_col1_comp, top_col2_comp = st.columns([3, 1])

                    with top_col1_comp:
                        st.markdown(f"## {player_name_comp}")
                        player_team_comp = stats_comp.get("Team")
                        position_comp = stats_comp.get("Position")
                        st.markdown(f"### {player_team_comp}")
                        st.markdown(f"### {position_comp}")

                    with top_col2_comp:
                        image_path_comp = Path('images.png')
                        st.image(image_path_comp, width=100)

                    st.divider()

                    # 2. Summary Metrics (3 cols)
                    first_label_comp = (
                        'Clean Sheets' if stats_comp.get('Position') == 'GK'
                        else 'Total Goals Scored'
                    )
                    first_metric_comp = (
                        stats_comp.get('Clean Sheets') if stats_comp.get('Position') == 'GK'
                        else stats_comp.get('Goals Scored')
                    )
                    third_metric_comp = (
                        stats_comp.get('Goalkeeper Minutes Played') if stats_comp.get('Position') == 'GK'
                        else stats_comp.get('Total Minutes Played')
                    )
                    metric_col1_comp, metric_col2_comp, metric_col3_comp = st.columns(3)

                    with metric_col1_comp:
                        st.metric(label=first_label_comp, value=first_metric_comp)
                    with metric_col2_comp:
                        st.metric(label="Plus / Minus", value=stats_comp.get("Plus/Minus", "0"))
                    with metric_col3_comp:
                        st.metric(label="Total Minutes Played", value=third_metric_comp)

                    st.divider()

                    # 3. Remainder of metrics (2 cols)
                    bottom_col1_comp, bottom_col2_comp = st.columns(2)

                    age_metric_comp = stats_comp.get("Age", "0")
                    club_metric_comp = stats_comp.get("Club", "0")
                    wins_metric_comp = stats_comp.get("Wins", "0")
                    losses_metric_comp = stats_comp.get("Losses", "0")
                    yc_metric_comp = stats_comp.get("Yellow Cards", "0")
                    rc_metric_comp = stats_comp.get("Red Cards", "0")

                    with bottom_col1_comp:
                        st.text(f"Age | {age_metric_comp}")
                        if position_comp == 'GK':
                            st.text(f"Wins | {wins_metric_comp}")
                        st.text(f"Yellow Cards | {yc_metric_comp}")
                    with bottom_col2_comp:
                        st.text(f"Club | {club_metric_comp}")
                        if position_comp == 'GK':
                            st.text(f"Losses | {losses_metric_comp}")
                        st.text(f"Red Cards | {rc_metric_comp}")

                    displayed_keys_comp = [
                        "Goals Scored", "Plus/Minus", "Total Minutes Played",
                        "Team", "Position", "Player Name", "Age", "Club",
                        "Yellow Cards", "Red Cards", "Wins", "Losses",
                        "Clean Sheets", "Goalkeeper Minutes Played"
                    ]
                    remaining_metrics_comp = {k: v for k, v in stats_comp.items() if k not in displayed_keys_comp}

                    for index, (metric_name, value) in enumerate(remaining_metrics_comp.items()):
                        if index % 2 == 0:
                            with bottom_col1_comp:
                                st.text(f"{metric_name} | {value}")
                        else:
                            with bottom_col2_comp:
                                st.text(f"{metric_name} | {value}")
                                num_player_conts += 1

                except Exception as e:
                    st.error(f"Player {player_name_comp} not found.")


