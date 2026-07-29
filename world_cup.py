"""Webpage for FIFA World Cup 2026 data using streamlit."""

from pathlib import Path

import streamlit as st
from streamlit_elements import (
    elements,
    html,
    nivo,
)
from st_aggrid import (
    AgGrid,
    ColumnsAutoSizeMode,
    GridOptionsBuilder,
)

from constants import NON_NUMERIC_COLS
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

# Cache individual player requests to ensure zero redundant queries
# trigger unhandled webhook tracking loops in AgGrid backends on layout updates
@st.cache_data
def get_cached_player_detail(player_name):
    players_api = Players()
    return players_api.get_player_by_name(player_name)

data_load_state = st.text('Getting stats for all players...')
all_players = get_all_players()
data_load_state.text("Done! All 2026 FIFA World Cup players are here.")

if "my_data" not in st.session_state:
    st.session_state.my_data = all_players.reset_index(drop=True)

# Functions
def render_player_subgrid(
        target_player_name,
        container_index,
        html_obj,
        nivo_obj,
        unique_canvas_key
):
    """
    Renders the internal content of a player statistics card using native
    Streamlit layout elements, and prints out working Nivo visual data charts.
    """
    if not target_player_name or str(target_player_name).strip() == "":
        return

    player_det = get_cached_player_detail(target_player_name)
    try:
        # For clean dictionary lookups, we convert it to a Series/Dict:
        # Assumes player_det has 'Metric' as index and values in the first column
        stats = player_det.iloc[:, 0].to_dict()
        # 1. Header (Name + Picture Side-by-Side + Close Button)
        top_col1, top_col2 = st.columns([3, 1])

        with top_col1:
            st.markdown(f"## {target_player_name}")
            player_team = stats.get("Team")
            position = stats.get("Position")
            st.markdown(f"### {player_team}")
            st.markdown(f"### {position}")
            # Close trigger action
            if st.button("Close Profile", key=f"clear_slot_{container_index}"):
                if container_index == 0:
                    # Primary card close: shift comp card up if it exists
                    if st.session_state.compare_player_name:
                        st.session_state.active_player_name = st.session_state.compare_player_name
                        st.session_state.compare_player_name = ""
                    else:
                        st.session_state.active_player_name = ""
                else:
                    # Secondary comparison card close
                    st.session_state.compare_player_name = ""
                st.session_state.grid_version += 1
                st.rerun()

        with top_col2:
            image_path = Path('images.png')
            st.image(image_path, width=100)

        st.divider()

        # 2. Summary Metrics (3 cols)
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

        # Gather available numerical/chartable
        # metrics from the dictionary safely
        numerical_metrics = {}
        for k, v in stats.items():
            try:
                # Exclude non-numeric descriptive strings (like Team, Position, Club)
                if k not in NON_NUMERIC_COLS:
                    numerical_metrics[k] = int(float(str(v)))
            except (ValueError, TypeError):
                continue

        # Set palettes for each card
        chart_palette = "#166256" if container_index == 0 else "#dfc578"

        # Inject the target player name to ensure a globally unique layout key wrapper
        safe_player_key = "".join(c for c in target_player_name if c.isalnum())

        # Multi-select widget to pick which statistics to map
        chosen_metrics = st.multiselect(
            "Select metrics to chart",
            options=list(numerical_metrics.keys()),
            default=None,
            key=f"chart_metrics_select_{container_index}_{safe_player_key}"
        )

        # Open an independent elements canvas for the chart frame
        with elements(f"{unique_canvas_key}_{container_index}_{safe_player_key}"):

            if chosen_metrics:
                chart_data = []
                for m in chosen_metrics:
                    try:
                        metric_value = numerical_metrics.get(m, 0)
                        chart_data.append({
                            "metric": str(m),
                            "value": float(metric_value)
                        })
                    except Exception:
                        continue

                if len(chart_data) > 0:
                    with html_obj.div(
                            key=f"chart_active_node_{container_index}_{safe_player_key}",
                            style={"height": 220, "width": "100%"}
                    ):
                        nivo_obj.Bar(
                            key=f"nivo_bar_element_{container_index}_{safe_player_key}",
                            data=chart_data,
                            keys=["value"],
                            indexBy="metric",
                            margin={"top": 20, "right": 20, "bottom": 50, "left": 50},
                            padding=0.3,
                            colors=chart_palette,
                            axisBottom={"tickSize": 5, "tickPadding": 5, "tickRotation": -15},
                            labelTextColor={"from": "theme", "modifiers": [["darker", 1.6]]},
                            animate=False,
                            motionConfig="none"
                        )

        # 3. Remainder of metrics (2 cols)
        bottom_col1, bottom_col2 = st.columns(2)
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
        remaining_metrics = {
            k: v for k, v in stats.items()
            if k not in displayed_keys
        }

        for index, (metric_name, value) in enumerate(remaining_metrics.items()):
            if index % 2 == 0:
                with bottom_col1:
                    st.text(f"{metric_name} | {value}")
            else:
                with bottom_col2:
                    st.text(f"{metric_name} | {value}")

    except Exception as e:
        st.error(f"Player {target_player_name} not found: {e}.")

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

    # Player rest button
    if st.button("Reset Comparison Views"):
        st.session_state.active_player_name = ""
        st.session_state.compare_player_name = ""
        st.session_state.grid_version += 1
        st.rerun()

