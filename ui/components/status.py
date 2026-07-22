import streamlit as st


def render_status():

    st.markdown(
        """
        <div class="card-header">
        🟢 System Status
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.success("Weather")

    c2.success("Hazard")

    c3.success("Infrastructure")

    c4.success("Gemini")

    c5.success("Registry")