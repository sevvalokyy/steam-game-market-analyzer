from pathlib import Path
import pandas as pd
from data_loader import DataLoader
from data_cleaner import DataCleaner
from game_analyzer import GameAnalyzer

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = DataCleaner(DataLoader(Path(__file__).parent / "data" / "games.csv").load()).clean()
analyzer = GameAnalyzer(df)

print("\n=== TURLERE GORE ===")
print(analyzer.genre_stats())
print("\n=== UCRETSIZ vs UCRETLI ===")
print(analyzer.free_vs_paid())
print("\n=== FIYAT ARALIKLARI ===")
print(analyzer.price_band_stats())
print("\n=== EN IYI 10 OYUN ===")
print(analyzer.top_games())
print("\n=== OYUN KARSILASTIRMA: Counter-Strike ===")
print(analyzer.compare_to_genre("Counter-Strike"))
