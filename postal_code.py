import pandas as pd  

df = pd.read_csv('data/listings_clean_duplicate_final.csv')
df["postal_code"] = df["postal_code"].astype(str)

postal_coordinates = (
    df.dropna(subset = ["postal_code", "latitude", "longitude"]).groupby("postal_code")[["latitude", "longitude"]].median().reset_index()

)

postal_coordinates.to_csv("data/postal_code_coordinates.csv", index=False)