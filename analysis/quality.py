from dataclasses import dataclass


@dataclass
class QualityAssessment:

    weather: str

    gpm: str

    sentinel: str

    terrain: str

    hazard: str

    infrastructure: str

    environmental: str

    flood: str

    engineering: str

    gemini: str

    registry: str


def build_quality_assessment(
    weather,
    gpm,
    sentinel,
    terrain,
    findings,
    brief,
):

    return QualityAssessment(

        weather="OK" if weather else "Unavailable",

        gpm="OK" if gpm else "Unavailable",

        sentinel=(
            sentinel.status
            if sentinel
            else "Unavailable"
        ),

        terrain=(
            terrain.status
            if terrain
            else "Unavailable"
        ),

        hazard=(
            "OK"
            if findings.get("hazard_metrics")
            else "Unavailable"
        ),

        infrastructure=(
            "OK"
            if findings.get("summary")
            else "Unavailable"
        ),

        environmental=(
            "OK"
            if findings.get("environmental_assessment")
            else "Unavailable"
        ),

        flood=(
            "OK"
            if findings.get("flood_assessment")
            else "Unavailable"
        ),

        engineering=(
            "OK"
            if findings.get("engineering_assessment")
            else "Unavailable"
        ),

        gemini=(
            "OK"
            if brief
            else "Unavailable"
        ),

        registry="Pending",
    )