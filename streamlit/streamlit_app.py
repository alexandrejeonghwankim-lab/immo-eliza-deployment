import streamlit as st
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
BANNER_IMAGE = BASE_DIR / "image" / "Immo_Eliza_proper.png"

st.image(str(BANNER_IMAGE), use_container_width = True)


st.set_page_config(
    page_title="Immo-Eliza Price Prediction",
    layout="centered",
)

API_URL = "https://immo-eliza-deployment-ru4g.onrender.com/predict"

def wake_api():
    try:
        response = requests.get("https://immo-eliza-deployment-ru4g.onrender.com",
                                timeout=60)
        
        return response.status_code == 200

    except requests.exceptions.RequestException:
        return False

def get_coordinates(address):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "be",
    }

    headers = {
        "User-Agent": "immo-eliza-streamlit-app"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None, None

    try:
        results = response.json()
    except ValueError:
        return None, None

    if not results:
        return None, None

    latitude = float(results[0]["lat"])
    longitude = float(results[0]["lon"])

    return latitude, longitude


def empty_coordinate_to_none(value):
    if value == 0.0:
        return None
    return value


def optional_surface_to_none(value):
    if value == 0:
        return None
    return value


def get_epc_options(province):
    flanders_provinces = [
        "Antwerp",
        "Flemish Brabant",
        "East Flanders",
        "West Flanders",
        "Limburg",
    ]

    wallonia_provinces = [
        "Walloon Brabant",
        "Hainaut",
        "Liege",
        "Luxembourg",
        "Namur",
    ]

    if province == "Brussels":
        return [
            "Unknown",
            "BrusselsA",
            "BrusselsB",
            "BrusselsC",
            "BrusselsD",
            "BrusselsE",
            "BrusselsF",
            "BrusselsG",
        ]

    if province in flanders_provinces:
        return [
            "Unknown",
            "FlandersDoubleA",
            "FlandersSingleA",
            "FlandersB",
            "FlandersC",
            "FlandersD",
            "FlandersE",
            "FlandersF",
        ]

    if province in wallonia_provinces:
        return [
            "Unknown",
            "WalloniaTripleA",
            "WalloniaDoubleA",
            "WalloniaSingleA",
            "WalloniaB",
            "WalloniaC",
            "WalloniaD",
            "WalloniaE",
            "WalloniaF",
            "WalloniaG",
        ]

    return ["Unknown"]


def validate_inputs(livable_surface, postal_code):
    errors = []

    if livable_surface <= 0:
        errors.append("Put a number greater than 0 for livable surface.")

    if not postal_code:
        errors.append("Postal code is required.")

    if postal_code and not postal_code.isdigit():
        errors.append("Postal code must contain only numbers.")

    if postal_code and len(postal_code) != 4:
        errors.append("Postal code must be 4 digits.")

    return errors



st.title("Immo-Eliza: Property Price Prediction in Belgium")
st.write(
    "Estimate the sale price of a Belgian house or apartment using a deployed "
    "machine learning API. Fill in the known property details below; optional "
    "fields can be left blank or set to 0."
)

st.divider()

st.header("Property Information")
left_col, right_col = st.columns(2)

with left_col:
    category = st.radio(
        "Property type",
        ["house", "apartment"],
        horizontal=True,
    )

    livable_surface = st.number_input(
        "Livable surface in m2",
        min_value=0,
        step=1,
        help="Required. Enter the indoor livable area of the property.",
    )

    total_land_surface = st.number_input(
        "Total land surface optional",
        min_value=0,
        step=1,
        help="Use this for houses or properties with land. Leave 0 if unknown.",
    )

with right_col:
    bedrooms = st.number_input(
        "Number of bedrooms",
        min_value=0,
        step=1,
    )

    bathrooms = st.number_input(
        "Number of bathrooms",
        min_value=0,
        step=1,
    )

    toilets = st.number_input(
        "Number of toilets",
        min_value=0,
        step=1,
    )

st.divider()

st.header("Location Information")
left_col, right_col = st.columns(2)

with left_col:
    province = st.selectbox(
        "Province",
        [
            "Brussels",
            "Antwerp",
            "Flemish Brabant",
            "Walloon Brabant",
            "East Flanders",
            "West Flanders",
            "Hainaut",
            "Liege",
            "Limburg",
            "Luxembourg",
            "Namur",
        ],
    )

    postal_code = st.text_input(
        "Postal code",
        placeholder="Four digits only, e.g. 1000",
    )

with right_col:
    address = st.text_input(
        "Address optional",
        placeholder="Example: Rue Neuve 123, Brussels",
        help="Used only to estimate latitude and longitude more precisely.",
    )

    latitude = st.number_input(
        "Latitude optional",
        value=0.0,
        format="%.6f",
        help="Leave 0 if unknown. Address or postal code can be used instead.",
    )

    longitude = st.number_input(
        "Longitude optional",
        value=0.0,
        format="%.6f",
        help="Leave 0 if unknown. Address or postal code can be used instead.",
    )

st.caption("EPC options are based on the selected province. The address is only used to find latitude and longitude.")

st.divider()

st.header("Energy and Equipment")
left_col, right_col = st.columns(2)

with left_col:
    epc = st.radio(
        "EPC score",
        get_epc_options(province),
    )

    if epc == "Unknown":
        epc = None

with right_col:
    kitchen_equipment = st.radio(
        "Kitchen equipment",
        [
            "Unknown",
            "Super equipped",
            "Fully equipped",
            "Partially equipped",
            "Not equipped",
        ],
    )

    if kitchen_equipment == "Unknown":
        kitchen_equipment = None

st.divider()

st.header("Optional Information")
left_col, right_col = st.columns(2)

with left_col:
    garden = st.checkbox("Garden")
    terrace = st.checkbox("Terrace")
    swimming_pool = st.checkbox("Swimming pool")
    fireplace = st.checkbox("Fireplace")
    solar_panels = st.checkbox("Solar panels")

with right_col:
    air_conditioning = st.checkbox("Air conditioning")
    vat = st.checkbox("Mandatory to pay VAT (new building)")
    electrical_certificate = st.checkbox("Electrical certificate")
    security_door = st.checkbox("Security door")
    hammam_sauna_jacuzzi = st.checkbox("Hammam / Sauna / Jacuzzi")

st.divider()

st.header("Prediction")
st.write("Click the button after filling in the property information.")

if st.button("Predict price", type="primary", use_container_width=True):
    errors = validate_inputs(livable_surface, postal_code)

    if errors:
        for error in errors:
            st.error(error)
        st.stop()

    final_latitude = empty_coordinate_to_none(latitude)
    final_longitude = empty_coordinate_to_none(longitude)
    final_total_land_surface = optional_surface_to_none(total_land_surface)

    if address:
        geocoded_latitude, geocoded_longitude = get_coordinates(address)

        if geocoded_latitude is None or geocoded_longitude is None:
            st.warning(
                "The address could not be converted to coordinates. "
                "The app will use the latitude and longitude values from the form."
            )
        else:
            final_latitude = geocoded_latitude
            final_longitude = geocoded_longitude
            st.success(
                f"Address found: latitude {final_latitude:.6f}, "
                f"longitude {final_longitude:.6f}"
            )

    property_data = {
        "category": category,
        "livable_surface": livable_surface,
        "total_land_surface": final_total_land_surface,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "toilets": toilets,
        "province": province,
        "postal_code": postal_code,
        "latitude": final_latitude,
        "longitude": final_longitude,
        "epc": epc,
        "kitchen_equipment": kitchen_equipment,
        "garden": garden,
        "terrace": terrace,
        "swimming_pool": swimming_pool,
        "fireplace": fireplace,
        "solar_panels": solar_panels,
        "air_conditioning": air_conditioning,
        "vat": vat,
        "electrical_certificate": electrical_certificate,
        "security_door": security_door,
        "hammam_sauna_jacuzzi": hammam_sauna_jacuzzi,
    }

    with st.spinner("Waking up prediction API....."):
        api_awake = wake_api()

    if not api_awake:
        st.warning("THe API may still be waking up, Prediction can take longer.")

    try:
        response = requests.post(API_URL, json=property_data, timeout=90)

        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicted price: {result['prediction']:,.2f} EUR")
        else:
            st.error("The prediction API returned an error.")
            st.write(response.text)

    except requests.exceptions.Timeout:
        st.error(
            "The prediction API took too long to answer. "
            "If the Render service was sleeping, wait one minute and try again."
        )

    except requests.exceptions.RequestException as error:
        st.error("Could not connect to the prediction API.")
        st.write(error)

    with st.expander("Request data sent to the API"):
        st.write(property_data)
