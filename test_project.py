import pandas as pd
import pytest

from data_cleaner import DataCleaner
from game_analyzer import GameAnalyzer


def make_raw_data():
    """Testler için küçük, elle hazırlanmış ham veri."""
    return pd.DataFrame({
        "Name": ["Good Game", "Bad Game", "Few Reviews", "Paint Tool", "Old DLC"],
        "Short Description": ["", "", "", "", ""],
        "Price": [1999, 0, 499, 2999, 999],
        "Initial Price": [1999, 0, 499, 2999, 999],
        "Owners": ["100,000 .. 200,000", "0 .. 20,000", "0 .. 20,000",
                   "20,000 .. 50,000", "0 .. 20,000"],
        "Release Date": ["2020/05/01", "2018/01/15", "2021/03/10",
                         "2019/07/07", "2015/02/02"],
        "Genre": ["Action, Indie", "Action", "Indie",
                  "Design & Illustration", "Action"],
        "Type": ["game", "game", "game", "game", "dlc"],
        "Website": ["", "", "", "", ""],
        "Required Age": [0, 0, 0, 0, 0],
        "Positive Reviews": [90, 20, 2, 500, 50],
        "Negative Reviews": [10, 80, 0, 5, 50],
    })


@pytest.fixture
def clean_df():
    return DataCleaner(make_raw_data()).clean()


# ---------- DataCleaner testleri ----------

def test_price_converted_to_dollars(clean_df):
    good = clean_df[clean_df["Name"] == "Good Game"].iloc[0]
    assert good["Price"] == pytest.approx(19.99)


def test_owners_parsed_to_numbers(clean_df):
    good = clean_df[clean_df["Name"] == "Good Game"].iloc[0]
    assert good["Owners Min"] == 100000
    assert good["Owners Max"] == 200000
    assert good["Owners Mid"] == 150000


def test_release_year_extracted(clean_df):
    good = clean_df[clean_df["Name"] == "Good Game"].iloc[0]
    assert good["Release Year"] == 2020


def test_review_score_calculated(clean_df):
    good = clean_df[clean_df["Name"] == "Good Game"].iloc[0]
    assert good["Total Reviews"] == 100
    assert good["Review Score"] == pytest.approx(0.9)


def test_unwanted_rows_removed(clean_df):
    names = set(clean_df["Name"])
    assert "Few Reviews" not in names   # 10'dan az inceleme
    assert "Paint Tool" not in names    # oyun değil, program
    assert "Old DLC" not in names       # türü "game" değil
    assert names == {"Good Game", "Bad Game"}


def test_original_data_not_modified():
    raw = make_raw_data()
    DataCleaner(raw).clean()
    assert raw["Price"].iloc[0] == 1999


# ---------- GameAnalyzer testleri ----------

def test_genre_stats(clean_df):
    stats = GameAnalyzer(clean_df).genre_stats(min_games=1)
    action = stats[stats["Genre"] == "Action"].iloc[0]
    assert action["Games"] == 2
    assert action["Avg_Score"] == pytest.approx((0.9 + 0.2) / 2)


def test_free_vs_paid(clean_df):
    result = GameAnalyzer(clean_df).free_vs_paid().set_index("Type")
    assert result.loc["Free", "Games"] == 1
    assert result.loc["Paid", "Games"] == 1


def test_find_game_is_case_insensitive(clean_df):
    found = GameAnalyzer(clean_df).find_game("good")
    assert list(found["Name"]) == ["Good Game"]


def test_compare_to_genre(clean_df):
    result = GameAnalyzer(clean_df).compare_to_genre("Good Game")
    action = result[result["Genre"] == "Action"].iloc[0]
    assert action["Better Than (%)"] == pytest.approx(50.0)


def test_compare_unknown_game_returns_none(clean_df):
    assert GameAnalyzer(clean_df).compare_to_genre("No Such Game") is None


# ---------- ReviewPredictor testi ----------

def test_predictor_returns_probability():
    import numpy as np
    from predictor import ReviewPredictor

    rng = np.random.default_rng(0)
    n = 400
    df = pd.DataFrame({
        "Price": rng.choice([0, 9.99, 19.99], n),
        "Release Year": rng.integers(2010, 2023, n),
        "Genre List": [["Action"] if i % 2 else ["Indie"] for i in range(n)],
        "Review Score": rng.random(n),
    })
    model = ReviewPredictor()
    results = model.train(df, min_genre_games=10)
    chance = model.predict_proba(9.99, 2020, ["Action"])
    assert 0 <= results["accuracy"] <= 1
    assert 0 <= chance <= 1
