\# Flood Intelligence Orchestrator



\## Purpose



Coordinate the execution of all system skills to produce a review-ready Infrastructure Review Brief.



\## Responsibilities



Execute the workflow in the following order:



1\. Retrieve weather data.

2\. Load hazard layer.

3\. Retrieve infrastructure.

4\. Perform spatial analysis.

5\. Assemble structured findings.

6\. Generate the AI Situation Brief.

7\. Present the report for human review.

8\. Save the report only if approved.



\## Inputs



Municipality name or geographic coordinates.



\## Outputs



Infrastructure Review Brief.



\## Constraints



Never skip the Human Review step.



Never allow the AI to make operational decisions.



Never modify structured findings before they are reviewed.



\## Success Criteria



The complete workflow executes successfully and produces a review-ready report with all required evidence.

