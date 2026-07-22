import tempfile

from analysis.registry import (
    save_report,
    retrieve_all_reports,
    registry_statistics,
)


def test_registry_workflow():

    with tempfile.NamedTemporaryFile(suffix=".db") as db:

        findings = {
            "affected_infrastructure": [
                {
                    "name": "Central High School",
                    "type": "School",
                    "intersecting_zone_name": "AE Zone",
                    "hazard_level": "AE",
                },
                {
                    "name": "General Hospital",
                    "type": "Hospital",
                    "intersecting_zone_name": "AE Zone",
                    "hazard_level": "AE",
                },
            ],
            "supporting_evidence": {
                "weather": {
                    "timestamp": 0,
                    "rainfall_mm": 18.5,
                    "condition": "Rain",
                    "temperature_c": 24.0,
                    "active_alerts": [],
                },
                "hazard_zones_implicated": [
                    {
                        "zone_id": "1",
                        "area_name": "AE Zone",
                        "hazard_level": "AE",
                    }
                ],
            },
            "confidence": "High",
        }

        row_id = save_report(
            brief="Test infrastructure review.",
            findings=findings,
            decision="Approved",
            reviewer_comments="Automated test.",
            db_path=db.name,
        )

        assert row_id == 1

        reports = retrieve_all_reports(
            db_path=db.name,
        )

        assert len(reports) == 1

        stats = registry_statistics(
            db_path=db.name,
        )

        assert stats["previous_events"] == 1
        assert stats["average_rainfall"] == 18.5
        assert stats["average_confidence"] == "High"