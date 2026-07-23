import matplotlib.pyplot as plt
import streamlit as st


def render_analytics(findings):

    st.markdown(
        """
        <div class="card-header">
        📈 Environmental Analytics
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not findings:

        st.info(
            "Run an analysis to generate analytics."
        )
        return

    environment = findings.get(
        "environmental_assessment",
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

    # ----------------------------------------------------------
    # Rainfall Timeline
    # ----------------------------------------------------------

    st.markdown("#### 🌧 Rainfall Timeline")

    rainfall = [

        environment.get(
            "forecast_rainfall_mm",
            0,
        ),

        environment.get(
            "observed_rainfall_mm",
            0,
        ),

        environment.get(
            "accumulation_24h_mm",
            0,
        ),

        environment.get(
            "accumulation_48h_mm",
            0,
        ),

        environment.get(
            "accumulation_72h_mm",
            0,
        ),
    ]

    labels = [
        "Forecast",
        "Observed",
        "24 h",
        "48 h",
        "72 h",
    ]

    fig, ax = plt.subplots(
        figsize=(8, 3),
    )

    ax.plot(
        labels,
        rainfall,
        marker="o",
        linewidth=2,
    )

    ax.set_ylabel(
        "Rainfall (mm)",
    )

    ax.grid(
        alpha=0.3,
    )

    st.pyplot(
        fig,
        clear_figure=True,
    )

    # ----------------------------------------------------------
    # Infrastructure Exposure
    # ----------------------------------------------------------

    st.markdown("#### 🏗 Engineering Review Summary")

    categories = [
        "Hospitals",
        "Schools",
        "Fire",
        "Police",
        "Roads",
    ]

    values = [

        engineering.get(
            "hospitals",
            0,
        ),

        engineering.get(
            "schools",
            0,
        ),

        engineering.get(
            "fire_stations",
            0,
        ),

        engineering.get(
            "police",
            0,
        ),

        engineering.get(
            "roads",
            0,
        ),
    ]

    fig, ax = plt.subplots(
        figsize=(8, 3),
    )

    ax.bar(
        categories,
        values,
    )

    ax.set_ylabel(
        "Engineering Review Assets",
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    st.pyplot(
        fig,
        clear_figure=True,
    )

    # ----------------------------------------------------------
    # Hazard Footprint
    # ----------------------------------------------------------

    st.markdown("#### 🌊 Hazard Footprint")

    municipality = hazard.get(
        "municipality_area_km2",
        0,
    )

    affected = hazard.get(
        "hazard_area_km2",
        0,
    )

    fig, ax = plt.subplots(
        figsize=(4, 4),
    )

    ax.pie(
        [
            max(municipality - affected, 0),
            affected,
        ],
        labels=[
            "Unaffected",
            "Hazard",
        ],
        autopct="%1.1f%%",
        startangle=90,
    )

    ax.set_title(
        "Municipal Area",
    )

    st.pyplot(
        fig,
        clear_figure=True,
    )

    # ----------------------------------------------------------
    # Exposure Summary
    # ----------------------------------------------------------

    st.markdown("#### 📊 Exposure Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Assets Inside",
        exposure.get(
            "assets_inside",
            0,
        ),
    )

    c2.metric(
        "≤100 m",
        exposure.get(
            "assets_within_100m",
            0,
        ),
    )

    c3.metric(
        "≤250 m",
        exposure.get(
            "assets_within_250m",
            0,
        ),
    )

    c1.metric(
        "Hazard Polygons",
        hazard.get(
            "polygon_count",
            0,
        ),
    )

    c2.metric(
        "FEMA Zones",
        hazard.get(
            "unique_fema_zones",
            0,
        ),
    )

    c3.metric(
        "Dominant Zone",
        hazard.get(
            "dominant_fema_zone",
            "--",
        ),
    )