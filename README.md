# WorldCupData

Portal to view stats for each player for the 2026 World Cup. Player information is displayed as a "player card" that
supports interactive Nivo charts to compare stats for each player in the database.

## Description

This application uses [Kaggle data](https://www.kaggle.com/datasets/swaptr/fifa-wc-2026-players?resource=download) for
the 2026 FIFA World Cup.The data was then loaded into a Postgres SQL database. A Python/Pandas backend loads and cleans
the data for the front end built with [streamlit](https://streamlit.io).

## Getting Started

### Dependencies

- Mac OS
- Python 3.11
- [PostgresSQL](https://www.postgresql.org)

### Installing

1. From the project directory in terminal, run `python -m pip install -r requirements.txt` to install the project
dependencies.
2. Import the csv file from Kaggle into the postgres database.
3. Create a `.env` file in the project directory and populate with your database credentials:
- Example:
  - DATABASE={database name}
  - PY_USER={SQL username}
  - PASSWORD={SQL password}
  - HOST={local host}
  - PORT={port number}

### Testing

Test are all in the `tests` folder in the project's root directory. Pytest is the testing framework for this
application.

### Executing application

In the terminal run `python -m streamlit run world_cup.py` to display a local version of the app that can be edited from the
`world_cup.py` file in the project directory.

## Authors
Kyle Knoebel

## Version History
- Version 0.1
  - Initial release

## Acknowledgements

- Swapnil Tripathi for the original players dataset.


- [nivo](https://nivo.rocks)
- [pandas](https://pandas.pydata.org)
- [streamlit](https://streamlit.io)
- [streamlit-aggrid](https://github.com/PablocFonseca/streamlit-aggrid)
- [streamlit-elements](https://github.com/okld/streamlit-elements)
