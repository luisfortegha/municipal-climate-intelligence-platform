\# Situation Brief Skill



\## Purpose



Generate an explainable Infrastructure Review Brief from structured engineering findings.



\## Responsibilities



\- Summarize engineering findings.

\- Organize information clearly.

\- Report confidence.

\- Cite supplied evidence.



\## Depends On



\- Infrastructure Analysis Skill



\## Inputs



Structured Findings JSON



\## Outputs



Infrastructure Review Brief



Sections



\- Summary

\- Weather

\- Infrastructure

\- Evidence

\- Confidence

\- Requires Human Review



\## Constraints



Never recommend actions.



Never invent facts.



Never infer missing information.



Use only supplied evidence.



\## Success Criteria



The generated report is factually consistent with the supplied findings.



\## Failure Behavior



If structured findings are missing:



\- Do not call the LLM.

\- Return an informative error.

