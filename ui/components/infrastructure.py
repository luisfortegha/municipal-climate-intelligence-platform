import pandas as pd
import streamlit as st


def render_infrastructure(findings):

    st.markdown(
        """
        <div class="card-header">
        🏗 Infrastructure Inventory
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not findings:

        st.info(
            "Run an analysis to retrieve infrastructure."
        )
        return

    summary = findings.get(
        "summary",
        {},
    )

    affected = findings.get(
        "affected_infrastructure",
        [],
    )

    nearby = findings.get(
        "nearby_infrastructure",
        [],
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Infrastructure Retrieved",
        summary.get(
            "total_assets",
            0,
        ),
    )

    c2.metric(
        "Hospitals",
        summary.get(
            "hospitals",
            0,
        ),
    )

    c3.metric(
        "Schools",
        summary.get(
            "schools",
            0,
        ),
    )

    c4.metric(
        "Fire Stations",
        summary.get(
            "fire_stations",
            0,
        ),
    )

    st.caption(
        "Infrastructure inventory retrieved from OpenStreetMap for the selected study area. "
        "Engineering review assets are determined separately using environmental evidence."
    )

    with st.expander(
        "Infrastructure Summary",
        expanded=False,
    ):

        metrics = [
            ("Road Segments", summary.get("roads", 0)),
            ("Hospitals", summary.get("hospitals", 0)),
            ("Schools", summary.get("schools", 0)),
            ("Fire Stations", summary.get("fire_stations", 0)),
            ("Police", summary.get("police", 0)),
            ("Emergency Services", summary.get("emergency_services", 0)),
            ("City Halls", summary.get("city_halls", 0)),
            (
                "Water Assets",
                summary.get("water_treatment", 0)
                + summary.get("wastewater_treatment", 0)
                + summary.get("waterways", 0)
                + summary.get("water", 0),
            ),
            ("Power Substations", summary.get("power_substations", 0)),
            ("Public Works", summary.get("public_works", 0)),
        ]
    
        metrics = [
            (label, value)
            for label, value in metrics
            if value > 0
        ]
    
        metrics.sort(
            key=lambda x: x[1],
            reverse=True,
        )
    
        left, right = st.columns(2)
    
        for i, (label, value) in enumerate(metrics):
    
            if i % 2 == 0:
                left.metric(label, value)
            else:
                right.metric(label, value)

        

    # ---------------------------------------------------------
    # Affected Assets
    # ---------------------------------------------------------

    st.markdown(
        "#### 🔴 Infrastructure Selected for Engineering Review"
    )

    if not affected:

        st.success(
            "No infrastructure currently meets the engineering review criteria based on environmental evidence."
        )

    else:

        df = pd.DataFrame(
            affected,
        )

        df = df.rename(
            columns={
                "name": "Asset",
                "type": "Category",
                "intersecting_zone_name": "Hazard Zone",
                "hazard_level": "Flood Zone",
            }
        )

        columns = [
            "Asset",
            "Category",
            "Hazard Zone",
            "Flood Zone",
        ]

        existing = [
            c
            for c in columns
            if c in df.columns
        ]

        st.dataframe(
            df[existing],
            width="stretch",
            hide_index=True,
        )

    # ---------------------------------------------------------
    # Nearby Assets
    # ---------------------------------------------------------

    st.markdown("#### 🟡 Supporting Infrastructure Context")

    if nearby:

        nearby_df = pd.DataFrame(
            nearby,
        )

        nearby_df = nearby_df.rename(
            columns={
                "name": "Asset",
                "type": "Category",
                "distance_class": "Distance",
                "segments": "Segments",
            }
        )

        columns = [
            "Asset",
            "Category",
            "Distance",
            "Segments",
        ]

        existing = [
            c
            for c in columns
            if c in nearby_df.columns
        ]

        st.dataframe(
            nearby_df[existing],
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No nearby infrastructure within the configured buffer distances."
        )

    # ---------------------------------------------------------
    # Selected Asset
    # ---------------------------------------------------------

    selected = st.session_state.get(
        "selected_asset",
    )

    if selected:

        st.markdown("#### 📍 Selected Map Feature")

        st.json(
            selected,
            expanded=False,
        )