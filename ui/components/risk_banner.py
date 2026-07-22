import streamlit as st


def render_risk_banner(findings):

    if not findings:
        return

    flood = findings.get(
        "flood_assessment",
        {},
    )

    engineering = findings.get(
        "engineering_assessment",
        {},
    )

    overall = flood.get(
        "overall_condition",
        "Unknown",
    )

    reasons = flood.get(
        "supporting_reasons",
        [],
    )

    assets = engineering.get(
        "affected_assets",
        0,
    )

    if "severe" in overall.lower():

        color = "#B91C1C"
        icon = "🔴"

    elif "high" in overall.lower():

        color = "#EA580C"
        icon = "🟠"

    elif "moderate" in overall.lower():

        color = "#CA8A04"
        icon = "🟡"

    elif (
        "low" in overall.lower()
        or "no" in overall.lower()
    ):

        color = "#15803D"
        icon = "🟢"

    else:

        color = "#2563EB"
        icon = "🔵"

    st.markdown(
        f"""
<div style="
padding:18px;
border-left:8px solid {color};
background:#111827;
border-radius:10px;
margin-bottom:20px;
">

<h3 style="margin:0;color:white;">
{icon} {overall}
</h3>

<p style="margin-top:10px;color:#D1D5DB;">
Affected infrastructure:
<b>{assets}</b>
</p>

</div>
""",
        unsafe_allow_html=True,
    )

    if reasons:

        with st.expander(
            "Supporting Engineering Evidence",
            expanded=False,
        ):

            for reason in reasons:

                st.write(
                    f"• {reason}"
                )