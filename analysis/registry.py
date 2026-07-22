import os
import sqlite3
import json
import time
from typing import Dict, Any, List, Optional
from analysis.logger import logger
import csv
from pathlib import Path
from shapely.geometry import mapping
from shapely.geometry.base import BaseGeometry

class RegistryError(Exception):
    """Raised when report storage/retrieval operations fail."""
    pass

from shapely.geometry.base import BaseGeometry

def make_json_safe(obj):

    if isinstance(obj, BaseGeometry):
        return mapping(obj)

    if isinstance(obj, dict):
        return {
            k: make_json_safe(v)
            for k, v in obj.items()
        }

    if isinstance(obj, (list, tuple)):
        return [
            make_json_safe(v)
            for v in obj
        ]

    return obj

def _get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a connection to the SQLite database, creating directories if needed."""
    if db_path is None:
        db_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "reports.db")
        )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        # Enable foreign keys and set row factory for dict conversion
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        raise RegistryError(f"Database connection failure: {str(e)}")

def init_registry(db_path: Optional[str] = None) -> None:
    """Initializes the database schema if it does not already exist."""
    conn = _get_db_connection(db_path)
    try:
        logger.info("Initializing report registry.")
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    brief TEXT NOT NULL,
                    findings TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    human_decision TEXT NOT NULL,
                    reviewer_comments TEXT
                );
            """)
    except Exception as e:
        raise RegistryError(f"Failed to initialize registry schema: {str(e)}")
    finally:
        conn.close()

def save_report(
    brief: str,
    findings: Dict[str, Any],
    decision: str,
    reviewer_comments: str,
    db_path: Optional[str] = None
) -> int:
    """
    Saves an approved report into the registry SQLite database.
    
    Enforces constraints:
    - Only 'Approved' decisions are written to the database.
    """
    if decision.lower() != "approved":
        raise RegistryError("Only approved reports are allowed to be saved to the database registry.")
        
    init_registry(db_path)
    conn = _get_db_connection(db_path)
    
    evidence_structure = {

        "supporting_evidence": findings.get(
            "supporting_evidence",
            {},
        ),
    
        "environmental_assessment": findings.get(
            "environmental_assessment",
            {},
        ),
    
        "engineering_assessment": findings.get(
            "engineering_assessment",
            {},
        ),
    
        "flood_assessment": findings.get(
            "flood_assessment",
            {},
        ),

        "quality_assessment":
        findings.get(
            "quality_assessment",
            {},
        ),
    }

    timestamp = int(time.time())
    
    try:
        with conn:
            cursor = conn.cursor()
            logger.info("Saving approved report.")
            safe_findings = make_json_safe(findings)
            safe_evidence = make_json_safe(evidence_structure)
            cursor.execute(
                """
                INSERT INTO reports (timestamp, brief, findings, evidence, human_decision, reviewer_comments)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    timestamp,
                    brief,
                    json.dumps(safe_findings, indent=2),
                    json.dumps(safe_evidence, indent=2),
                    decision,
                    reviewer_comments
                )
            )
            row_id = cursor.lastrowid
            logger.info(f"Report {row_id} stored successfully.")
            return row_id
    except Exception as e:
        raise RegistryError(f"Database insertion failed: {str(e)}")
    finally:
        conn.close()

def retrieve_all_reports(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all reports chronologically from the registry."""
    init_registry(db_path)
    conn = _get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        logger.info("Retrieving report history.")
        cursor.execute("SELECT * FROM reports ORDER BY timestamp DESC;")
        rows = cursor.fetchall()
        logger.info(f"Retrieved {len(rows)} stored reports.")
        reports = []
        for row in rows:
            reports.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "brief": row["brief"],
                "findings": json.loads(row["findings"]),
                "evidence": json.loads(row["evidence"]),
                "human_decision": row["human_decision"],
                "reviewer_comments": row["reviewer_comments"]
            })
        return reports
    except Exception as e:
        raise RegistryError(f"Failed to query registry database: {str(e)}")
    finally:
        conn.close()

