import datetime
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

def render_evidence(findings):

    st.markdown(
        """
        <div class="card-header">
        🔬 Engineering Assessment
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not findings:

        st.info(
            "Run an analysis first."
        )
        return

    evidence = findings.get(
        "supporting_evidence",
        {},
    )

    weather = evidence.get(
        "weather",
        {},
    )

    engineering = findings.get(
        "engineering_assessment",
        {},
    )

    exposure = findings.get(
        "exposure_assessment",
        {},
    )

    hazard = findings.get(
        "hazard_metrics",
        {},
    )

    flood = findings.get(
        "flood_assessment",
        {},
    )

    zones = evidence.get(
        "hazard_zones_implicated",
        [],
    )

    # --------------------------------------------------------
    # Weather
    # --------------------------------------------------------

    with st.expander(
        "🌦 Weather & Rainfall",
        expanded=True,
    ):

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Condition",
            weather.get(
                "condition",
                "--",
            ),
        )

        c2.metric(
            "Temperature",
            metric(
                weather.get(
                    "temperature_c",
                ),
                " °C",
            ),
        )

        c3.metric(
            "Forecast Rainfall",
            metric(
                weather.get(
                    "rainfall_mm",
                ),
                " mm",
            ),
        )

        c1.metric(
            "Observed",
            metric(
                engineering.get(
                    "observed_rainfall_mm",
                ),
                " mm",
            ),
        )

        c2.metric(
            "24 h",
            metric(
                engineering.get(
                    "accumulation_24h_mm",
                ),
                " mm",
            ),
        )

        c3.metric(
            "72 h",
            metric(
                engineering.get(
                    "accumulation_72h_mm",
                ),
                " mm",
            ),
        )

        timestamp = weather.get(
            "timestamp"
        )

        if timestamp:

            st.caption(
                "Observation: "
                + datetime.datetime.fromtimestamp(
                    timestamp
                ).strftime(
                    "%Y-%m-%d %H:%M"
                )
            )

    # --------------------------------------------------------
    # Earth Observation
    # --------------------------------------------------------

    with st.expander(
        "🛰 Earth Observation",
        expanded=True,
    ):

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "NDWI",
            metric(
                engineering.get(
                    "ndwi",
                )
            ),
        )

        c2.metric(
            "Surface Water",
            metric(
                engineering.get(
                    "surface_water_area_m2",
                ),
                " m²",
            ),
        )

        c3.metric(
            "Rainfall Trend",
            engineering.get(
                "precipitation_trend",
                "--",
            ),
        )

    # --------------------------------------------------------
    # Infrastructure
    # --------------------------------------------------------

    with st.expander(
        "🏗 Engineering Review",
        expanded=True,
    ):

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Engineering Review Assets",
            engineering.get(
                "affected_assets",
                0,
            ),
        )
        
        c2.metric(
            "Critical Facilities Reviewed",
            engineering.get(
                "critical_facilities",
                0,
            ),
        )
        
        c3.metric(
            "Infrastructure Retrieved",
            exposure.get(
                "total_assets",
                0,
            ),
        )

        c1.metric(
            "Hospitals",
            engineering.get(
                "hospitals",
                0,
            ),
        )

        c2.metric(
            "Schools",
            engineering.get(
                "schools",
                0,
            ),
        )

        c3.metric(
            "Fire Stations",
            engineering.get(
                "fire_stations",
                0,
            ),
        )

        c1.metric(
            "Police",
            engineering.get(
                "police",
                0,
            ),
        )

        c2.metric(
            "Roads",
            engineering.get(
                "roads",
                0,
            ),
        )

        c3.metric(
            "Critical Facility Ratio",
            metric(
                engineering.get(
                    "critical_facility_ratio",
                )
            ),
        )

    # --------------------------------------------------------
    # Environmental Evidence
    # --------------------------------------------------------

    with st.expander(
        "🌍 Environmental Evidence",
        expanded=True,
    ):

        c1, c2 = st.columns(2)

        c1.metric(
            "Study Area",
            metric(
                exposure.get(
                    "study_area_km2",
                ),
                " km²",
            ),
        )

        c2.metric(
            "Infrastructure Retrieved",
            exposure.get(
                "total_assets",
                0,
            ),
        )

        c1.metric(
            "Engineering Review Assets",
            engineering.get(
                "affected_assets",
                0,
            ),
        )

        c2.metric(
            "Critical Facilities Reviewed",
            engineering.get(
                "critical_facilities",
                0,
            ),
        )

        c1.metric(
            "72 h Rainfall",
            metric(
                engineering.get(
                    "accumulation_72h_mm",
                ),
                " mm",
            ),
        )

        c2.metric(
            "Surface Water",
            metric(
                engineering.get(
                    "surface_water_area_m2",
                ),
                " m²",
            ),
        )

        c1.metric(
            "NDWI",
            metric(
                engineering.get(
                    "ndwi",
                ),
            ),
        )

        c2.metric(
            "Assessment",
            flood.get(
                "overall_condition",
                "--",
            ),
        )

    # --------------------------------------------------------
    # Flood Assessment
    # --------------------------------------------------------

    with st.expander(
        "⚠ Flood Assessment",
        expanded=True,
    ):

        if flood:

            c1, c2 = st.columns(2)

            c2.metric(
                "Rainfall",
                flood.get(
                    "rainfall_condition",
                    "--",
                ),
            )

            c1.metric(
                "Surface Water",
                flood.get(
                    "surface_water_condition",
                    "--",
                ),
            )

            c2.metric(
                "Terrain",
                flood.get(
                    "terrain_condition",
                    "--",
                ),
            )

            st.metric(
                "Flood Hazard",
                flood.get(
                    "flood_zone_condition",
                    "--",
                ),
            )

            reasons = flood.get(
                "supporting_reasons",
                [],
            )

            if reasons:

                st.markdown(
                    "**Supporting Reasons**"
                )

                for reason in reasons:

                    st.write(
                        f"• {reason}"
                    )

        else:

            st.info(
                "Flood assessment unavailable."
            )

    # --------------------------------------------------------
    # Flood Evidence
    # --------------------------------------------------------

    with st.expander(
        "🌊 Flood Evidence",
        expanded=False,
    ):

        st.success(
            "Engineering review is performed using multiple environmental evidence sources rather than regulatory flood polygons.\n\n"
            "Evidence includes observed and forecast rainfall, surface water detection (NDWI), terrain analysis, proximity to waterways, and municipal infrastructure."
        )