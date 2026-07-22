# Municipal Climate Intelligence Platform

Municipal Climate Intelligence Platform is an open-source Human-in-the-Loop decision support system for municipal infrastructure and environmental assessment.

The platform combines weather observations, satellite Earth observation, terrain analysis, geospatial infrastructure data, deterministic engineering workflows, and AI-generated engineering summaries into a single operational dashboard.

Operational decisions remain the responsibility of authorized personnel.

The system is **not** a flood prediction model.

The system does **not** recommend emergency actions.

The AI summarizes engineering findings.

---

# Mission

Provide municipal emergency managers with evidence-based infrastructure intelligence through deterministic engineering analysis and AI-assisted communication.

---

# Architecture

```
Study Area

↓

OpenWeather

↓

NASA GPM

↓

Sentinel-2

↓

Copernicus DEM

↓

Environmental Assessment

↓

Flood Assessment

↓

OpenStreetMap Infrastructure

↓

Exposure Assessment

↓

Engineering Assessment

↓

Gemini Infrastructure Review Brief

↓

Human Review

↓

SQLite Registry
```

---

# Engineering Principles

## Deterministic Engineering

Engineering calculations are performed using Python.

Examples include:

- Rainfall assessment
- Surface water analysis
- Terrain assessment
- Infrastructure assessment
- Spatial analysis
- Exposure assessment

The LLM performs no engineering calculations.

---

## Human Authority

The AI never:

- predicts flooding
- recommends evacuations
- recommends emergency actions
- communicates with the public
- replaces municipal decision makers

Every report requires explicit human approval.

---

## Explainable AI

Every statement produced by Gemini originates from deterministic structured findings.

The AI only communicates engineering evidence.

---

# Features

- OpenWeather Forecast Integration
- Environmental Evidence Assessment
- OpenStreetMap Infrastructure
- GeoPandas Spatial Analysis
- Interactive GIS Dashboard
- Earth Observation Dashboard
- NASA GPM Integration (initial)
- Infrastructure Review Brief
- Human Review Workflow
- SQLite Report Registry
- Historical Operations Dashboard
- Sentinel-2 Surface Water Analysis
- Copernicus DEM Terrain Analysis
- Custom Study Area Analysis
- PDF Engineering Report Export

---

# Screenshots

## Operations Dashboard

![Operations Dashboard](docs/images/dashboard.png)

## Earth Observation Center

![Earth Observation](docs/images/earth_center.png)

## Infrastructure Review Brief

![Review Brief](docs/images/brief.png)

# Repository

```
municipal_climate_agent/

analysis/
earth_observation/
ui/
data/
tests/

app.py
requirements.txt
Dockerfile
```

---

# Technology Stack

- Python
- Streamlit
- GeoPandas
- Shapely
- OSMnx
- Folium
- OpenWeather API
- NASA GPM
- Google Gemini
- SQLite
- Docker
- Google Cloud Run

---

# Environment Variables

Create a `.env` file.

```
OPENWEATHER_API_KEY=

GEMINI_API_KEY=

GEMINI_MODEL=gemini-2.5-flash
```

---

# Local Development

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
streamlit run app.py
```

---

# Testing

Run the complete test suite

```bash
pytest
```

Run with coverage

```bash
pytest --cov=analysis
```

---

# Docker

Build

```bash
docker build -t municipal-climate-agent .
```

Run

```bash
docker run \
-p 8080:8080 \
--env-file .env \
municipal-climate-agent
```

---

# Google Cloud Run

Build

```bash
gcloud builds submit \
--tag gcr.io/PROJECT_ID/municipal-climate-agent
```

Deploy

```bash
gcloud run deploy municipal-climate-agent \
--image gcr.io/PROJECT_ID/municipal-climate-agent \
--platform managed \
--allow-unauthenticated \
--region us-central1 \
--set-env-vars OPENWEATHER_API_KEY=YOUR_KEY,GEMINI_API_KEY=YOUR_KEY
```

---

# Kaggle Submission

The submission demonstrates:

- Human-in-the-Loop AI
- Deterministic engineering analysis
- Interactive municipal GIS dashboard
- Infrastructure intelligence
- Explainable AI summaries
- Registry-backed review workflow
- Earth Observation integration

---

# Future Roadmap

- Additional municipalities
- Enhanced environmental evidence visualization
- Performance optimization
- Multi-event historical analysis
- Additional infrastructure categories
- Automated quality assurance tests
- Historical climate analytics
- Environmental indicators
- Asset filtering
- Interactive infrastructure selection
- Multi-event analytics

The Human-in-the-Loop architecture remains unchanged.

# License

This project is released under the MIT License.
See the LICENSE file for details.