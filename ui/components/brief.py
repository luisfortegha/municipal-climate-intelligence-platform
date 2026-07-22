import streamlit as st

def split_sections(text: str):

    sections = []

    title = None
    content = []

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):

            if title is not None:

                sections.append(
                    (
                        title,
                        "\n".join(content).strip(),
                    )
                )

            title = line.lstrip("#").strip()
            content = []

        else:

            content.append(line)

    if title is not None:

        sections.append(
            (
                title,
                "\n".join(content).strip(),
            )
        )

    return sections

def render_brief(brief: str):

    selected = st.session_state.get(
        "selected_asset"
    )

    st.markdown(
        """
    <div class="brief-card">
    
    <div class="brief-title">
    📄 Infrastructure Review Brief
    </div>

    <div class="brief-description">
    AI-generated engineering summary based on deterministic
    environmental observations, GIS analysis and infrastructure
    assessment.
    </div>

    </div>
    """,
        unsafe_allow_html=True,
    )

    if selected:

        st.info(
            "Focused on selected infrastructure."
        )

    if not brief:

        st.info(
            "Run an analysis to generate the engineering brief."
        )

        return

    sections = split_sections(
        brief,
    )

    # Remove empty sections
    sections = [
        (title, body)
        for title, body in sections
        if body.strip()
    ]
    
    for title, body in sections:
    
        with st.expander(
            title,
            expanded=(
                title == "Executive Summary"
            ),
        ):
    
            st.markdown(body)