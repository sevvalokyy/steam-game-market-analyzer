import pandas as pd


class DataCleaner:
    """Ham Steam verisini analize hazır hale getirir."""

    def __init__(self, df, min_reviews=10):
        self.df = df.copy()
        self.min_reviews = min_reviews

    def remove_non_games(self):
        self.df = self.df[self.df["Type"] == "game"]

    def drop_unused_columns(self):
        self.df = self.df.drop(columns=["Website", "Short Description", "Required Age", "Type"])

    def drop_missing(self):
        self.df = self.df.dropna(subset=["Genre", "Release Date"])

    def convert_price(self):
        self.df["Price"] = self.df["Price"] / 100
        self.df["Initial Price"] = self.df["Initial Price"] / 100

    def parse_owners(self):
        bounds = (
            self.df["Owners"]
            .str.replace(",", "")
            .str.split(" .. ", expand=True)
            .astype(int)
        )
        self.df["Owners Min"] = bounds[0]
        self.df["Owners Max"] = bounds[1]
        self.df["Owners Mid"] = (bounds[0] + bounds[1]) / 2

    def parse_release_date(self):
        self.df["Release Date"] = pd.to_datetime(
            self.df["Release Date"], format="%Y/%m/%d", errors="coerce"
        )
        self.df = self.df.dropna(subset=["Release Date"])
        self.df["Release Year"] = self.df["Release Date"].dt.year

    def add_review_metrics(self):
        total = self.df["Positive Reviews"] + self.df["Negative Reviews"]
        self.df["Total Reviews"] = total
        self.df["Review Score"] = self.df["Positive Reviews"] / total

    def filter_min_reviews(self):
        self.df = self.df[self.df["Total Reviews"] >= self.min_reviews]

    def split_genres(self):
        self.df["Genre List"] = self.df["Genre"].str.split(", ")

    def remove_software(self):
        software = {
            "Game Development", "Design & Illustration", "Education",
            "Animation & Modeling", "Utilities", "Software Training",
            "Video Production", "Audio Production", "Photo Editing",
            "Web Publishing", "Accounting",
        }
        is_software = self.df["Genre List"].apply(lambda g: any(x in software for x in g))
        self.df = self.df[~is_software]

    def clean(self):
        """Tüm temizlik adımlarını sırayla çalıştırır."""
        self.remove_non_games()
        self.drop_unused_columns()
        self.drop_missing()
        self.convert_price()
        self.parse_owners()
        self.parse_release_date()
        self.add_review_metrics()
        self.filter_min_reviews()
        self.split_genres()
        self.remove_software()
        return self.df.reset_index(drop=True)