# Tables
st.title('Players of the 2026 FIFA World Cup')
st.subheader('Player summaries')

# All players table
st.caption(PLAYER_SUMM_TEXT)

# Categorical drop-down filters
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    unique_teams = sorted(st.session_state.my_data["Team"].dropna().unique())
    selected_teams = st.multiselect("Filter by Team", options=unique_teams, default=[])
with col_f2:
    unique_positions = sorted(st.session_state.my_data["Position"].dropna().unique())
    selected_positions = st.multiselect(
        "Filter by Position",
        options=unique_positions,
        default=[]
    )
with col_f3:
    unique_clubs = sorted(
        st.session_state.my_data["Club"].dropna().unique()
    )
    selected_clubs = st.multiselect(
        "Filter by Club", options=unique_clubs, default=[]
    )

# Apply row filtration matching layout state
filtered_df = st.session_state.my_data.copy()
if selected_teams:
    filtered_df = filtered_df[filtered_df["Team"].isin(selected_teams)]
if selected_positions:
    filtered_df = filtered_df[filtered_df["Position"].isin(selected_positions)]
if selected_clubs:
    filtered_df = filtered_df[filtered_df["Club"].isin(selected_clubs)]

st.divider()

# Dashboard
with st.container(border=True):

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

    event = AgGrid(
        filtered_df,
        gridOptions=gridOptions,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        update_on=['selectionChanged'],
        key=f"main_player_grid_v{st.session_state.grid_version}",
        theme=AGGRID_THEME,
    )

# Parse selected row safely using ag-grid standard format
selected_rows = event.get("selected_rows", [])
selected_player = None

# Handle varying AgGrid structure variants across library versions
if selected_rows is not None and len(selected_rows) > 0:
    # If the version returns a dataframe context structure
    if hasattr(selected_rows, "to_dict"):
        selected_player = selected_rows["Player Name"].iloc[0]
    # If the version returns a list of dictionaries format
    elif isinstance(selected_rows, list):
        first_row = selected_rows[0]
        if isinstance(first_row, dict):
            selected_player = first_row.get("Player Name", "")
        else:
            selected_player = str(first_row)
    else:
        selected_player = selected_rows["Player Name"]

# Trigger an immediate visual refresh if a new candidate is targeted
if selected_player and str(
        selected_player).strip() != "" and selected_player != st.session_state.active_player_name:
    if st.session_state.active_player_name and st.session_state.active_player_name.strip() != "":
        st.session_state.compare_player_name = st.session_state.active_player_name

    st.session_state.active_player_name = selected_player
    st.session_state.grid_version += 1
    st.rerun()

# Grid for player cards
if st.session_state.active_player_name:

    # Fork screen space depending on comparison slot status using native columns
    if st.session_state.compare_player_name:
        row_layout_cols = st.columns(2)

        # COLUMN 1: Primary active selection slot (Card A)
        with row_layout_cols[0]:
            render_player_subgrid(
                st.session_state.active_player_name,
                container_index=0,
                html_obj=html,
                nivo_obj=nivo,
                unique_canvas_key="master_deck_canvas_left",
            )

        # COLUMN 2: Secondary comparative selection slot (Card B)
        with row_layout_cols[1]:
            render_player_subgrid(
                st.session_state.compare_player_name,
                container_index=1,
                html_obj=html,
                nivo_obj=nivo,
                unique_canvas_key="master_deck_canvas_right",
            )

    else:
        row_layout_cols = st.columns(1)
        with row_layout_cols[0]:
            render_player_subgrid(
                st.session_state.active_player_name,
                container_index=0,
                html_obj=html,
                nivo_obj=nivo,
                unique_canvas_key="master_deck_canvas_left",
            )