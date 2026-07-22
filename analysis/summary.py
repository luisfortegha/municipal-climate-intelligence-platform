import os
import json
from typing import Dict, Any
from google.genai.errors import ServerError
from google import genai
from dotenv import load_dotenv

load_dotenv()


class SummaryServiceError(Exception):
    """Raised when the summary generation fails."""
    pass


# Read Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise SummaryServiceError(
        "GEMINI_API_KEY environment variable is not configured."
    )

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_situation_brief(
    structured_findings: Dict[str, Any],
    api_key: str = None
) -> str:
    """
    Generates an explainable Infrastructure Review Brief using Google Gemini.

    Only structured engineering findings are sent to the model.

    No raw GIS geometries or raw API responses are included.
    """

    if not structured_findings:
        raise SummaryServiceError(
            "Structured findings are missing. Cannot generate brief."
        )

    # ------------------------------------------------------------------
    # Remove geometry before sending anything to the LLM
    # ------------------------------------------------------------------

    hazard_zones = (
        structured_findings.get(
            "supporting_evidence",
            {},
        ).get(
            "hazard_zones_implicated",
            [],
        )
    )
    
    hazard_summary = {

        "polygon_count": 0,
    
        "assessment_basis": "Environmental Evidence",

    }

    assets = structured_findings.get(
        "affected_infrastructure",
        []
    )
    
    infrastructure_summary = {
    
        "affected_assets": len(assets),
    
        "hospitals": 0,
    
        "schools": 0,
    
        "fire_stations": 0,
    
        "police": 0,
    
        "roads": 0,
    }
    
    for asset in assets:
    
        layer = asset.get(
            "osm_layer",
            "",
        )
    
        if layer == "hospitals":
            infrastructure_summary["hospitals"] += 1
    
        elif layer == "schools":
            infrastructure_summary["schools"] += 1
    
        elif layer == "fire_stations":
            infrastructure_summary["fire_stations"] += 1
    
        elif layer == "police":
            infrastructure_summary["police"] += 1
    
        elif layer == "primary_roads":
            infrastructure_summary["roads"] += 1


    study_area = structured_findings.get(
        "study_area",
        {},
    )

    filtered_findings = {
        "study_area": study_area,

        "flood_assessment":
        structured_findings.get(
            "flood_assessment",
            {},
        ),

        "engineering_assessment": structured_findings.get(
            "engineering_assessment",
            {}
        ),
        "exposure_assessment": structured_findings.get(
            "exposure_assessment",
            {}
        ),
        "hazard_metrics": structured_findings.get(
            "hazard_metrics",
            {},
        ),
        "environmental_assessment": structured_findings.get(
            "environmental_assessment",
            {},
        ),
        "infrastructure_summary": infrastructure_summary,
        "supporting_evidence": {
            "weather": structured_findings.get(
                "supporting_evidence", {}
            ).get("weather", {}),
            "engineering_basis": hazard_summary
        }
    }

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------

    prompt = f"""
You are an AI assistant supporting a Municipal Climate Intelligence Platform.

Your role is strictly limited to summarizing deterministic engineering findings.

You are NOT an emergency manager.

You MUST NOT:

• predict flooding

• estimate flood probability

• estimate infrastructure failure

• recommend emergency actions

• recommend evacuations

• recommend resource deployment

• infer consequences

• rank municipalities

• calculate engineering metrics

• invent facts

• communicate with the public

The engineering analysis has already been completed.

Python performed:

• weather processing
• GIS analysis
• hazard intersection
• infrastructure assessment

Your only task is to communicate those results clearly.

Write a concise Infrastructure Review Brief using exactly these sections.

# Executive Summary

Summarize the deterministic engineering and exposure findings.

Do not interpret the results.

Do not recommend actions.

# Study Area

Study Area

Report the municipality exactly as supplied in the structured findings.

Do not infer the municipality.

# Weather Conditions

Summarize the forecast precipitation, weather conditions and alerts.

# Flood Evidence

Report:

• Flood evidence areas

• Environmental review basis

• Surface water observations

• Rainfall observations

Only summarize the supplied findings.

# Infrastructure Exposure

Report:

• Infrastructure retrieved

• Infrastructure selected for engineering review

Group by category when possible.

Do not recommend actions.

# Engineering Assessment

Summarize:

• Forecast rainfall

• Weather alerts

• Environmental evidence basis

• Critical facilities

• Exposure ratio

Do not infer consequences.

# Environmental Assessment

Summarize the environmental observations exactly as supplied.

Include when available:

• Forecast rainfall

• Latest observed rainfall

• 24-hour accumulated rainfall

• 48-hour accumulated rainfall

• 72-hour accumulated rainfall

• Maximum precipitation interval

• Rainfall trend

• Surface water indicator

• Terrain

Do not calculate values.

Do not infer flooding.

Do not recommend actions.

# Sentinel-2 Observations

Include:

• NDWI

• Estimated Surface Water Area

• Acquisition Date (if available)

Do not infer flooding.

Only summarize supplied values.

# Flood Assessment

Summarize the deterministic flood assessment.

Include:

• Rainfall condition

• Surface water condition

• Terrain condition

• Flood hazard condition

• Overall environmental condition

• Supporting reasons

Do not predict flooding.

Do not recommend actions.

Only summarize supplied findings.

# Supporting Evidence

Summarize the deterministic evidence supporting the findings.

# Human Review Required

State that operational decisions remain the responsibility of authorized personnel.

Structured Findings

{json.dumps(filtered_findings, indent=2)}
"""

    try:
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.8,
        }
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=generation_config,
        )

        if (
            response is None
            or not hasattr(response, "text")
            or not response.text
        ):
            raise SummaryServiceError(
                "Gemini returned an empty response."
            )

        return response.text

    except ServerError:

        return """
    # Infrastructure Review Brief

    ## AI Summary Temporarily Unavailable
    
    Google Gemini is temporarily unavailable due to service demand.
    
    The deterministic engineering analysis completed successfully.
    
    Review the Engineering Assessment and Supporting Evidence sections below.
    
    Human review is still required before any operational decision.
    """
    
    except Exception as e:
    
        raise SummaryServiceError(
            f"Failed to generate Situation Brief: {str(e)}"
        )