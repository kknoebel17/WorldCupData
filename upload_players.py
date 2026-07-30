import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load the environment variable containing your Neon connection string
load_dotenv()
db_url = os.getenv("DATABASE_URL")

# Quick fix: SQLAlchemy requires 'postgresql://' instead of 'postgres://'
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Create the database connection engine
engine = create_engine(db_url)

# Read your local CSV file
# Change 'players_data.csv' to the actual filename of your CSV file
data_path = Path("tests/resources/players.csv")
df = pd.read_csv(data_path)

try:
    print("Uploading CSV rows to Neon...")

    # Push data to the 'players' table
    # 'append' adds data to the table we created.
    df.to_sql("players", engine, if_exists="append", index=False)

    print("Success! All player data has been successfully imported to Neon.")

except Exception as e:
    print(f"Upload failed: {e}")
