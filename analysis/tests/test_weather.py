import os

from analysis.environment import DEFAULT_STUDY_AREA
from analysis.weather import (
    get_forecast,
    ForecastData,
)


def test_weather_download():

    lat, lon = DEFAULT_STUDY_AREA.center

    weather = get_forecast(
        lat,
        lon,
        municipality=DEFAULT_STUDY_AREA.name,
        api_key=os.environ["OPENWEATHER_API_KEY"],
    )

    assert isinstance(
        weather,
        ForecastData,
    )


def test_weather_fields():

    lat, lon = DEFAULT_STUDY_AREA.center

    weather = get_forecast(
        lat,
        lon,
        municipality=DEFAULT_STUDY_AREA.name,
        api_key=os.environ["OPENWEATHER_API_KEY"],
    )

    assert isinstance(
        weather.timestamp,
        int,
    )

    assert isinstance(
        weather.municipality,
        str,
    )

    assert isinstance(
        weather.rainfall,
        float,
    )

    assert isinstance(
        weather.weather_condition,
        str,
    )

    assert isinstance(
        weather.temperature,
        float,
    )