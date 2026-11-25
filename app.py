import streamlit as st

from data_loader import DataLoader
from data_cleaner import DataCleaner
from game_analyzer import GameAnalyzer
from visualizer import Visualizer
from predictor import ReviewPredictor

st.set_page_config(page_title="Steam Game Market Analyzer", layout="wide")


@st.cache_data
def load_data():
    raw = DataLoader("data/games.csv").load()
    return DataCleaner(raw).clean()


@st.cache_resource
def train_model(_data):
    model = ReviewPredictor()
    model.train(_data)
    return model


df = load_data()
viz = Visualizer()
predictor = train_model(df)

st.title("Steam Game Market Analyzer")
st.caption("What makes a game successful on Steam? Based on the Kaggle dataset "
           "'All 55,000 Games on Steam (November 2022)'.")

# --- Kenar çubuğu: filtreler ---
st.sidebar.header("Filters")
min_year, max_year = int(df["Release Year"].min()), int(df["Release Year"].max())
years = st.sidebar.slider("Release year", min_year, max_year, (2010, max_year))
min_reviews = st.sidebar.number_input("Minimum reviews", min_value=10, value=10, step=10)

filtered = df[
    df["Release Year"].between(*years) & (df["Total Reviews"] >= min_reviews)
]
analyzer = GameAnalyzer(filtered)

# --- Özet kartları ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Games", f"{len(filtered):,}")
c2.metric("Average score", f"{filtered['Review Score'].mean():.0%}")
c3.metric("Median price", f"${filtered['Price'].median():.2f}")
c4.metric("Free games", f"{(filtered['Price'] == 0).mean():.0%}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Genres", "Pricing", "Over time", "Search a game", "Predict"]
)

with tab1:
    genre_df = analyzer.genre_stats(min_games=50)
    st.plotly_chart(viz.genre_scores(genre_df), width="stretch")
    st.plotly_chart(viz.genre_popularity(genre_df), width="stretch")

with tab2:
    price_df = analyzer.price_band_stats()
    left, right = st.columns(2)
    left.plotly_chart(viz.price_bands(price_df), width="stretch")
    right.plotly_chart(viz.price_popularity(price_df), width="stretch")
    st.subheader("Free vs. paid")
    st.dataframe(analyzer.free_vs_paid(), hide_index=True)

with tab3:
    st.plotly_chart(viz.releases_per_year(analyzer.releases_per_year()),
                    width="stretch")
    st.subheader("Top rated games (1,000+ reviews)")
    st.dataframe(analyzer.top_games(n=15), hide_index=True)

with tab4:
    query = st.text_input("Type a game name", "Hollow Knight")
    results = GameAnalyzer(df).find_game(query) if query else df.iloc[0:0]
    if results.empty:
        st.info("No game found. Try another name.")
    else:
        choice = st.selectbox("Select a game", results["Name"].head(50).tolist())
        comparison = GameAnalyzer(df).compare_to_genre(choice)
        game = df[df["Name"] == choice].iloc[0]

        g1, g2, g3 = st.columns(3)
        g1.metric("Review score", f"{game['Review Score']:.0%}")
        g2.metric("Price", f"${game['Price']:.2f}")
        g3.metric("Release year", int(game["Release Year"]))

        best = comparison.loc[comparison["Better Than (%)"].idxmax()]
        st.success(f"**{choice}** has a higher review score than "
                   f"**{best['Better Than (%)']:.0f}%** of {best['Genre']} games.")
        st.plotly_chart(viz.game_vs_genre(comparison, choice), width="stretch")
        st.dataframe(comparison, hide_index=True)

with tab5:
    st.subheader("Will a new game get positive reviews?")
    st.write("A Random Forest model predicts the chance that a game gets "
             "**at least 80% positive reviews**, using only information known "
             "before release: price, release year and genres.")

    p1, p2 = st.columns(2)
    price = p1.slider("Price ($)", 0.0, 70.0, 15.0, step=0.5)
    year = p2.slider("Release year", min_year, max_year, max_year)
    default_genres = [g for g in ["Indie", "Adventure"] if g in predictor.genres]
    chosen = st.multiselect("Genres", predictor.genres, default=default_genres)

    if chosen:
        chance = predictor.predict_proba(price, year, chosen)
        st.metric("Chance of positive reviews", f"{chance:.0%}")
    else:
        st.info("Select at least one genre.")

    r = predictor.results
    st.caption(f"Model accuracy on {r['test_size']:,} test games: {r['accuracy']:.0%} "
               f"(always guessing the most common class: {r['baseline']:.0%}).")
    st.plotly_chart(viz.feature_importance(predictor.feature_importance()), width="stretch")
