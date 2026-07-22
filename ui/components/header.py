import streamlit as st


def render_header():

    municipality = "No Study Area"

    if st.session_state.get("findings"):

        municipality = (
            st.session_state.findings
            .get("study_area", {})
            .get("name", municipality)
        )

    analysis_time = "--"

    if st.session_state.get("last_analysis"):

        analysis_time = (
            st.session_state.last_analysis.strftime(
                "%d %b %Y • %H:%M"
            )
        )

    status = (
        "Analysis Complete"
        if st.session_state.get("findings")
        else "Awaiting Analysis"
    )

    st.markdown(
        f"""
<div style="margin-bottom:22px;">

<div class="title-text">
Municipal Climate Intelligence Platform
</div>

<div class="subtitle-text">

Deterministic Environmental Engineering Assessment • GIS • Earth Observation • Human Review

</div>

<div style="display:flex;justify-content:space-between;align-items:center;margin-top:18px;">

<div>

<b>Study Area:</b> {municipality}

</div>

<div>

<b>Status:</b> {status}

</div>

<div>

<b>Analysis:</b> {analysis_time}

</div>

</div>

</div>
""",
        unsafe_allow_html=True,
    )