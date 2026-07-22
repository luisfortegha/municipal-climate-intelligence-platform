import streamlit as st


def render_analysis_area(study_area, selection_mode):

    st.markdown(
        """
        <div class="card-header">
        📍 Active Analysis
        </div>
        """,
        unsafe_allow_html=True,
    )

    lat, lon = study_area.center

    display_name = (
        study_area.name
        if len(study_area.name) <= 28
        else study_area.name[:25] + "..."
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="Mode",
        value=selection_mode,
    )

    c2.metric(
        label="Study Area",
        value=display_name,
    )

    c3.metric(
        label="Center",
        value=f"{lat:.3f}, {lon:.3f}",
    )