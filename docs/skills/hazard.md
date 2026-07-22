\# Hazard Assessment Skill



\## Purpose



Identify whether forecasted weather overlaps with known flood-prone areas.



\## Responsibilities



\- Load static hazard layers.

\- Validate geometries.

\- Compare weather location with hazard polygons.

\- Identify areas requiring review.



\## Inputs



\- ForecastData

\- Hazard GeoJSON



\## Outputs



HazardAssessment



Example:



\- Hazard zone

\- Area name

\- Hazard level

\- Geometry



\## Constraints



\- Do not predict flooding.

\- Only identify known hazard areas.



\## Success Criteria



Returns all hazard zones relevant to the current weather event.



\## Failure Behavior



If the hazard layer cannot be loaded:



\- Return an error status.

\- Stop spatial analysis.

\- Notify the orchestrator.

