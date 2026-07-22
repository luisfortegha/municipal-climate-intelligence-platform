import os

from analysis.summary import generate_situation_brief


def test_summary_generation():

    findings = {
        "affected_infrastructure": [
            {
                "id": "1",
                "name": "Central High School",
                "type": "School",
                "intersecting_zone_id": "101",
                "intersecting_zone_name": "AE Zone",
                "hazard_level": "AE",
            }
        ],
        "supporting_evidence": {
            "weather": {
                "timestamp": 0,
                "rainfall_mm": 12.5,
                "condition": "Rain",
                "temperature_c": 22.4,
                "active_alerts": [],
            },
            "hazard_zones_implicated": [
                {
                    "zone_id": "101",
                    "area_name": "AE Zone",
                    "hazard_level": "AE",
                }
            ],
        },
        "confidence": "Medium",
    }

    brief = generate_situation_brief(
        findings,
        api_key=os.environ["GEMINI_API_KEY"],
    )

    assert isinstance(brief, str)

    assert len(brief) > 100

    assert "Executive Summary" in brief

    assert "Human Review Required" in brief