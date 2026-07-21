
import streamlit as st
import pandas as pd
import math
from  datetime import timezone
import altair as alt
st.set_page_config(initial_sidebar_state="expanded")
# libraries and set up for Open-Meteo API
import openmeteo_requests
import requests_cache
from retry_requests import retry
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Libraries and set up for SkyField API
from skyfield.api import load, wgs84

eph = load('de421.bsp')
earth = eph['earth']

# Libraries for geolocation
from streamlit_js_eval import get_geolocation


# coordinates top 50 major cities sorted in alpha order
MAJOR_CITIES = {
    "Atlanta": {"latitude": 33.7490, "longitude": -84.3880},
    "Austin": {"latitude": 30.2672, "longitude": -97.7431},
    "Baltimore": {"latitude": 39.2904, "longitude": -76.6122},
    "Birmingham": {"latitude": 33.5186, "longitude": -86.8104},
    "Boston": {"latitude": 42.3601, "longitude": -71.0589},
    "Buffalo": {"latitude": 42.8864, "longitude": -78.8784},
    "Charlotte": {"latitude": 35.2271, "longitude": -80.8431},
    "Chicago": {"latitude": 41.8781, "longitude": -87.6298},
    "Cincinnati": {"latitude": 39.1031, "longitude": -84.5120},
    "Cleveland": {"latitude": 41.4993, "longitude": -81.6944},
    "Columbus": {"latitude": 39.9612, "longitude": -82.9988},
    "Dallas": {"latitude": 32.7767, "longitude": -96.7970},
    "Denver": {"latitude": 39.7392, "longitude": -104.9903},
    "Detroit": {"latitude": 42.3314, "longitude": -83.0458},
    "Hartford": {"latitude": 41.7637, "longitude": -72.6851},
    "Houston": {"latitude": 29.7604, "longitude": -95.3698},
    "Indianapolis": {"latitude": 39.7684, "longitude": -86.1581},
    "Jacksonville": {"latitude": 30.3322, "longitude": -81.6557},
    "Kansas City": {"latitude": 39.0997, "longitude": -94.5786},
    "Las Vegas": {"latitude": 36.1716, "longitude": -115.1391},
    "Los Angeles": {"latitude": 34.0522, "longitude": -118.2437},
    "Louisville": {"latitude": 38.2527, "longitude": -85.7585},
    "Memphis": {"latitude": 35.1495, "longitude": -90.0490},
    "Miami": {"latitude": 25.7617, "longitude": -80.1918},
    "Milwaukee": {"latitude": 43.0389, "longitude": -87.9065},
    "Minneapolis": {"latitude": 44.9778, "longitude": -93.2650},
    "Nashville": {"latitude": 36.1627, "longitude": -86.7816},
    "New Orleans": {"latitude": 29.9511, "longitude": -90.0715},
    "New York": {"latitude": 40.7128, "longitude": -74.0060},
    "Oklahoma City": {"latitude": 35.4676, "longitude": -97.5164},
    "Orlando": {"latitude": 28.5384, "longitude": -81.3789},
    "Philadelphia": {"latitude": 39.9526, "longitude": -75.1652},
    "Phoenix": {"latitude": 33.4484, "longitude": -112.0740},
    "Pittsburgh": {"latitude": 40.4406, "longitude": -79.9959},
    "Portland": {"latitude": 45.5152, "longitude": -122.6784},
    "Providence": {"latitude": 41.8240, "longitude": -71.4128},
    "Raleigh": {"latitude": 35.7796, "longitude": -78.6382},
    "Richmond": {"latitude": 37.5407, "longitude": -77.4360},
    "Riverside": {"latitude": 33.9806, "longitude": -117.3755},
    "Sacramento": {"latitude": 38.5816, "longitude": -121.4944},
    "Salt Lake City": {"latitude": 40.7608, "longitude": -111.8910},
    "San Antonio": {"latitude": 29.4241, "longitude": -98.4936},
    "San Diego": {"latitude": 32.7157, "longitude": -117.1611},
    "San Francisco": {"latitude": 37.7749, "longitude": -122.4194},
    "San Jose": {"latitude": 37.3387, "longitude": -121.8853},
    "Seattle": {"latitude": 47.6062, "longitude": -122.3321},
    "St. Louis": {"latitude": 38.6270, "longitude": -90.1994},
    "Tampa": {"latitude": 27.9506, "longitude": -82.4572},
    "Virginia Beach": {"latitude": 36.8529, "longitude": -75.9780},
    "Washington DC": {"latitude": 38.9072, "longitude": -77.0369}
}

