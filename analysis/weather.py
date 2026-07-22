import os
import requests
from dataclasses import dataclass
from typing import List, Optional


class WeatherServiceError(Exception):
    """Raised when the weather service cannot be reached or returns an error."""
    pass


@dataclass
class ForecastAlert:
    event: str
    description: str
    start: int
    end: int


@dataclass
class ForecastData:
    timestamp: int
    municipality: str
    rainfall: float
    weather_condition: str
    temperature: float
    alerts: Optional[List[ForecastAlert]] = None


def get_forecast(
    lat: float,
    lon: float,
    api_key: Optional[str] = None,
    municipality: str = "",
) -> ForecastData:
    """
    Retrieves weather forecast data from OpenWeather and
    normalizes it into a ForecastData object.
    """

    key = api_key or os.getenv("OPENWEATHER_API_KEY")

    if not key:
        raise WeatherServiceError(
            "OPENWEATHER_API_KEY environment variable is not configured."
        )

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": key,
        "units": "metric"
    }

    headers = {
        "User-Agent": "MunicipalFloodIntelligenceAgent/1.0"
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15
        )

    except requests.Timeout:
        raise WeatherServiceError(
            "OpenWeather request timed out."
        )

    except requests.ConnectionError:
        raise WeatherServiceError(
            "Unable to connect to OpenWeather."
        )

    except requests.RequestException as e:
        raise WeatherServiceError(
            f"Weather request failed: {e}"
        )

    if response.status_code == 401:
        raise WeatherServiceError(
            "Invalid OpenWeather API key."
        )

    if response.status_code == 429:
        raise WeatherServiceError(
            "OpenWeather API rate limit exceeded."
        )

    if response.status_code >= 500:
        raise WeatherServiceError(
            "OpenWeather service is temporarily unavailable."
        )

    if response.status_code != 200:
        raise WeatherServiceError(
            f"Unexpected OpenWeather response ({response.status_code}): {response.text}"
        )

    try:
        data = response.json()

    except ValueError:
        raise WeatherServiceError(
            "OpenWeather returned invalid JSON."
        )

    forecasts = data.get("list")

    if not forecasts:
        raise WeatherServiceError(
            "OpenWeather returned no forecast data."
        )

    first = forecasts[0]

    rainfall = 0.0

    rain = first.get("rain")

    if isinstance(rain, dict):

        rainfall = float(
            rain.get("3h")
            or rain.get("1h")
            or 0.0
        )

    weather_condition = "Unknown"

    weather = first.get("weather")

    if (
        isinstance(weather, list)
        and len(weather) > 0
    ):
        weather_condition = weather[0].get(
            "main",
            "Unknown"
        )

    temperature = float(
        first.get("main", {}).get(
            "temp",
            0.0
        )
    )

    alerts = None

    if isinstance(data.get("alerts"), list):

        alerts = []

        for alert in data["alerts"]:

            alerts.append(
                ForecastAlert(
                    event=alert.get(
                        "event",
                        "Unknown Alert"
                    ),
                    description=alert.get(
                        "description",
                        ""
                    ),
                    start=alert.get(
                        "start",
                        0
                    ),
                    end=alert.get(
                        "end",
                        0
                    )
                )
            )

    timestamp = first.get("dt")

    if timestamp is None:
        raise WeatherServiceError(
            "Forecast timestamp missing."
        )

    return ForecastData(
        timestamp=int(timestamp),
        municipality=municipality,
        rainfall=rainfall,
        weather_condition=weather_condition,
        temperature=temperature,
        alerts=alerts,
    )