from dataclasses import dataclass


@dataclass
class DataSourceStatus:

    source: str

    status: str

    last_update: str | None


def build_data_sources(
    weather,
    gpm,
    sentinel,
    terrain,
):

    return [

        DataSourceStatus(
            "OpenWeather",
            "Operational" if weather else "Unavailable",
            getattr(weather, "timestamp", None),
        ),

        DataSourceStatus(
            "NASA GPM",
            "Operational" if gpm else "Unavailable",
            None,
        ),

        DataSourceStatus(
            "Sentinel-2",
            sentinel.status if sentinel else "Unavailable",
            getattr(sentinel, "acquisition_date", None),
        ),

        DataSourceStatus(
            "Copernicus DEM",
            terrain.status if terrain else "Unavailable",
            None,
        ),

        DataSourceStatus(
            "FEMA",
            "Operational",
            None,
        ),

        DataSourceStatus(
            "OpenStreetMap",
            "Operational",
            None,
        ),
    ]