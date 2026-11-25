# Steam Game Market Analyzer

**What makes a game successful on Steam?**

An interactive data analysis dashboard built with Python, Pandas, Plotly and Streamlit. It analyzes ~38,000 Steam games to see how genre, price and release year relate to a game's review score and popularity.

Developed as a term project for SEN4015 – Advanced Programming with Python, Bahçeşehir University.

## Features

- **Data cleaning pipeline:** converts prices from cents to dollars, parses owner ranges into numbers, extracts release years, removes non-game software, DLCs and games with too few reviews.
- **Genre analysis:** average review score, median price and share of popular games for each genre.
- **Pricing analysis:** free vs. paid games and review scores across price bands.
- **Trends over time:** number of games released per year.
- **Game search:** pick any game and see how it compares to other games in its genres (e.g. *"Counter-Strike has a higher review score than 94% of Action games"*).
- **Interactive filters:** release year range and minimum review count.

## Key Findings

| Finding | Result |
|---|---|
| Paid games are rated higher than free games | 76% vs. 71% positive reviews |
| Review scores peak in the $10–20 price band | 79% positive |
| More expensive games are more often popular | 9% of $0–5 games vs. 46% of $40+ games have 100k+ owners |
| Massively Multiplayer games are popular but poorly rated | 37% popular, 64% positive |
| Indie and Casual are the most crowded genres | Only 10–13% of these games reach 100k+ owners |

## Project Structure

| File | Description |
|---|---|
| `data_loader.py` | `DataLoader` class: reads the raw CSV file |
| `data_cleaner.py` | `DataCleaner` class: cleans and prepares the data |
| `game_analyzer.py` | `GameAnalyzer` class: genre, price, year and game comparison analyses |
| `visualizer.py` | `Visualizer` class: turns analysis results into Plotly charts |
| `app.py` | Streamlit dashboard |
| `analyze.py` | Prints the main analysis tables to the terminal |
| `test_project.py` | 11 pytest tests for the cleaning and analysis logic |

## Dataset

[All 55,000 Games on Steam (November 2022)](https://www.kaggle.com/datasets/tristan581/all-55000-games-on-steam-november-2022) on Kaggle. Collected from the Steam store API and SteamSpy.

The dataset is not included in this repository. Download it from Kaggle and save `steam_games.csv` as `data/games.csv`.

## How to Run

```bash
git clone https://github.com/sevvalokyy/steam-game-market-analyzer.git
cd steam-game-market-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with:

```bash
pytest -v
```

## Limitations

- Review score is used as a proxy for quality and owner ranges from SteamSpy as a proxy for sales. Both are estimates.
- The data is a snapshot from November 2022.
- Findings show correlations, not causes. For example, expensive games may be more popular because they come from larger studios with bigger marketing budgets.
