import streamlit as st


def render_metrics(
    findings,
    weather=None,
    last_update=None,
):

    forecast = "--"

    observed = "--"

    ndwi = "--"

    surface = "--"

    elevation = "--"

    slope = "--"

    if findings:

        environment = findings.get(
            "environmental_assessment",
            {},
        )

        forecast = environment.get(
            "forecast_rainfall_mm",
            "--",
        )

        observed = environment.get(
            "observed_rainfall_mm",
            "--",
        )

        ndwi = environment.get(
            "ndwi",
            "--",
        )

        surface = environment.get(
            "surface_water_area_m2",
            "--",
        )

        elevation = environment.get(
            "mean_elevation_m",
            "--",
        )

        slope = environment.get(
            "mean_slope_percent",
            "--",
        )

    c1, c2, c3, c4, c5, c6 = st.columns(
        6,
        gap="medium",
    )

    c1.metric(

        "🌧 Latest Rainfall",

        (
            f"{observed:.2f} mm"
            if isinstance(observed, (int, float))
            else "--"
        ),
    )

    c2.metric(

        "🌦 Forecast",

        (
            f"{forecast:.2f} mm"
            if isinstance(forecast, (int, float))
            else "--"
        ),
    )

    c3.metric(

        "💧 NDWI",

        (
            f"{ndwi:.3f}"
            if isinstance(ndwi, (int, float))
            else "--"
        ),
    )

    c4.metric(

        "🌊 Surface Water",

        (
            f"{surface:,.0f} m²"
            if isinstance(surface, (int, float))
            else "--"
        ),
    )

    c5.metric(

        "⛰ Mean Elevation",

        (
            f"{elevation:.1f} m"
            if isinstance(elevation, (int, float))
            else "--"
        ),
    )

    c6.metric(

        "📐 Mean Slope",

        (
            f"{slope:.2f} %"
            if isinstance(slope, (int, float))
            else "--"
        ),
    )