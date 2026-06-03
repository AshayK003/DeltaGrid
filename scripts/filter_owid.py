import pandas as pd

df = pd.read_csv("data/raw/owid-energy-data.csv", low_memory=False)
df = df[df["year"].between(2010, 2025)]
df.to_csv("data/raw/owid-energy-data-2010-2025.csv", index=False)
print(f"Filtered: {len(df)} rows, years {df['year'].min()}-{df['year'].max()}")
