from io import BytesIO

import streamlit as st

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

def display(value):

    if value is None:
        return "Not available"

    if isinstance(value, float):

        if abs(value) >= 1:
            return f"{value:.1f}"

        return f"{value:.3f}"

    return value

def _table(title, data):

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            f"<b>{title}</b>",
            styles["Heading2"],
        )
    )

    rows = [["Field", "Value"]]

    for key, value in data.items():

        rows.append(
            [
                str(key).replace("_", " ").title(),
                str(display(value)),
            ]
        )

    table = Table(
        rows,
        colWidths=[180, 280],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ]
        )
    )

    elements.append(table)

    elements.append(Spacer(1, 16))

    return elements


def build_pdf(
    findings,
    brief,
    review_status,
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Municipal Climate Intelligence Platform",
            styles["Title"],
        )
    )

    story.append(
        Spacer(
            1,
            24,
        )
    )

    sections = [

        (
            "Study Area",
            findings.get(
                "study_area",
                {},
            ),
        ),

        (
            "Flood Assessment",
            findings.get(
                "flood_assessment",
                {},
            ),
        ),

        (
            "Infrastructure Inventory",
            findings.get(
                "summary",
                {},
            ),
        ),

        (
            "Exposure Assessment",
            findings.get(
                "exposure_assessment",
                {},
            ),
        ),

        (
            "Environmental Assessment",
            findings.get(
                "environmental_assessment",
                {},
            ),
        ),

        (
            "Engineering Assessment",
            findings.get(
                "engineering_assessment",
                {},
            ),
        ),

        (
            "Performance",
            findings.get(
                "performance",
                {},
            ),
        ),
    ]

    for title, data in sections:

        if data:

            story.extend(
                _table(
                    title,
                    data,
                )
            )

    story.append(
        Paragraph(
            "<b>AI Situation Brief</b>",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            brief.replace(
                "\n",
                "<br/>",
            ),
            styles["BodyText"],
        )
    )

    story.append(
        Spacer(
            1,
            20,
        )
    )

    flood = findings.get(
        "flood_assessment",
        {},
    )
    
    engineering = findings.get(
        "engineering_assessment",
        {},
    )
    
    exposure = findings.get(
        "exposure_assessment",
        {},
    )
    
    story.append(
        Paragraph(
            "<b>Executive Summary</b>",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            f"""
    <b>Flood Condition:</b> {display(flood.get("overall_condition"))}<br/>
    <b>Infrastructure Retrieved:</b> {display(exposure.get("total_assets"))}<br/>
    <b>Critical Facilities Reviewed:</b> {display(engineering.get("critical_facilities"))}
    """,
            styles["BodyText"],
        )
    )

    story.append(
        Spacer(
            1,
            18,
        )
    )

    story.append(
        Paragraph(
            "<b>Human Review</b>",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            review_status,
            styles["BodyText"],
        )
    )

    story.append(
        Spacer(
            1,
            24,
        )
    )

    story.append(
        Paragraph(
            "<font size=9 color='grey'>"
            "Municipal Climate Intelligence Platform is a Human-in-the-Loop "
            "engineering decision support platform. Flood assessments are "
            "derived from environmental evidence including rainfall, surface "
            "water detection, terrain analysis, waterway proximity, and "
            "municipal infrastructure. This report supports engineering "
            "review and does not replace professional judgment."
            "</font>",
            styles["BodyText"],
        )
    )

    doc.build(
        story,
    )

    buffer.seek(0)

    return buffer.getvalue()


def render_export(
    findings,
    brief,
    review_status,
):

    if not findings:

        return

    st.markdown(
        """
<div class="card-header">
📄 Report Actions
</div>
""",
        unsafe_allow_html=True,
    )

    pdf = build_pdf(
        findings,
        brief,
        review_status,
    )

    st.download_button(

        "📥 Export Engineering Report (PDF)",

        data=pdf,

        file_name="municipal_climate_report.pdf",

        mime="application/pdf",

        use_container_width=True,
    )