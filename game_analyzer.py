import pandas as pd


class GameAnalyzer:
    """Temizlenmiş Steam verisi üzerinde analizler yapar."""

    def __init__(self, df):
        self.df = df

    def genre_stats(self, min_games=100):
        """Her türün oyun sayısı, ortalama puanı ve medyan fiyatı."""
        genres = self.df.explode("Genre List")
        stats = (
            genres.groupby("Genre List")
            .agg(
                Games=("Name", "count"),
                Avg_Score=("Review Score", "mean"),
                Median_Price=("Price", "median"),
                Popular_Pct=("Owners Min", lambda x: (x >= 100000).mean() * 100),
            )
            .reset_index()
            .rename(columns={"Genre List": "Genre"})
        )
        stats = stats[stats["Games"] >= min_games]
        return stats.sort_values("Avg_Score", ascending=False).reset_index(drop=True)

    def free_vs_paid(self):
        """Ücretsiz ve ücretli oyunların karşılaştırması."""
        labels = self.df["Price"].apply(lambda p: "Free" if p == 0 else "Paid")
        return (
            self.df.groupby(labels)
            .agg(
                Games=("Name", "count"),
                Avg_Score=("Review Score", "mean"),
                Popular_Pct=("Owners Min", lambda x: (x >= 100000).mean() * 100),
            )
            .rename_axis("Type")
            .reset_index()
        )

    def price_band_stats(self):
        """Fiyat aralıklarına göre puan ve popülerlik."""
        bins = [-0.01, 0, 5, 10, 20, 40, float("inf")]
        labels = ["Free", "$0-5", "$5-10", "$10-20", "$20-40", "$40+"]
        bands = pd.cut(self.df["Price"], bins=bins, labels=labels)
        return (
            self.df.groupby(bands, observed=True)
            .agg(
                Games=("Name", "count"),
                Avg_Score=("Review Score", "mean"),
                Popular_Pct=("Owners Min", lambda x: (x >= 100000).mean() * 100),
            )
            .rename_axis("Price Band")
            .reset_index()
        )

    def releases_per_year(self):
        """Her yıl Steam'e çıkan oyun sayısı ve o yılın ortalama puanı."""
        return (
            self.df.groupby("Release Year")
            .agg(Games=("Name", "count"), Avg_Score=("Review Score", "mean"))
            .reset_index()
        )

    def top_games(self, n=10, min_reviews=1000):
        """En yüksek puanlı oyunlar (yeterince incelemesi olanlar arasından)."""
        popular = self.df[self.df["Total Reviews"] >= min_reviews]
        cols = ["Name", "Price", "Release Year", "Total Reviews", "Review Score"]
        return popular.nlargest(n, "Review Score")[cols].reset_index(drop=True)

    def find_game(self, name):
        """Adında verilen kelime geçen oyunları bulur."""
        mask = self.df["Name"].str.contains(name, case=False, na=False, regex=False)
        return self.df[mask]

    def compare_to_genre(self, game_name):
        """Bir oyunu kendi türlerindeki diğer oyunlarla karşılaştırır."""
        matches = self.df[self.df["Name"] == game_name]
        if matches.empty:
            return None
        game = matches.iloc[0]

        rows = []
        for genre in game["Genre List"]:
            same_genre = self.df[self.df["Genre List"].apply(lambda g: genre in g)]
            percentile = (same_genre["Review Score"] < game["Review Score"]).mean() * 100
            rows.append({
                "Genre": genre,
                "Games in Genre": len(same_genre),
                "Genre Avg Score": same_genre["Review Score"].mean(),
                "Game Score": game["Review Score"],
                "Better Than (%)": percentile,
            })
        return pd.DataFrame(rows)
