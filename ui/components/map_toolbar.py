import streamlit as st


def render_map_toolbar():

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "🎯 Study Area",
            use_container_width=True,
        ):
            st.session_state["map_reset"] = True

    with c2:

        if st.button(
            "🧹 Clear Selection",
            use_container_width=True,
        ):
            st.session_state.selected_asset = None

    with c3:

        st.button(
            "🗺 Layers",
            disabled=True,
            use_container_width=True,
        )