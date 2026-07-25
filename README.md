# Planet Peeker
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://planet-peeker-gwtm75aghvrkhzahaubagt.streamlit.app/)

> **🚀 Live Demo:** Try out the interactive app live at [Planet Peeker on Streamlit](https://planet-peeker-gwtm75aghvrkhzahaubagt.streamlit.app/)!

## About the Project

![Planet Peeker Demo](ezgif-2575e1c1052253de.gif)

Planet Peeker is a planetary observation tool that easily allows users to determine night sky visibility for a planet. Planet Peeker calculates real-time visibility scores based on exact user geolocation (if given access) and displays it in an easy to understand UI chart. 

### Key Features and Highlights:

- Hovering over a selected bar shows a **tooltip** with important information including the exact **visibility score** and the **biggest** and **smallest penalties** affecting the score

- **Factors in the scoring algorithm include**: visibility, cloud coverage, moon illumination, Bortle rating, and planet altitude

- **Note on empty bars:** Some bars may appear empty due to extreme climate interference or a planet altitude falling below the horizon  


<br>

## Built With  

<br>

- [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)  
- [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)  
- [![Vega-Altair](https://img.shields.io/badge/Vega--Altair-FFFFFF?style=for-the-badge&logo=vega&logoColor=4C78A8&labelColor=F28E2B)](https://altair-viz.github.io/)
- [![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)  
- [![Open-Meteo](https://img.shields.io/badge/Open--Meteo-1E61B1?style=for-the-badge&logo=icloud&logoColor=white)](https://open-meteo.com/)  
- [![Skyfield](https://img.shields.io/badge/Skyfield-0B1D3A?style=for-the-badge&logo=nasa&logoColor=white)](https://rhodesmill.org/skyfield/)  

<br>

## Getting Started

#### To run Planet Peeker locally on your machine:

1. **Clone the repository**

    ```bash 
    git clone https://github.com/villacarter2-a11y/planet-peeker
    cd planet-peeker
    ```
2. **Install Dependencies and Run the App**:
    ```bash
    python -m pip install -r requirements.txt
    python -m streamlit run app.py
## Contact / Author

* **Carter Villa** - [GitHub](https://github.com/villacarter2-a11y) | [LinkedIn](https://www.linkedin.com/in/carter-villa-a32040421/)

