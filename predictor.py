import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Dict, Tuple

class WeatherPredictor:
    @staticmethod
    def predict_temperature_trend(temperatures: List[float], hours_ahead: int = 24) -> Tuple[List[float], float]:
        """Predict temperature trend using linear regression."""
        if len(temperatures) < 3:
            return [], 0.0
        
        try:
            X = np.arange(len(temperatures)).reshape(-1, 1)
            y = np.array(temperatures)

            model = LinearRegression()
            model.fit(X, y)

            future_X = np.arange(len(temperatures), len(temperatures) + hours_ahead).reshape(-1, 1)
            predictions = model.predict(future_X)
            confidence = model.score(X, y)
            return predictions.tolist(), confidence
        except Exception as e:
            print(f"Error in temperature prediction: {str(e)}")
            return [], 0.0
        
    @staticmethod
    def analyze_weather_patterns(df: pd.DataFrame) -> Dict:
        """Analyze weather patterns from forecast data."""
        analysis = {}

        analysis['temp_trend'] = 'stable'
        temp_diff = df['temperature'].iloc[-1] - df['temperature'].iloc[0]
        if temp_diff > 2:
            analysis['temp_trend'] = 'warming'
        elif temp_diff < -2:
            analysis['temp_trend'] = 'cooling'

        # Rain probability
        analysis['rain_likelihood'] = df['pop'].mean()
        analysis['max_rain_prob'] = df['pop'].max()
        
        # Weather diversity
        analysis['weather_types'] = df['weather_main'].nunique()
        analysis['dominant_weather'] = df['weather_main'].mode().iloc[0]

        return analysis