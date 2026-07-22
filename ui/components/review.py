import streamlit as st


def render_review(
    has_brief: bool,
    review_status: str,
    review_message: str,
    review_message_type: str,
):

    st.markdown(
        """
        <div class="card-header">
        ✍ Engineering Review
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "All AI-generated engineering assessments require human review before archival."
    )

    status_icon = {
        "Awaiting Analysis": "🔵",
        "Pending Review": "🟡",
        "Approved": "🟢",
        "Needs Review": "🟠",
        "Rejected": "🔴",
    }.get(
        review_status,
        "⚪",
    )

    c1 = st.container()

    with c1:

        st.metric(
            label="Review Status",
            value=review_status,
        )

    reviewer_comments = st.text_area(
        "Reviewer Comments",
        placeholder=(
            "Document observations, engineering rationale, "
            "recommended follow-up actions, or approval notes..."
        ),
        height=140,
    )

    st.write("")

    c1, c2, c3 = st.columns(3)

    approve = c1.button(
        "🟢 Approve",
        disabled=not has_brief,
        use_container_width=True,
    )

    review = c2.button(
        "🟡 Needs Review",
        disabled=not has_brief,
        use_container_width=True,
    )

    reject = c3.button(
        "🔴 Reject",
        disabled=not has_brief,
        use_container_width=True,
    )

    if review_message:

        st.write("")

        if review_message_type == "success":

            st.success(
                review_message,
            )

        elif review_message_type == "warning":

            st.warning(
                review_message,
            )

        elif review_message_type == "error":

            st.error(
                review_message,
            )

        else:

            st.info(
                review_message,
            )

    return (
        approve,
        review,
        reject,
        reviewer_comments,
    )