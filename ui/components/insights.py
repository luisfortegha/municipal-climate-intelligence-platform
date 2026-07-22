import streamlit as st


def render_insights(findings):

    st.markdown(
        """
        <div class="card-header">
        🤖 AI Engineering Highlights
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not findings:

        st.info(
            "Run an analysis."
        )

        return

    engineering = findings.get(
        "engineering_assessment",
        {},
    )

    assets = findings.get(
        "affected_infrastructure",
        [],
    )

    if assets:

        top = assets[0]

        st.info(
            f"""
### Primary Infrastructure Review

**Asset**

{top["name"]}

**Category**

{top["type"]}

**Review Basis**

Hydrology Proximity
"""
        )

    st.success(
        f"""
Engineering Summary

• Review Assets: {engineering.get("affected_assets", 0)}

• Critical Facilities: {engineering.get("critical_facilities", 0)}

• Forecast Rainfall: {engineering.get("forecast_rainfall_mm", "--"):.1f} mm

• 72-hour Rainfall: {engineering.get("accumulation_72h_mm", "--"):.1f} mm
"""
    )