# constants describing weight of penalty each element has on viewing_score
TYPE_WEIGHTS = {
    "faint": {
        "max_cloud_penalty": 35.0,
        "max_visibility_penalty": 25.0,
        "max_moon_penalty": 20.0,
        "max_bortle_penalty": 20.0
    },

    "bright": {
        "max_cloud_penalty": 50.0,
        "max_visibility_penalty": 30.0,
        "max_moon_penalty": 10.0,
        "max_bortle_penalty": 10.0,
    },

} 
penalties = {"cloud_penalty": [],
             "visibility_penalty": [],
             "moon_penalty": [],
             "bortle_penalty": [],
             "altitude_penalty": [],
             }







# display/run body of website
def display_visual(user_lat: str,
                    user_lon: str,):

    #draws graph containing viewing scores for specific night
    def draw_graph(penalties: dict):
        
        
        chart_df = pd.DataFrame({
            "time": final_data[1],
            "score": final_data[0],
            "moon_penalty": penalties["moon_penalty"],
            "visibility_penalty": penalties["visibility_penalty"],
            "cloud_penalty": penalties["cloud_penalty"],
            "bortle_penalty": penalties["bortle_penalty"],
            "altitude_penalty": penalties["altitude_penalty"],
        })
       
        penalty_cols = ["moon_penalty", "altitude_penalty", "cloud_penalty", "visibility_penalty", "bortle_penalty"]
        chart_df['score'] = pd.to_numeric(chart_df['score'])

        chart_df["worst_penalty_name"] = chart_df[penalty_cols].idxmax(axis=1)
        chart_df["least_penalty_name"] = chart_df[penalty_cols].idxmin(axis=1)
        
        #add warning if every hour shows score of 0
        if (max(final_data[0]) == 0):
            st.warning(f"{planet_choice} is not visible on {day_of_week} due to a/an {chart_df['worst_penalty_name'][0].replace('_', ' ').title()}")

        elif (min(final_data[0]) == 0):
            st.warning (f"{planet_choice} may not be visible some hours due to having an altitiude below horizon or full cloud coverage")

        chart = alt.Chart(chart_df).mark_bar().encode(
            x = alt.X('time:O', sort = None),
            y = alt.Y('score:Q', scale = alt.Scale(domain = [0,100])),

            #show user tooltip of score, penalty most affecting score, penalty least affecting score
            tooltip = [
                alt.Tooltip('score:Q', title = 'Score'),
                alt.Tooltip('worst_penalty_name:N', title = 'Worst Factor'),
                alt.Tooltip('least_penalty_name:N', title = 'Best Factor'),
            ],
            # color code bars based on viewing scores
            color = alt.Color(
                'score:Q',
                scale = alt.Scale(
                    type = 'threshold',
                    domain = [30,50, 70, 80],
                    range = ['darkred','orange', 'yellow', 'green', 'darkgreen']
                ),
                legend = None
            )
                

        )
        st.altair_chart(chart, width = 'stretch')
        st.caption("Showing viewing scores for the full calendar day (12 AM – 11 PM). Daylight hours with no visibility are excluded.", text_alignment = 'center')
    
    # calculates an estimated score from 0-100 based on the users ability to experience chosen planet
    def calculate_viewing_score(
        
        
        cloud_cover: float,
        visibility_meters: float,
        moon_illumination: float,
        bortle_rating: float,
        planet_altitude: float,
        planet_type: str,
    ) -> float:
        weights = TYPE_WEIGHTS.get(planet_type, TYPE_WEIGHTS[planet_type])
        

        #Cloud cover penalty --> exponentially weight based on cloud coverage
        cloud_cover_penalty = (((cloud_cover)/100) ** 2) * weights["max_cloud_penalty"]
        penalties["cloud_penalty"].append(int(cloud_cover_penalty))


        #visibility Penalty --> 10,000 meters max
        visibility_meters = min(visibility_meters, 10000)
        visibility_penalty = (((10000 - visibility_meters))/10000) * weights["max_visibility_penalty"]
        penalties["visibility_penalty"].append(int(visibility_penalty))

        #Moon illumination penalty
        moon_penalty = (moon_illumination/100) * weights["max_moon_penalty"]
        penalties["moon_penalty"].append(int(moon_penalty))

        #Bortle Light Pollution Penalty --> penalty scales exponentially
        bortle_ratio = bortle_rating / 9.0
        bortle_penalty = (bortle_ratio**2) * weights["max_bortle_penalty"]
        penalties["bortle_penalty"].append(int(bortle_penalty))

        # Planet altidude penalty --> handle bigger effects closer to horizon using airmass formula
        airmass = 1.0 / (math.sin(math.radians(planet_altitude + 5.0)))
        planet_multiplier = 1.0 - (airmass * .1)
        planet_multiplier = max(.1, min(1.0, planet_multiplier))

        #calculate total score
        before_planet_multiplier = 100 - (cloud_cover_penalty + visibility_penalty + moon_penalty + bortle_penalty)
        viewing_score = (before_planet_multiplier * planet_multiplier)
        penalties["altitude_penalty"].append(int(before_planet_multiplier - viewing_score))
        

        if ((visibility_meters < 2000) or (cloud_cover > 95)):
            viewing_score *= .2
        if (planet_altitude < 0):
            viewing_score = 0
            penalties["altitude_penalty"].pop()
            penalties["altitude_penalty"].append(100)
        return viewing_score

    #gets graph data for the day of week selected for every hour from sunset to sunrise
    def get_graph_data(day_of_week: "str", planet_choice: "str") -> list[int]:
        # array from sunset to sunrise of viewing scores
        scores_data = []
        time_data = []
        all_data = []

        #find target_index of day -> use to find sunrise/sunset and the days hourly data
        ordered_days = list(daily_dataframe["day_of_week"])
        target_index = ordered_days.index(day_of_week.title())

        target_row = daily_dataframe.iloc[target_index]
        target_sunset = target_row["sunset"]
        target_sunrise= target_row["sunrise"]


        sunset_hour = int(pd.to_datetime(target_sunset).hour)
        sunrise_hour = int(pd.to_datetime(target_sunrise).hour)


        target_date = pd.to_datetime(target_row["date"]).tz_localize(None).to_pydatetime()


        day_shift = target_index * 24




        # 1. Load the same celestial data for planets
        ts = load.timescale()
        eph = load('de421.bsp') 

        # 2. Get the current time
        now = ts.now()

        # 3. Quick calculation to find out how illuminated the moon is
        sun, moon, earth = eph['sun'], eph['moon'], eph['earth']
        #get data for morning viewing times
        for i in range(24):
            

            if (i < sunrise_hour or (i > sunset_hour)):
                specific_hour_time  = target_date.replace(hour = i, minute = 0, second = 0, microsecond =0, tzinfo=timezone.utc)
                current_time = ts.from_datetime(specific_hour_time)
        

                # Calculate positions relative to Earth
                e = earth.at(current_time)
                s = e.observe(sun).apparent()
                m = e.observe(moon).apparent()

                sep = s.separation_from(m)
                planet_target = eph[planet_choice.lower() + " barycenter"]
                
                position = observer.at(current_time).observe(planet_target)
                planet_alt, az, distance = position.apparent().altaz()
                planet_altitude = planet_alt.degrees
            
                moon_illumination = ((1.0 - math.cos(sep.radians)) / 2.0) * 100
            
                current_score = calculate_viewing_score(cloud_cover = hourly_data["cloud_cover"][i + day_shift],
                                                visibility_meters = hourly_data["visibility"][i+ day_shift], 
                                                moon_illumination = moon_illumination,
                                                bortle_rating = bortle_rating,
                                                planet_altitude = planet_altitude,
                                                planet_type = planets[planet_choice])

                scores_data.append(int(current_score))
                if (i > 12):
                    time_data.append(str(i-12) + " pm")
                elif (i==0):
                    time_data.append("12 am")
                else:
                    time_data.append(str(i) +" am")
        all_data.append(scores_data)
        all_data.append(time_data)
        
        
        return all_data

    
    
    user_location = {
        "latitude": user_lat,
        "longitude": user_lon
    }


    params = {
        "latitude": user_location["latitude"],
        "longitude": user_location["longitude"],
        "hourly": ["cloud_cover", "visibility"],
        "daily": ["sunrise", "sunset"],
        "timezone": "auto",
        
    }

    responses = openmeteo.weather_api(url, params = params)
    response = responses[0]
    

    # Process hourly data -> turn into dictionary (dataframe option available for debugging purposes)
    hourly = response.Hourly()
    hourly_cloud_cover = hourly.Variables(0).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(1).ValuesAsNumpy()
    hourly_data = {
        "date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        ).tz_convert(response.Timezone().decode())
    }

    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["visibility"] = hourly_visibility
    


    hourly_dataframe = pd.DataFrame(data = hourly_data)


    #process data daily -> turn into dictionary (dataframe option available for debugging purposes)
    daily = response.Daily()
    daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
    daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()
    
    daily_data = {
        "date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        ).tz_convert(response.Timezone().decode())
    }

    # convert UTC to local time and extract current day of week
    local_tz = response.Timezone().decode()
    daily_data["sunrise"] = pd.to_datetime(daily_sunrise, unit = "s", utc = True).tz_convert(local_tz).tz_localize(None)
    daily_data["sunset"] = pd.to_datetime(daily_sunset, unit = "s", utc = True).tz_convert(local_tz).tz_localize(None)
    daily_data["day_of_week"] = daily_data["date"].day_name()


    daily_dataframe = pd.DataFrame(data = daily_data)






    


    
    # 1. Tell Skyfield where the user is standing
    observer = earth + wgs84.latlon(user_location["latitude"], user_location["longitude"])

    # 2. Tell Skyfield what time it is right now
    ts = load.timescale()
    current_time = ts.now()






    # Algorithm to estimate closest major city
    min_distance = 1000000000
    bortle_rating = 0

    for city in MAJOR_CITIES:
        dif_longitude = MAJOR_CITIES[city]["longitude"] - user_location["longitude"]
        dif_latitude = MAJOR_CITIES[city]["latitude"] - user_location["latitude"]
        distance = (((dif_longitude ** 2) + (dif_latitude **2)) ** .5) * 69
        min_distance = min(distance, min_distance)



    # use distance to estimate bortle rating
    bortle_rating = (8 - (2 * ((min_distance-10)/10)))
    


    



    

    # create a button for user to select a Planet
    planets = {"Mercury": "bright" , "Venus": "bright", "Mars": "bright", 'Jupiter': "bright", "Saturn": "bright", "Uranus": "faint", "Neptune": "faint"}
    planet_choice = st.selectbox(label = "Select a Planet", options = planets, width = 100)


    # find target_index of day -> use to find sunrise/sunset and the days hourly data
    ordered_days = list(daily_dataframe["day_of_week"])


    #get day of week selected from user
    day_of_week = st.selectbox("Which day of the week?", list(ordered_days))

    #get data for week and planet selected by user and draw graph to visualize the data
    final_data = get_graph_data(day_of_week = day_of_week, planet_choice = planet_choice)
    draw_graph(penalties = penalties)


