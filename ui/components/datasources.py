import datetime
import streamlit as st


def _status_icon(status):

    status = (status or "").lower()

    if "operational" in status:
        return "🟢"

    if "cached" in status:
        return "🟡"

    if "unavailable" in status:
        return "🔴"

    return "⚪"


def _format_timestamp(value):

    if value is None:
        return "--"

    if isinstance(value, (int, float)):

        try:

            return datetime.datetime.fromtimestamp(
                value
            ).strftime(
                "%Y-%m-%d %H:%M"
            )

        except Exception:

            return str(value)

    return str(value)


def render_data_sources(findings=None):

    with st.expander(
        "📡 System Status",
        expanded=False,
    ):

        if not findings:

            st.info(
                "Run an analysis to view data source status."
            )

            return

        sources = findings.get(
            "data_sources",
            [],
        )

        if not sources:

            st.info(
                "No data source information available."
            )

            return

        for source in sources:

            c1, c2 = st.columns(
                [4, 1],
            )

            with c1:

                st.markdown(
                    f"**{source['source']}**"
                )

                st.caption(
                    f"Last Update: {_format_timestamp(source['last_update'])}"
                )

            with c2:

                st.markdown(
                    f"### {_status_icon(source['status'])}"
                )

                st.caption(
                    source["status"]
                )

            st.divider()