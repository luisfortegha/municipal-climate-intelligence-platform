\# Weather Processing Skill



\## Purpose



Retrieve the latest weather forecast from OpenWeather and normalize the data for downstream analysis.



\## Responsibilities



\- Connect to the OpenWeather API.

\- Retrieve forecast data.

\- Extract precipitation and relevant weather variables.

\- Normalize the response into a standard format.

\- Handle API failures gracefully.



\## Inputs



\- Latitude

\- Longitude

\- OpenWeather API key



\## Outputs



ForecastData



Example:



\- Forecast timestamp

\- Rainfall forecast (mm)

\- Temperature

\- Weather condition

\- Alerts (if available)



\## Constraints



\- Never perform flood prediction.

\- Never interpret weather conditions.

\- Only provide normalized weather observations.



\## Success Criteria



A valid ForecastData object is returned or an informative error is produced.



\## Failure Behavior



If the weather service cannot be reached:



\- Return an error status.

\- Do not continue the workflow.

\- Notify the orchestrator.

