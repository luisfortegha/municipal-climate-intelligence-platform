from dataclasses import dataclass


@dataclass
class SituationAssessment:

    study_area: dict

    environmental: dict

    hazards: dict

    exposure: dict

    engineering: dict


def build_situation_assessment(
    structured_findings,
):

    return SituationAssessment(

        study_area=structured_findings.get(
            "study_area",
            {},
        ),

        environmental=structured_findings.get(
            "environmental_assessment",
            {},
        ),

        hazards=structured_findings.get(
            "hazard_metrics",
            {},
        ),

        exposure=structured_findings.get(
            "exposure_assessment",
            {},
        ),

        engineering=structured_findings.get(
            "engineering_assessment",
            {},
        ),
    )