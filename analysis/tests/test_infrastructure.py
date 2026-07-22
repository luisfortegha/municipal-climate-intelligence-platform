from analysis.environment import DEFAULT_STUDY_AREA
from analysis.hazard import (
    assess_hazard,
    HazardAssessment,
)


def test_hazard_layer_download():

    assessment, gdf = assess_hazard(
        DEFAULT_STUDY_AREA
    )

    assert isinstance(
        assessment,
        HazardAssessment,
    )

    assert gdf is not None

    assert not gdf.empty

    assert len(gdf) >= len(
        assessment.zones
    )


def test_hazard_assessment_fields():

    assessment, _ = assess_hazard(
        DEFAULT_STUDY_AREA
    )

    assert isinstance(
        assessment.intersects,
        bool,
    )

    assert isinstance(
        assessment.zones,
        list,
    )

    for zone in assessment.zones:

        assert zone.zone_id

        assert zone.area_name

        assert zone.hazard_level

        assert zone.geometry is not None