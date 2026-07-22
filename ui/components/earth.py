

import streamlit as st

def metric(value, suffix=""):

    if value is None:
        return "--"

    if value == "":
        return "--"

    try:
        value = float(value)

        if abs(value) >= 1:
            return f"{value:.1f}{suffix}"
        else:
            return f"{value:.3f}{suffix}"

    except (TypeError, ValueError):
        return f"{value}{suffix}"

def render_earth_dashboard(
    gpm=None,
    environment=None,
    sentinel=None,
    terrain=None,
):

    forecast = "--"

    observed = "--"
    
    difference = "--"
    
    acc24 = "--"
    
    acc48 = "--"
    
    acc72 = "--"
    
    maximum = "--"
    
    trend = "--"
    
    ndwi = "--"
    
    surface_water = "--"
    
    elevation = "--"
    
    slope = "--"

    if environment:

        if environment.forecast_rainfall_mm is not None:
            forecast = environment.forecast_rainfall_mm

        if environment.observed_rainfall_mm is not None:
            observed = environment.observed_rainfall_mm

        if environment.rainfall_difference_mm is not None:
            difference = environment.rainfall_difference_mm

        if environment.accumulation_24h_mm is not None:
            acc24 = environment.accumulation_24h_mm
        
        if environment.accumulation_48h_mm is not None:
            acc48 = environment.accumulation_48h_mm
        
        if environment.accumulation_72h_mm is not None:
            acc72 = environment.accumulation_72h_mm
        
        if environment.maximum_interval_mm is not None:
            maximum = environment.maximum_interval_mm
        
        if environment.precipitation_trend is not None:
            trend = environment.precipitation_trend
        
        if environment.ndwi is not None:
            ndwi = environment.ndwi

        if environment.surface_water_area_m2 is not None:
            surface_water = (
                f"{environment.surface_water_area_m2:.0f} m²"
            )

        if environment.mean_elevation_m is not None:
            elevation = (
                f"{environment.mean_elevation_m:.1f} m"
            )

        if environment.mean_slope_percent is not None:
            slope = (
                f"{environment.mean_slope_percent:.1f} %"
            )

    st.markdown("### 🌧 NASA GPM")

    c1, c2 = st.columns(2)

    with c1:
    
        st.metric(
            "Latest Rainfall",
            (
                f"{observed} mm"
                if observed != "--"
                else "--"
            ),
        )
    
        st.metric(
            "24 h",
            (
                f"{acc24} mm"
                if acc24 != "--"
                else "--"
            ),
        )
    
        st.metric(
            "48 h",
            (
                f"{acc48} mm"
                if acc48 != "--"
                else "--"
            ),
        )
    
        st.metric(
            "72 h",
            (
                f"{acc72} mm"
                if acc72 != "--"
                else "--"
            ),
        )
    
    with c2:
    
        st.metric(
            "Maximum",
            (
                f"{maximum} mm"
                if maximum != "--"
                    else "--"
            ),
        )
    
        st.metric(
            "Trend",
            trend,
        )
    
        st.metric(
            "Status",
            sentinel.status
            if sentinel
            else "--",
        )

        st.metric(
            "Source",
            gpm.source
            if gpm
            else "--",
        )
    
    st.divider()
    
    st.markdown("### 🌿 Sentinel-2")
    
    c1, c2 = st.columns(2)
    
    with c1:
    
        st.metric(
            "NDWI",
            ndwi,
        )
    
        st.metric(
            "Surface Water",
            surface_water,
        )
    
    with c2:

        st.metric(
            "Acquisition",
            getattr(
                environment,
                "sentinel_acquisition_date",
                "--",
            ),
        )
    
        st.metric(
            "Status",
            sentinel.status
            if sentinel
            else "--",
        )

        st.metric(
            "Source",
            sentinel.source
            if sentinel
            else "Sentinel-2",
        )
    
    st.divider()
    
    st.markdown("### ⛰ Copernicus DEM")
    
    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Mean Elevation",
            elevation,
        )

        st.metric(
            "Elevation Range",
            (
                f"{environment.minimum_elevation_m:.1f}–"
                f"{environment.maximum_elevation_m:.1f} m"
                if (
                    getattr(environment, "minimum_elevation_m", None)
                    is not None
                )
                else "--"
            ),
        )

    with c2:

        st.metric(
            "Mean Slope",
            slope,
        )

        st.metric(
            "Status",
            terrain.status
            if terrain
            else "--",
        )

        st.metric(
            "Source",
            terrain.source
            if terrain
            else "Copernicus DEM",
        )