def registry_statistics(
    db_path: Optional[str] = None,
) -> Dict[str, Any]:

    reports = retrieve_all_reports(db_path)

    if not reports:
        return {
            "previous_events": 0,
            "recurring_assets": 0,
            "recurring_zones": 0,
            "average_rainfall": 0.0,
            "average_hazard_polygons": 0,
            "average_affected_assets": 0,
            "most_common_flood_condition": "--",
        }

    flood_conditions = {}
    asset_counter = {}
    zone_counter = {}
    rainfall = []
    hazard_counts = []
    affected_assets = []
    
    for report in reports:

        findings = report.get(
            "findings",
            {},
        )
    
        evidence = findings.get(
            "supporting_evidence",
            {},
        )
        
        flood = findings.get(
            "flood_assessment",
            {},
        )
    
        condition = flood.get(
            "overall_condition"
        )
    
        if condition:
    
            flood_conditions[condition] = (
                flood_conditions.get(condition, 0)
                + 1
            )
    
        weather = evidence.get(
            "weather",
            {},
        )
        
        environment = findings.get(
            "environmental_assessment",
            {},
        )
    
        engineering = findings.get(
            "engineering_assessment",
            {},
        )
    
        rain = environment.get(
            "observed_rainfall_mm"
        )
    
        if rain is None:
            rain = weather.get(
                "rainfall_mm"
            )
    
        if rain is not None:
            rainfall.append(rain)
    
        hazard_counts.append(
            engineering.get(
                "hazard_polygons",
                0,
            )
        )
    
        affected_assets.append(
            engineering.get(
                "affected_assets",
                0,
            )
        )
    
        for asset in findings.get(
            "affected_infrastructure",
            [],
        ):
    
            key = asset.get(
                "name",
                "Unknown",
            )
    
            asset_counter[key] = (
                asset_counter.get(key, 0)
                + 1
            )
    
        for zone in evidence.get(
            "hazard_zones_implicated",
            [],
        ):
    
            key = zone.get(
                "area_name",
                "Unknown",
            )
    
            zone_counter[key] = (
                zone_counter.get(key, 0)
                + 1
            )

    return {
        "most_common_flood_condition":
            max(
                flood_conditions,
                key=flood_conditions.get,
            ) if flood_conditions else "--",
        "previous_events": len(reports),
        "recurring_assets": recurring_assets,
        "recurring_zones": recurring_zones,
        "average_rainfall": average_rainfall,
        "average_hazard_polygons": average_hazard_polygons,
        "average_affected_assets": average_affected_assets,
    }

def export_reports_json(
    output_path: str = "exports/reports.json",
    db_path: str | None = None,
):

    reports = retrieve_all_reports(db_path)

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            reports,
            f,
            indent=2,
        )

    return output_path

def export_reports_csv(
    output_path: str = "exports/reports.csv",
    db_path: str | None = None,
):

    reports = retrieve_all_reports(db_path)

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "ID",
                "Timestamp",
                "Decision",
                "Study Area",
                "Forecast Rainfall",
                "Observed Rainfall",
                "Affected Assets",
                "Flood Condition",
            ]
        )

        for report in reports:

            findings = report.get(
                "findings",
                {},
            )

            engineering = findings.get(
                "engineering_assessment",
                {},
            )

            environment = findings.get(
                "environmental_assessment",
                {},
            )

            study = findings.get(
                "study_area",
                {},
            )

            writer.writerow(
                [
                    report["id"],
                    report["timestamp"],
                    report["human_decision"],
                    study.get("name"),
                    environment.get(
                        "forecast_rainfall_mm"
                    ),
                    environment.get(
                        "observed_rainfall_mm"
                    ),
                    engineering.get(
                        "affected_assets"
                    ),
                    findings.get(
                        "flood_assessment",
                        {}
                    ).get(
                        "overall_condition"
                    )
                ]
            )

    return output_path