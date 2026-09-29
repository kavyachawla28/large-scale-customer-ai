import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

INPUT_FILE = "data/processed/churn_dataset.parquet"
OUTPUT_FILE = "data/processed/churn_predictions.parquet"

print("Loading churn dataset...")

df = pd.read_parquet(INPUT_FILE)

print(f"Customers: {len(df):,}")
print(f"Columns: {len(df.columns)}")

FEATURES = [
    "total_spend",
    "total_transactions",
    "avg_order_value",
    "total_quantity",
    "avg_discount",
    "avg_session_duration",
    "avg_pages_viewed",
    "category_count",
    "active_months",
    "days_since_last_purchase",
]

TARGET = "churned"

X = df[FEATURES]
y = df[TARGET]

print("\nTarget distribution:")
print(y.value_counts().sort_index())

print("\nSplitting data...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training rows: {len(X_train):,}")
print(f"Testing rows: {len(X_test):,}")

print("\nPreparing feature scaling...")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training matrix: {X_train_scaled.shape}")
print(f"Testing matrix: {X_test_scaled.shape}")
print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

model.fit(X_train, y_train)

print("Random Forest training completed.")
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

print("\nEvaluating model...")

y_pred = model.predict(X_test)
y_probability = model.predict_proba(X_test)[:, 1]

print("\nROC-AUC:")
print(f"{roc_auc_score(y_test, y_probability):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nGenerating churn predictions...")

df["churn_probability"] = model.predict_proba(X)[:, 1]

df["churn_prediction"] = model.predict(X)

df.to_parquet(
    OUTPUT_FILE,
    index=False,
    compression="snappy"
)

print("\nPrediction dataset created.")

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nPrediction distribution:")
print(df["churn_prediction"].value_counts().sort_index())

print("\nSample predictions:")
print(
    df[
        [
            "customer_id",
            "total_spend",
            "total_transactions",
            "days_since_last_purchase",
            "churned",
            "churn_probability",
            "churn_prediction",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print(f"\nOutput: {OUTPUT_FILE}")
print("\nFeature importance:")

feature_importance = (
    pd.DataFrame({
        "feature": FEATURES,
        "importance": model.feature_importances_,
    })
    .sort_values("importance", ascending=False)
)

print(feature_importance.to_string(index=False))