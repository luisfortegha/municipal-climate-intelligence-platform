import os

from analysis.environment import DEFAULT_STUDY_AREA
from analysis.weather import get_forecast
from analysis.hazard import assess_hazard
from analysis.infrastructure import (
    retrieve_infrastructure,
    analyze_affected_infrastructure,
)
from analysis.summary import generate_situation_brief


def test_end_to_end_pipeline():

    study_area = DEFAULT_STUDY_AREA

    lat, lon = study_area.center

    weather = get_forecast(
        lat,
        lon,
        municipality=study_area.name,
        api_key=os.environ["OPENWEATHER_API_KEY"],
    )

    hazard, hazard_gdf = assess_hazard(
        study_area
    )

    assert hazard_gdf is not None
    assert not hazard_gdf.empty

    infrastructure = retrieve_infrastructure(
        study_area
    )

    assert isinstance(
        infrastructure,
        dict,
    )

    findings = analyze_affected_infrastructure(
        weather,
        hazard,
        infrastructure,
    )

    assert "affected_infrastructure" in findings
    assert "supporting_evidence" in findings
    assert "confidence" in findings

    brief = generate_situation_brief(
        findings,
        api_key=os.environ["GEMINI_API_KEY"],
    )

    assert isinstance(
        brief,
        str,
    )

    assert len(
        brief
    ) > 100