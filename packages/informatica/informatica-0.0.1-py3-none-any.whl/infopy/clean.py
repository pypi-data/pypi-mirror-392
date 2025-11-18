import pandas as pd

def clean_missing(df: pd.DataFrame, strategy: str = "mean"):
    """
    Fill missing values in a DataFrame with a chosen strategy.
    Supported strategies: 'mean', 'median', 'mode', 'zero'
    Returns: (cleaned_df, explanation)
    """
    explanation = []
    cleaned = df.copy()

    for col in cleaned.select_dtypes(include="number").columns:
        if cleaned[col].isnull().any():
            if strategy == "mean":
                val = cleaned[col].mean()
                cleaned[col].fillna(val, inplace=True)
                explanation.append(f"Filled NaNs in {col} with mean={val:.2f}")
            elif strategy == "median":
                val = cleaned[col].median()
                cleaned[col].fillna(val, inplace=True)
                explanation.append(f"Filled NaNs in {col} with median={val:.2f}")
            elif strategy == "mode":
                val = cleaned[col].mode()[0]
                cleaned[col].fillna(val, inplace=True)
                explanation.append(f"Filled NaNs in {col} with mode={val}")
            elif strategy == "zero":
                cleaned[col].fillna(0, inplace=True)
                explanation.append(f"Filled NaNs in {col} with 0")

    return cleaned, explanation
