# 🌦️ Advanced Weather Forecast & Predictor

A comprehensive weather application built with Streamlit that provides real-time weather data, forecasts, and AI-powered predictions for cities worldwide.

## 📁 File Structure

```
weather_app/
│
├── main.py              # Main application file
├── config.py            # Configuration and API settings
├── styles.py            # CSS styles and UI theming
├── city_search.py       # City search and geocoding functionality
├── weather_api.py       # Weather API integration
├── data_processor.py    # Data processing and formatting
├── predictor.py         # AI prediction models
├── weather_map.py       # Interactive map components
├── ui_components.py     # UI components and displays
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🚀 Features

- **🌍 Global City Search**: Search for any city worldwide with autocomplete suggestions
- **🌤️ Real-time Weather**: Current weather conditions with detailed metrics
- **📈 5-Day Forecast**: Interactive charts showing temperature, humidity, wind, and rain probability
- **🔮 AI Predictions**: Machine learning-powered temperature trend predictions
- **⚖️ City Comparison**: Compare weather conditions across multiple cities
- **🗺️ Interactive Maps**: Visualize weather data on interactive world maps
- **📊 Weather Insights**: Analyze weather patterns and trends
- **🎨 Modern UI**: Beautiful, responsive design with smooth animations

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- OpenWeatherMap API key (free at https://openweathermap.org/api)

### Step 1: Clone or Download Files
Create a new directory and save all the provided files:
```bash
mkdir weather_app
cd weather_app
```

Save the following files in your directory:
- `main.py`
- `config.py`
- `styles.py`
- `city_search.py`
- `weather_api.py`
- `data_processor.py`
- `predictor.py`
- `weather_map.py`
- `ui_components.py`
- `requirements.txt`

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key
1. Get your free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Open `config.py`
3. Replace the API_KEY value with your actual API key:
   ```python
   API_KEY = "your_actual_api_key_here"
   ```

⚠️ **Important**: New API keys can take up to 2 hours to activate!

### Step 4: Run the Application
```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📝 Usage Instructions

### Main Features:

1. **Search Cities**: 
   - Type any city name in the search box
   - Select from autocomplete suggestions
   - Or choose from popular cities list

2. **View Weather Data**:
   - Current conditions with temperature, humidity, wind speed
   - 5-day forecast with interactive charts
   - AI-powered temperature predictions

3. **Compare Cities**:
   - Add multiple cities for comparison
   - View side-by-side weather data
   - Interactive comparison charts and maps

4. **Navigate the Interface**:
   - Use tabs to switch between different chart views
   - Hover over charts for detailed information
   - Click on map markers for city details

## 🔧 Troubleshooting

### Common Issues:

**API Key Problems:**
- Make sure your API key is valid and active
- New keys need up to 2 hours to activate
- Check your API usage limits

**Installation Issues:**
- Ensure Python 3.8+ is installed
- Try upgrading pip: `pip install --upgrade pip`
- Install dependencies one by one if batch installation fails

**City Search Not Working:**
- Check internet connection
- Verify API key in config.py
- Try searching with just city name (e.g., "London" instead of "London, UK")

**Charts Not Displaying:**
- Clear browser cache
- Check if all dependencies are installed
- Try refreshing the page

## 🎯 Key Components Explained

### `main.py`
- Main application orchestration
- Session state management
- User interface coordination

### `config.py`
- API configuration
- Cache settings
- API key validation

### `weather_api.py`
- OpenWeatherMap API integration
- Data fetching with caching
- Error handling

### `ui_components.py`
- Streamlit UI components
- Interactive charts and displays
- User input handling

### `predictor.py`
- Machine learning predictions
- Weather pattern analysis
- Temperature trend forecasting

## 📊 API Information

This application uses the [OpenWeatherMap API](https://openweathermap.org/api):
- **Current Weather Data**: Real-time weather conditions
- **5-Day Forecast**: Weather predictions every 3 hours
- **Geocoding API**: City search and coordinates

**API Limits (Free Plan):**
- 1,000 calls per day
- 60 calls per minute
- Data updates every 2 hours

## 🔄 Updates and Maintenance

To update the application:
1. Replace the old files with new versions
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Restart the Streamlit application

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify your API key and internet connection
3. Ensure all dependencies are correctly installed
4. Check the Streamlit documentation for UI-related issues

## 🌟 Tips for Best Experience

- **Search Tips**: Use simple city names for better results
- **Performance**: The app caches data for 5 minutes to improve speed
- **Mobile**: Works on mobile devices but desktop experience is recommended
- **Multiple Cities**: Add up to 10 cities for comparison for optimal performance

---

**Built with ❤️ using Streamlit and OpenWeatherMap API**