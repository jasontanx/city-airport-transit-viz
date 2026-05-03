# Project Overview

This is a **Python/Streamlit web application** named "Global Airport Transit Explorer" (focusing primarily on Southeast Asia). The application provides an interactive infographic that allows users to compare how quickly and efficiently they can travel from various airports to their respective city centers. 

It visualizes transit data using interactive charts and maps, specifically:
- A Radial Map (bullseye) standardizing distances to the city center.
- A Dumbbell Chart for direct distance and time comparison.
- A Transfer Focus visualization showing route segments, train lines, and transit operators with custom badges and logos.
- A detailed data grid including travel times, distances, speeds, and pricing information.

## Main Technologies
- **Python**
- **Streamlit**: For the interactive web interface.
- **Pandas**: For data loading, filtering, sorting, and manipulation.
- **Plotly (`plotly.express`, `plotly.graph_objects`)**: For generating interactive visualizations (radial maps, scatter plots).
- **JSON**: The primary data source (`airport_transit_data.json`).

## Directory Structure
- `app.py`: The main Streamlit application script.
- `airport_transit_data.json`: The dataset containing city, airport, distance, time, train operator, coordinate, segment, and pricing data.
- `requirements.txt`: Python package dependencies.
- `city_icon_image/`: Contains custom city icon images (e.g., Kuala Lumpur, Singapore, Bangkok, Jakarta) used in the charts.
- `train_operator_image/`: Contains images related to train operators.
- `train_operator_logo/`: Contains logos for various transit operators (e.g., ERL, SMRT, BTS) displayed in the transfer focus visualizations.

## Building and Running

1. **Activate the Virtual Environment**:
   If not already activated, activate the existing virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

## Development Conventions
- **Styling**: The application utilizes a combination of Streamlit's native layout features, Plotly's dark templates (`plotly_dark`), and raw HTML/CSS injected via `st.markdown(..., unsafe_allow_html=True)` to create custom badges, logos, and UI elements.
- **Data Caching**: The application uses Streamlit's `@st.cache_data` decorator to cache the loading of the JSON data and the base64 encoding of images to improve performance.
- **Modifying Data**: To add new cities or transit routes, update the `airport_transit_data.json` file following the existing schema. Ensure any corresponding logos or images are added to the appropriate image directories and mapped correctly in `app.py` (e.g., inside `get_city_drawing` and `generate_logo_badge` functions).