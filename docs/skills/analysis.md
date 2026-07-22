\# Infrastructure Analysis Skill



\## Purpose



Determine which critical infrastructure assets intersect hazard areas.



\## Responsibilities



\- Load OpenStreetMap infrastructure.

\- Filter critical assets.

\- Perform spatial intersection.

\- Produce structured findings.



\## Depends On



\- Weather Processing Skill

\- Hazard Assessment Skill



\## Inputs



\- HazardAssessment

\- Infrastructure layers



\## Outputs



InfrastructureFindings



Example



\- Schools affected

\- Hospitals affected

\- Road segments

\- Fire stations



\## Constraints



Only perform deterministic GIS analysis.



No AI reasoning.



\## Success Criteria



Every affected asset is returned with supporting geometry.



\## Failure Behavior



If infrastructure data cannot be retrieved:



\- Return an empty result with an error message.

\- Do not generate a report.

