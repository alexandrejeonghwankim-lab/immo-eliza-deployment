from math import atan2, cos, radians, sin, sqrt

import pandas as pd


METRO_AREAS = {
    "Brussels": (50.8503, 4.3517),
    "Antwerp": (51.2194, 4.4025),
    "Ghent": (51.0543, 3.7174),
    "Liege": (50.6326, 5.5797),
    "Charleroi": (50.4108, 4.4446),
}

CITIES_50K = {
    "Bruges": (51.2093, 3.2247),
    "Namur": (50.4674, 4.8718),
    "Leuven": (50.8798, 4.7005),
    "Mons": (50.4542, 3.9523),
    "Aalst": (50.9360, 4.0355),
    "Hasselt": (50.9307, 5.3325),
    "Mechelen": (51.0259, 4.4775),
    "SintNiklaas": (51.1651, 4.1437),
    "LaLouviere": (50.4866, 4.1878),
    "Kortrijk": (50.8266, 3.2645),
    "Ostend": (51.2300, 2.9200),
    "Tournai": (50.6056, 3.3886),
    "Genk": (50.9650, 5.5000),
    "Roeselare": (50.9465, 3.1227),
    "Mouscron": (50.7449, 3.2064),
    "Verviers": (50.5890, 5.8624),
    "Lokeren": (51.1036, 3.9934),
}

ALL_CITIES = {**METRO_AREAS, **CITIES_50K}

postal_df = pd.read_csv("data/postal_code_coordinates.csv")

POSTAL_CODE_COORDINATES =dict(
    zip(
        postal_df["postal_code"].astype(str),
        zip(postal_df["latitude"], postal_df["longitude"])
    )
)

def add_coordinates_from_postal_code(df):
    df = df.copy()

    if "postal_code" not in df.columns:
        return df
    
    if "latitude" not in df.columns:
        df["latitude"] =None 

    if "longitude" not in df.columns:
        df["longitude"] = None

    def fill_coordinates(row):
        has_latitude = pd.notna(row["latitude"])
        has_longitude = pd.notna(row["longitude"])

        if has_latitude and has_longitude:
            return row

        postal_code = str(row["postal_code"])
        coordinates = POSTAL_CODE_COORDINATES.get(postal_code)

        if coordinates is None:
            return row

        row["latitude"] = coordinates[0]
        row["longitude"] = coordinates[1]

        return row
    
    return df.apply(fill_coordinates, axis = 1 )

def haversine(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


def remove_outliers_by_group(df, group_col="postal_code", k=1.5, min_group_size=20):
    if group_col not in df.columns:
        return df

    grouped_prices = df.groupby(group_col)["price"]
    group_size = grouped_prices.transform("size")
    q1 = grouped_prices.transform(lambda prices: prices.quantile(0.25))
    q3 = grouped_prices.transform(lambda prices: prices.quantile(0.75))
    iqr = q3 - q1

    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr
    small_group = group_size < min_group_size
    in_bounds = (df["price"] >= lower_bound) & (df["price"] <= upper_bound)

    return df[small_group | in_bounds]


def clean_data(df):
    df = df.copy()

    if  "price" in df.columns and "longitude" in df.columns and "latitude" in df.columns:
        df = df.dropna(subset=["longitude", "latitude"])

    if "category" in df.columns:
        df["category"] = df["category"].replace({"appartment": "apartment"})
        allowed = ["house", "apartment"]
        df = df[df["category"].isin(allowed)]

    if "price" in df.columns:
        df = df[(df["price"] > 50000) & (df["price"] < 5000000)]
        df = remove_outliers_by_group(
            df,
            group_col="postal_code",
            k=2,
            min_group_size=20,
        )
        q_99 = df["price"].quantile(0.99)
        df = df[df["price"] <= q_99]

    return df


def features_engineering(df):
    df = df.copy()

    df = add_coordinates_from_postal_code(df)

    epc_map = {
        "FlandersDoubleA": 4,
        "FlandersSingleA": 4,
        "BrusselsA": 4,
        "WalloniaTripleA": 4,
        "WalloniaDoubleA": 4,
        "WalloniaSingleA": 4,
        "FlandersB": 3,
        "BrusselsB": 3,
        "BrusselsC": 3,
        "WalloniaB": 3,
        "FlandersC": 2,
        "FlandersD": 2,
        "BrusselsD": 2,
        "BrusselsE": 2,
        "WalloniaC": 2,
        "WalloniaD": 2,
        "WalloniaE": 2,
        "FlandersE": 1,
        "FlandersF": 1,
        "BrusselsF": 1,
        "BrusselsG": 1,
        "WalloniaF": 1,
        "WalloniaG": 1,
    }

    if "epc" in df.columns:
        df["epc_ordinal"] = df["epc"].map(epc_map)

    if "kitchen_equipment" in df.columns:
        kitchen_map = {
            "Super equipped": 4,
            "Fully equipped": 3,
            "Partially equipped": 2,
            "Not equipped": 1,
        }
        df["kitchen_level"] = df["kitchen_equipment"].map(kitchen_map)

    if (
        "latitude" in df.columns
        and "longitude" in df.columns
        and df["latitude"].notna().all()
        and df["longitude"].notna().all()
    ):
        for city, (city_lat, city_lon) in ALL_CITIES.items():
            df[f"dist_{city.lower()}"] = df.apply(
                lambda row: haversine(
                    row["latitude"],
                    row["longitude"],
                    city_lat,
                    city_lon,
                ),
                axis=1,
            )
    else:
        for city in ALL_CITIES:
            df[f"dist_{city.lower()}"] = 0

    return df
