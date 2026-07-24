"""Location for helper functions used in the get modules."""

import unicodedata

def remove_accents(input_str):
    # Decompose the string into base characters and diacritics
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    # Filter out the combining diacritical marks
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_player_name(df):
    df['player'] = df.apply(
        lambda row: remove_accents(row.player), axis='columns'
    )

    return df