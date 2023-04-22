import streamlit as st
import datetime
import pytz
from utils.predicthq import get_api_key, get_predicthq_client
from utils.code_examples import get_code_example


def show_sidebar_options():
    locations = [
        {
            "id": "seattle",
            "name": "1417 Bellevue Ave, Seattle",
            "address": "1417 Bellevue Ave, Seattle, WA 98122, USA",
            "lat": 47.61354,
            "lon": -122.32712,
            "tz": "America/Los_Angeles",
            "units": "imperial",
        },
        {
            "id": "san-diego",
            "name": "1351 Fifth Ave, San Diego",
            "address": "1351 Fifth Ave, San Diego, CA 92101, USA",
            "lat": 32.71963,
            "lon": -117.15992,
            "tz": "America/Los_Angeles",
            "units": "imperial",
        },
        {
            "id": "phoenix",
            "name": "1616 N Central Ave, Phoenix",
            "address": "1616 N Central Ave, Phoenix, AZ 85003, USA",
            "lat": 33.46647,
            "lon": -112.07523,
            "tz": "America/Los_Angeles",
            "units": "imperial",
        },
        {
            "id": "los-angeles",
            "name": "1234 Wilshire Blvd, Los Angeles",
            "address": "1234 Wilshire Blvd, Los Angeles, CA 90017, USA",
            "lat": 34.05345,
            "lon": -118.26593,
            "tz": "America/Los_Angeles",
            "units": "imperial",
        },
        {
            "id": "chicago",
            "name": "3639 N Fremont St, Chicago",
            "address": "3639 N Fremont St, Chicago, IL 60613, USA",
            "lat": 41.94786,
            "lon": -87.65185,
            "tz": "America/Chicago",
            "units": "imperial",
        },
        {
            "id": "miami",
            "name": "1350 NE 2nd Ave, Miami",
            "address": "1350 NE 2nd Ave, Miami, FL 33132, USA",
            "lat": 25.78780,
            "lon": -80.19065,
            "tz": "America/New_York",
            "units": "imperial",
        },
        {
            "id": "cleveland",
            "name": "750 Vincent Ave., Cleveland",
            "address": "750 Vincent Ave., Cleveland, OH 44114, USA",
            "lat": 41.50081,
            "lon": -81.68837,
            "tz": "America/New_York",
            "units": "imperial",
        },
        {
            "id": "nashville",
            "name": "107 4th Ave N, Nashville",
            "address": "107 4th Ave N, Nashville, TN 37219, USA",
            "lat": 36.16145,
            "lon": -86.77756,
            "tz": "America/Chicago",
            "units": "imperial",
        },
        {
            "id": "cincinnati",
            "name": "321 Central Ave #2270, Cincinnati",
            "address": "321 Central Ave #2270, Cincinnati, OH 45202, USA",
            "lat": 39.09906,
            "lon": -84.51917,
            "tz": "America/New_York",
            "units": "imperial",
        },
    ]

    # Work out which location is currently selected
    index = 0

    if "location" in st.session_state:
        for idx, location in enumerate(locations):
            if st.session_state["location"]["id"] == location["id"]:
                index = idx
                break

    location = st.sidebar.selectbox(
        "Parking Building",
        locations,
        index=index,
        format_func=lambda x: x["name"],
        help="Select the parking building location.",
        disabled=get_api_key() is None,
        key="location",
    )

    # Prepare the date range (today + 30d as the default)
    tz = pytz.timezone(location["tz"])
    today = datetime.datetime.now(tz).date()
    date_options = [
        {
            "id": "next_7_days",
            "name": "Next 7 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=7),
        },
        {
            "id": "next_30_days",
            "name": "Next 30 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=30),
        },
        {
            "id": "next_90_days",
            "name": "Next 90 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=90),
        },
    ]

    # Work out which date is currently selected
    index = 2  # Default to next 90 days

    if "daterange" in st.session_state:
        for idx, date_option in enumerate(date_options):
            if st.session_state["daterange"]["id"] == date_option["id"]:
                index = idx
                break

    st.sidebar.selectbox(
        "Date Range",
        date_options,
        index=index,
        format_func=lambda x: x["name"],
        help="Select the date range for fetching event data.",
        disabled=get_api_key() is None,
        key="daterange",
    )

    # Use an appropriate radius unit depending on location
    radius_unit = (
        "mi" if "units" in location and location["units"] == "imperial" else "km"
    )

    st.session_state.suggested_radius = fetch_suggested_radius(
        location["lat"], location["lon"], radius_unit=radius_unit
    )

    # Allow changing the radius if needed (default to suggested radius)
    # The Suggested Radius API is used to determine the best radius to use for the given location and industry
    st.sidebar.slider(
        f"Suggested Radius around parking building ({radius_unit})",
        0.0,
        10.0,
        st.session_state.suggested_radius.get("radius", 2.0),
        0.1,
        help="[Suggested Radius Docs](https://docs.predicthq.com/resources/suggested-radius)",
        key="radius",
    )


@st.cache_data
def fetch_suggested_radius(lat, lon, radius_unit="mi", industry="parking"):
    phq = get_predicthq_client()
    suggested_radius = phq.radius.search(
        location__origin=f"{lat},{lon}", radius_unit=radius_unit, industry=industry
    )

    return suggested_radius.to_dict()


def show_map_sidebar_code_examples():
    st.sidebar.markdown("## Code examples")

    # The code examples are saved as markdown files in docs/code_examples
    examples = [
        {"name": "Suggested Radius API", "filename": "suggested_radius_api"},
        {
            "name": "Features API (Predicted Attendance aggregation)",
            "filename": "features_api",
        },
        {"name": "Count of Events", "filename": "count_api"},
        {"name": "Demand Surge API", "filename": "demand_surge_api"},
        {"name": "Search Events", "filename": "events_api"},
        {"name": "Python SDK for PredictHQ APIs", "filename": "python_sdk"},
    ]

    for example in examples:
        with st.sidebar.expander(example["name"]):
            st.markdown(get_code_example(example["filename"]))

    st.sidebar.caption(
        "Get the code for this app at [GitHub](https://github.com/predicthq/streamlit-parking-demo)"
    )
