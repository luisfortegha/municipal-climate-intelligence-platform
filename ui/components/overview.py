import streamlit as st


def render_overview(
    findings,
    last_analysis,
    analysis_mode,
):

    st.markdown(
        """
        <div class="card-header">
        🏛 Municipal Operations Overview
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not findings:

        st.info(
            "Run an analysis to generate the municipal operations overview."
        )
        return

    study = findings.get(
        "study_area",
        {},
    )

    engineering = findings.get(
        "engineering_assessment",
        {},
    )

    flood = findings.get(
        "flood_assessment",
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

    performance = findings.get(
        "performance",
        {},
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Study Area",
            study.get(
                "name",
                "--",
            ),
        )

        st.metric(
            "Analysis Mode",
            analysis_mode,
        )

        st.metric(
            "Workflow",
            "Completed",
        )

    with c2:

        st.metric(
            "Flood Condition",
            flood.get(
                "overall_condition",
                "--",
            ),
        )

        st.metric(
            "Critical Assets",
            engineering.get(
                "critical_facilities",
                0,
            ),
        )

        st.metric(
            "Affected Assets",
            engineering.get(
                "affected_assets",
                0,
            ),
        )

    with c3:

        st.metric(
            "Affected Area",
            f"{hazard.get('percent_area_affected',0):.1f} %",
        )

        runtime = performance.get(
            "total",
            None,
        )

        st.metric(
            "Runtime",
            f"{runtime:.1f} s"
            if runtime is not None
            else "--",
        )

        if last_analysis:

            st.metric(
                "Last Analysis",
                last_analysis.strftime(
                    "%d %b %Y\n%H:%M",
                ),
            )

        else:

            st.metric(
                "Last Analysis",
                "--",
            )