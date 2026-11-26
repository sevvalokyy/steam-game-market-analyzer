from pathlib import Path
import pandas as pd
from data_loader import DataLoader
from data_cleaner import DataCleaner

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

raw_df = DataLoader(Path(__file__).parent / "data" / "games.csv").load()
clean_df = DataCleaner(raw_df).clean()

print("Ham veri:", raw_df.shape)
print("Temiz veri:", clean_df.shape)
print(clean_df[["Name", "Price", "Owners Mid", "Release Year", "Review Score", "Genre List"]].head(10))
