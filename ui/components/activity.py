import datetime
import streamlit as st


def render_activity():

    st.markdown(
        """
        <div class="card-header">
        ⚙ Workflow Status
        </div>
        """,
        unsafe_allow_html=True,
    )

    activity = st.session_state.get(
        "activity",
        [],
    )

    if not activity:

        st.info(
            "No workflow has been executed."
        )

        return

    st.success("Workflow Completed")

    st.caption(
        f"{len(activity)} workflow events recorded"
    )

    st.write("")

    for event in activity:

        if isinstance(
            event,
            dict,
        ):

            timestamp = event.get(
                "time",
                "--:--:--",
            )

            message = event.get(
                "message",
                "",
            )

        else:

            timestamp = datetime.datetime.now().strftime(
                "%H:%M:%S"
            )

            message = str(event)

        if "✓" in message:

            icon = "🟢"

        elif "warning" in message.lower():

            icon = "🟡"

        elif "error" in message.lower():

            icon = "🔴"

        else:

            icon = "⚪"

        left, right = st.columns(
            [1, 8],
        )

        with left:

            st.markdown(
                f"""
            <div style="
            font-size:22px;
            text-align:center;
            ">
            {icon}
            </div>
            """,
                unsafe_allow_html=True,
            )

        with right:

            st.markdown(
                f"**{timestamp}**"
            )

            st.caption(
                message.replace(
                    "✓ ",
                    "",
                )
            )

        st.divider()