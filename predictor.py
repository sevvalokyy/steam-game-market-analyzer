import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


class ReviewPredictor:
    """Bir oyunun olumlu inceleme alıp almayacağını tahmin eder.

    "Olumlu" = incelemelerin en az %80'i olumlu (Steam'deki
    "Very Positive" seviyesine yakın bir eşik).
    Sadece oyun çıkmadan önce bilinen bilgiler kullanılır:
    fiyat, çıkış yılı ve türler.
    """

    def __init__(self, threshold=0.8, random_state=42):
        self.threshold = threshold
        self.random_state = random_state
        self.model = RandomForestClassifier(
            n_estimators=200, max_depth=10, min_samples_leaf=20,
            random_state=random_state, n_jobs=1,
        )
        self.genres = []
        self.results = {}

    def _make_features(self, df):
        X = pd.DataFrame(index=df.index)
        X["Price"] = df["Price"]
        X["Is Free"] = (df["Price"] == 0).astype(int)
        X["Release Year"] = df["Release Year"]
        X["Genre Count"] = df["Genre List"].apply(len)
        for genre in self.genres:
            X[genre] = df["Genre List"].apply(lambda g: int(genre in g))
        return X

    def train(self, df, min_genre_games=100):
        """Modeli eğitir ve test verisindeki başarısını kaydeder."""
        counts = df["Genre List"].explode().value_counts()
        self.genres = sorted(counts[counts >= min_genre_games].index)

        X = self._make_features(df)
        y = (df["Review Score"] >= self.threshold).astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )
        self.model.fit(X_train, y_train)

        predictions = self.model.predict(X_test)
        majority = int(y_train.mean() >= 0.5)
        self.results = {
            "accuracy": accuracy_score(y_test, predictions),
            "baseline": (y_test == majority).mean(),
            "positive_rate": y.mean(),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }
        return self.results

    def feature_importance(self, n=10):
        """Modelin en çok dikkate aldığı özellikler."""
        importance = pd.DataFrame({
            "Feature": self.model.feature_names_in_,
            "Importance": self.model.feature_importances_,
        })
        return importance.nlargest(n, "Importance").reset_index(drop=True)

    def predict_proba(self, price, release_year, genres):
        """Verilen özelliklerdeki bir oyunun olumlu inceleme alma olasılığı."""
        game = pd.DataFrame({
            "Price": [price],
            "Release Year": [release_year],
            "Genre List": [list(genres)],
        })
        X = self._make_features(game)
        return self.model.predict_proba(X)[0][1]
