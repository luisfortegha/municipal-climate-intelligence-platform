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

    flood = findings.get(
        "flood_assessment",
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

Environmental Evidence
"""
        )

    forecast = engineering.get("forecast_rainfall_mm")
    rainfall72 = engineering.get("accumulation_72h_mm")

    forecast_text = (
        f"{forecast:.1f} mm"
        if isinstance(forecast, (int, float))
        else "--"
    )

    rainfall72_text = (
        f"{rainfall72:.1f} mm"
        if isinstance(rainfall72, (int, float))
        else "--"
    )

    st.success(
        f"""
    Engineering Summary
    
    • Flood Condition: {flood.get("overall_condition", "--")}

    • Engineering Review Assets: {engineering.get("affected_assets", 0)}

    • Critical Facilities Reviewed: {engineering.get("critical_facilities", 0)}

    • Forecast Rainfall: {forecast_text}

    • 72-hour Rainfall: {rainfall72_text}
    """
    )