# Make sure all required weather variables are listed here

url = "https://api.open-meteo.com/v1/forecast"


# Retrieve user geolocation data and store it
location_data = get_geolocation()
user_location = {}



# create basic UI layout
st.markdown(
    """
    <style>
    .block-container {
        
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("Planet Peeker", text_alignment='center')
st.caption("### *An Astronomical Analysis & Observation Tool*", text_alignment = 'center')
st.sidebar.header("Location Settings")
use_manual = st.sidebar.checkbox("Manually Select City")


# if user choses to manually select a city
if use_manual:
    selected_city = st.sidebar.selectbox("Select City", list(MAJOR_CITIES.keys()))
    user_location = MAJOR_CITIES[selected_city]
    user_lat = user_location["latitude"]  
    user_lon = user_location["longitude"]
    display_visual(user_lat = user_lat, user_lon = user_lon)
    with st.expander("How the Viewing Score is Calculated"):
        st.markdown("""
        **Planet Peeker** evaluates real-time atmospheric and orbital conditions to determine the optimal window for viewing planets in our solar system.
        
        * **Cloud Cover & Visibility:** Pulled live via Open-Meteo API to measure atmospheric clarity.
        * **Planetary Altitude:** Calculated via Skyfield ephemerides using airmass extinction formulas to penalize objects that are low or below the horizon
        * **Moon Illumination & Light Pollution:** Factors in lunar phase brightness and localized Bortle scale in order to measure and penalize sky glow.
        """)
    

# if user allows exact location to be accessed
elif location_data:
    if location_data and 'coords' in location_data and location_data['coords']:
        user_lat = location_data['coords']['latitude']
        user_lon = location_data['coords']['longitude']
        display_visual(user_lat = user_lat, user_lon = user_lon)
        with st.expander("How the Viewing Score is Calculated"):
            st.markdown("""
            **Planet Peeker** evaluates real-time atmospheric and orbital conditions to determine the optimal window for viewing planets in our solar system.
            
            * **Cloud Cover & Visibility:** Pulled live via Open-Meteo API to measure atmospheric clarity.
            * **Planetary Altitude:** Calculated via Skyfield ephemerides using airmass extinction formulas to penalize objects that are low or below the horizon
            * **Moon Illumination & Light Pollution:** Factors in lunar phase brightness and localized Bortle scale in order to measure and penalize sky glow.
            """)
    else:
        
        st.info("Please allow location access or manually enter a city. See button for menu labeled '>>' on the top left of the page")
    
    
# if user has not selected any form of location
else:
    st.write("Please allow location access in order to continue. See button for menu labeled '>>' on the top left of the page")
    


    