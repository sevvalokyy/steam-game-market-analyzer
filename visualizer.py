import plotly.express as px
import plotly.graph_objects as go


class Visualizer:
    """GameAnalyzer'ın tablolarını Plotly grafiklerine çevirir."""

    def genre_scores(self, genre_df):
        fig = px.bar(
            genre_df.sort_values("Avg_Score"),
            x="Avg_Score", y="Genre", orientation="h",
            hover_data=["Games", "Median_Price", "Popular_Pct"],
            labels={"Avg_Score": "Average review score", "Genre": ""},
            title="Average review score by genre",
        )
        fig.update_xaxes(tickformat=".0%", range=[0.5, 0.85])
        return fig

    def genre_popularity(self, genre_df):
        fig = px.scatter(
            genre_df, x="Popular_Pct", y="Avg_Score", size="Games", text="Genre",
            labels={"Popular_Pct": "Games with 100k+ owners (%)",
                    "Avg_Score": "Average review score"},
            title="Popularity vs. review score by genre",
        )
        fig.update_traces(textposition="top center")
        fig.update_yaxes(tickformat=".0%")
        return fig

    def price_bands(self, price_df):
        fig = px.bar(
            price_df, x="Price Band", y="Avg_Score", text_auto=".0%",
            hover_data=["Games", "Popular_Pct"],
            labels={"Avg_Score": "Average review score"},
            title="Review score by price band",
        )
        fig.update_yaxes(tickformat=".0%", range=[0.5, 0.85])
        return fig

    def price_popularity(self, price_df):
        return px.bar(
            price_df, x="Price Band", y="Popular_Pct", text_auto=".0f",
            labels={"Popular_Pct": "Games with 100k+ owners (%)"},
            title="Share of popular games by price band",
        )

    def releases_per_year(self, year_df):
        return px.line(
            year_df, x="Release Year", y="Games", markers=True,
            title="Number of games released per year",
        )

    def game_vs_genre(self, comparison_df, game_name):
        fig = go.Figure()
        fig.add_bar(x=comparison_df["Genre"], y=comparison_df["Genre Avg Score"],
                    name="Genre average")
        fig.add_bar(x=comparison_df["Genre"], y=comparison_df["Game Score"],
                    name=game_name)
        fig.update_layout(barmode="group", title=f"{game_name} vs. its genres")
        fig.update_yaxes(tickformat=".0%", range=[0, 1])
        return fig

    def feature_importance(self, importance_df):
        return px.bar(
            importance_df.sort_values("Importance"),
            x="Importance", y="Feature", orientation="h",
            labels={"Feature": ""},
            title="What the model looks at most",
        )
