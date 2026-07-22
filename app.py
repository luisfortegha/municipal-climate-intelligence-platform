import streamlit as st
import os
import datetime
import traceback

# Analysis Imports
from analysis.logger import logger
from analysis.environment import (
    STUDY_AREAS,
    StudyArea,
)
from analysis.situation import (
    build_situation_assessment,
)
from analysis.flood import compute_flood_assessment
from analysis.quality import (
    build_quality_assessment,
)
from analysis.data_sources import (
    build_data_sources,
)
from analysis.weather import get_forecast, WeatherServiceError
from analysis.hazard import assess_hazard, HazardServiceError
from analysis.infrastructure import retrieve_infrastructure, analyze_affected_infrastructure, InfrastructureRetrievalError
from analysis.exposure import (
    compute_exposure_assessment,
)
from analysis.hazard_metrics import (
    compute_hazard_metrics,
)
from analysis.summary import generate_situation_brief, SummaryServiceError
from analysis.registry import (
    save_report,
    retrieve_all_reports,
    registry_statistics,
    RegistryError,
)
from analysis.performance import (
    AnalysisTimer,
    Timer,
)
from analysis.environmental_assessment import (
    build_environmental_assessment,
)

# UI Components Import
from ui.components.header import render_header
from ui.components.metrics import render_metrics
from ui.components.status import render_status
from ui.components.datasources import render_data_sources
from ui.components.map import (
    render_map,
    hazard_style,
)
from ui.components.brief import render_brief
from ui.components.evidence import render_evidence
from ui.components.infrastructure import render_infrastructure
from ui.components.review import render_review
from ui.components.insights import render_insights
from ui.components.activity import render_activity
from ui.components.risk_banner import render_risk_banner
from ui.components.analysis_area import render_analysis_area
from ui.components.map_toolbar import render_map_toolbar
from ui.components.earth_center import render_earth_center
from ui.components.export import render_export
from ui.components.overview import render_overview
from ui.components.analysis_modal import (
    render_analysis_modal,
    show_analysis_brief,
)

# Earth Observations Import
from earth_observation.sentinel import (
    get_latest_observation as get_sentinel_observation,
)
from earth_observation.dem import (
    get_latest_observation as get_dem_observation,
)
from earth_observation.gpm import (
    get_precipitation_timeseries,
)

weather_key = os.environ.get("OPENWEATHER_API_KEY", "")
gemini_key = os.environ.get("GEMINI_API_KEY", "")


if not weather_key:
    st.error("OPENWEATHER_API_KEY not found in environment.")
    st.stop()

if not gemini_key:
    st.error("GEMINI_API_KEY not found in environment.")
    st.stop()


# Set up page config
st.set_page_config(
    page_title="Municipal Climate Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State variables
if "show_analysis_dialog" not in st.session_state:
    st.session_state.show_analysis_dialog = False
if "analysis_started" not in st.session_state:
    st.session_state.analysis_started = False
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False
if "brief" not in st.session_state:
    st.session_state.brief = ""
if "activity" not in st.session_state:
    st.session_state.activity = []
if "hazard_gdf" not in st.session_state:
    st.session_state.hazard_gdf = None
if "infra_gdfs" not in st.session_state:
    st.session_state.infra_gdfs = None
if "findings" not in st.session_state:
    st.session_state.findings = None
if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = None
if "status_message" not in st.session_state:
    st.session_state.status_message = ""
if "status_type" not in st.session_state:
    st.session_state.status_type = "info"
if "review_status" not in st.session_state:
    st.session_state.review_status = "Awaiting Analysis"
if "review_message" not in st.session_state:
    st.session_state.review_message = ""
if "review_message_type" not in st.session_state:
    st.session_state.review_message_type = "info"
if "map_instance" not in st.session_state:
    st.session_state.map_instance = 0
if "custom_study_area" not in st.session_state:
    st.session_state.custom_study_area = None

def refresh_map():
    st.session_state.map_instance += 1

def reset_analysis_state(clear_map=True):

    st.session_state.hazard_gdf = None
    st.session_state.infra_gdfs = None
    st.session_state.findings = None

    st.session_state.brief = ""
    st.session_state.activity = []

    st.session_state.selected_asset = None

    st.session_state.weather = None
    st.session_state.gpm = None
    st.session_state.sentinel = None
    st.session_state.terrain = None
    st.session_state.environment = None

    st.session_state.status_message = ""
    st.session_state.status_type = "info"

    st.session_state.review_status = "Awaiting Analysis"
    st.session_state.review_message = ""
    st.session_state.review_message_type = "info"

    if clear_map:

        st.session_state.custom_study_area = None

        st.session_state.pop("map_state", None)

        st.session_state.map_instance += 1

# Inject custom CSS for premium styling
from pathlib import Path

css = Path("ui/theme.css").read_text(encoding="utf-8")

st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True,
)

# Sidebar Inputs for Configuration
with st.sidebar:
    st.markdown(
        """
    # 🏛 Municipal Climate Intelligence
    
    ### Mission Control
    """
    )
    
    selection_mode = st.radio(
        "Study Area",
        [
            "Municipality",
            "Custom Area",
        ],
    )
    
    if "previous_mode" not in st.session_state:
        st.session_state.previous_mode = selection_mode
    
    if selection_mode != st.session_state.previous_mode:
    
        st.session_state.previous_mode = selection_mode
    
        reset_analysis_state()
    
    if selection_mode == "Municipality":

        selected = st.selectbox(
            "Municipality",
            list(STUDY_AREAS.keys()),
            key="municipality_selector",
            accept_new_options=False,
        )

        if "previous_municipality" not in st.session_state:
            st.session_state.previous_municipality = selected
        
        if selected != st.session_state.previous_municipality:
        
            st.session_state.previous_municipality = selected
        
            reset_analysis_state()
    
        study_area = STUDY_AREAS[selected]
            
    elif selection_mode == "Custom Area":

        if st.session_state.get("custom_study_area") is None:

            study_area = StudyArea.from_bbox(
                name="Draw Study Area",
                west=-87.07,
                south=35.90,
                east=-86.56,
                north=36.42,
            )

        else:

            study_area = st.session_state.custom_study_area

    st.divider()

    st.markdown(
        "### Current Operation"
    )

    st.markdown(f"""
    **Status**
    
    {st.session_state.review_status}
    
    **Mode**
    
    {selection_mode}
    
    **Study Area**
    
    {study_area.name}
    """)

    if st.session_state.get(
        "last_analysis"
    ):

        st.caption(
            "Last Analysis"
        )

        st.write(
            st.session_state.last_analysis.strftime(
                "%d %b %Y\n%H:%M"
            )
        )

    st.divider()

    st.markdown(
        "### Workflow"
    )
    
    workflow = [

        "Weather",
    
        "NASA GPM",
    
        "Sentinel-2",

        "Copernicus DEM",

        "Flood Evidence",

        "Infrastructure",

        "Exposure",
    
        "Engineering",

        "Gemini",

    ]

    completed = len(
        st.session_state.activity
    )

    for i, step in enumerate(
        workflow
    ):

        if completed > i:
            st.markdown(f"✅ {step}")
        elif completed == i:
            with st.spinner(step):
                pass
        else:
            st.markdown(f"⚪ {step}")

    st.divider()

    st.markdown("### Analysis Configuration")

    with st.expander("Developer Information", expanded=False):

        st.success("✓ OpenWeather configured")
        st.success("✓ Gemini configured")

        st.caption(
            "API credentials are loaded from environment variables."
        )

# Application Header
render_header()
render_metrics(
    st.session_state.findings,
    st.session_state.get("weather"),
    st.session_state.get("last_update"),
)
render_overview(
    st.session_state.findings,
    st.session_state.get("last_analysis"),
    selection_mode,
)
render_risk_banner(
    st.session_state.findings,
)

render_insights(
    st.session_state.findings
)

# Main Two-Column Layout
main = st.container()

with main:
    
    render_map_toolbar()
    
    render_analysis_area(
        study_area,
        selection_mode,
    )

    st.write("")
    
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    
    button_label = (
        "🚨 Analyze Municipality"
        if selection_mode == "Municipality"
        else "🚨 Analyze Custom Area"
    )
    
    analyze_enabled = (
        selection_mode == "Municipality"
        or st.session_state.custom_study_area is not None
    )

    analyze_clicked = st.button(
        button_label,
        type="primary",
        use_container_width=True,
        disabled=not analyze_enabled,
    )

    render_status()

    st.write("")


    map_title = (
        "🗺️ Municipal Operations Map"
        if selection_mode == "Municipality"
        else "🗺️ Interactive Study Area"
    )

    st.markdown(
        f'<div class="card-header">{map_title}</div>',
        unsafe_allow_html=True,
    )

    new_area = render_map(
        study_area,
        st.session_state.hazard_gdf,
        st.session_state.infra_gdfs,
        allow_rectangle=(
            selection_mode == "Custom Area"
        ),
        map_instance=st.session_state.map_instance,
    )

    if (
        selection_mode == "Custom Area"
        and new_area is not None
    ):

        if (
            st.session_state.custom_study_area is None
            or new_area.bounds != st.session_state.custom_study_area.bounds
        ):
            st.session_state.custom_study_area = new_area
            st.rerun()

    study_area = (
        st.session_state.custom_study_area
        if selection_mode == "Custom Area"
        and st.session_state.custom_study_area is not None
        else study_area
    )

    if (
        selection_mode == "Custom Area"
        and st.session_state.custom_study_area is not None
    ):
        st.success(
            "✅ Study area selected. Click **Analyze Custom Area** to begin."
        )

    if (
        selection_mode == "Custom Area"
        and st.session_state.findings is not None
    ):
        if st.button(
            "🗺️ Analyze Another Custom Area",
            use_container_width=True,
        ):
            reset_analysis_state()
            st.session_state.map_instance += 1
            st.rerun()

    map_state = st.session_state.get("map_state")

    if map_state:
    
        clicked = map_state.get("last_object_clicked")
    
        if clicked:

            st.session_state.selected_asset = clicked

    modal = st.empty()

    if analyze_clicked:

        show_analysis_brief()

    run_analysis = st.session_state.run_analysis

    if st.session_state.run_analysis:

        reset_analysis_state(clear_map=False)

        lat_val, lon_val = study_area.center

        st.session_state.run_analysis = False

        modal.container()

        with modal:

            render_analysis_modal(0)

        logger.info("Analysis requested by user.")

        performance = AnalysisTimer()

        overall_timer = Timer()

        with st.spinner(

            "Running Municipal Climate Intelligence workflow..."

        ):
            try:
                # Reset review state on new run
                st.session_state.review_status = "Pending Review"
                st.session_state.review_message = ""
                
                # 1. Weather processing
                st.info("Retrieving weather forecast...")
                logger.info("Retrieving weather forecast.")
                timer = Timer()
                forecast_data = get_forecast(
                    lat_val,
                    lon_val,
                    api_key=weather_key,
                    municipality=study_area.name,
                )
                st.session_state.weather = forecast_data
                performance.weather = timer.elapsed()
                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Weather Retrieved",
                    }
                )

                modal.empty()

                with modal:
                    render_analysis_modal(1)

                timer = Timer()
                gpm = get_precipitation_timeseries(
                    study_area,
                )

                st.session_state.gpm = gpm

                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ NASA GPM Retrieved",
                    }
                )

                modal.empty()

                with modal:
                    render_analysis_modal(2)

                performance.gpm = timer.elapsed()
                st.info("Loading Sentinel-2 observation...")
                logger.info("Loading Sentinel-2 observation.")
                timer = Timer()
                try:

                    sentinel = get_sentinel_observation(
                        study_area,
                    )
                
                except Exception as ex:
                
                    logger.warning(
                        f"Sentinel unavailable: {ex}"
                    )
                
                    sentinel = None

                st.session_state.sentinel = sentinel
                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Sentinel-2 Retrieved",
                    }
                )

                modal.empty()
                
                with modal:
                    render_analysis_modal(3)
                performance.sentinel = timer.elapsed()

                st.info("Loading Copernicus DEM...")
                logger.info("Loading Copernicus DEM.")
                timer = Timer()
                try:

                    terrain = get_dem_observation(
                        study_area,
                    )
                
                except Exception as ex:
                
                    logger.warning(
                        f"DEM unavailable: {ex}"
                    )

                    terrain = None

                st.session_state.terrain = terrain

                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Copernicus DEM Retrieved",
                    }
                )

                modal.empty()
                
                with modal:
                    render_analysis_modal(4)

                performance.terrain = timer.elapsed()

                environment = build_environmental_assessment(

                    forecast_data,
                
                    gpm,
                
                    sentinel,
                
                    terrain,
                
                )

                # 2. Hazard layer check
                st.info("Assessing flood evidence...")
                logger.info(
                    f"Loading hazard polygons for {study_area.name}."
                )
                timer = Timer()
                hazard_assessment, hazard_gdf = assess_hazard(
                    study_area
                )
                st.session_state.hazard_gdf = hazard_gdf
                refresh_map()
                performance.hazard = timer.elapsed()
                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Flood Evidence Completed",
                    }
                )

                modal.empty()

                with modal:
                    render_analysis_modal(5)

                # 3. Retrieve infrastructure across the study area
                st.info("Retrieving infrastructure...")
                logger.info(
                    f"Retrieving OpenStreetMap infrastructure for {study_area.name}."
                )
                timer = Timer()
                infra_gdfs = retrieve_infrastructure(
                    study_area,
                    hazard_gdf,
                )
                st.session_state.infra_gdfs = infra_gdfs
                refresh_map()
                performance.infrastructure = timer.elapsed()
                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Infrastructure Retrieved",
                    }
                )

                modal.empty()

                with modal:
                    render_analysis_modal(6)

                # 4. Perform spatial analysis / deterministic intersections
                st.info("Running spatial analysis...")
                logger.info("Running deterministic spatial analysis.")
                timer = Timer()
                structured_findings = analyze_affected_infrastructure(
                    environment,
                    st.session_state.infra_gdfs,
                )
                

                structured_findings[
                    "environmental_assessment"
                ] = environment.__dict__

                st.session_state.environment = environment
                
                structured_findings["data_sources"] = [
                    source.__dict__
                    for source in build_data_sources(
                        forecast_data,
                        gpm,
                        sentinel,
                        terrain,
                    )
                ]

                performance.spatial = timer.elapsed()
                situation = build_situation_assessment(
                    structured_findings
                )

                structured_findings[
                    "situation_assessment"
                ] = situation.__dict__
                
                structured_findings["study_area"] = {
                    "name": study_area.name,
                }

                structured_findings.setdefault(
                    "affected_infrastructure",
                    [],
                )
                
                structured_findings.setdefault(
                    "nearby_infrastructure",
                    [],
                )
                
                structured_findings.setdefault(
                    "summary",
                    {},
                )
                
                structured_findings.setdefault(
                    "engineering_assessment",
                    {},
                )
                
                structured_findings.setdefault(
                    "exposure_assessment",
                    {},
                )
                
                structured_findings.setdefault(
                    "hazard_metrics",
                    {},
                )
                exposure = compute_exposure_assessment(
                    study_area=study_area,
                    hazard_gdf=hazard_gdf,
                    infrastructure=st.session_state.infra_gdfs,
                )
                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Exposure Assessment Completed",
                    }
                )

                modal.empty()
                
                with modal:
                    render_analysis_modal(7)
                hazard_metrics = compute_hazard_metrics(
                    study_area,
                    hazard_gdf,
                )
                structured_findings["exposure_assessment"] = {

                    "study_area_km2":
                        exposure.study_area_km2,
                
                    "hazard_area_km2":
                        exposure.hazard_area_km2,
                
                    "percent_area_affected":
                        exposure.percent_area_affected,
                
                    "largest_hazard_polygon_km2":
                        exposure.largest_hazard_polygon_km2,
                
                    "assets_inside":
                        exposure.assets_inside,
                
                    "assets_within_100m":
                        exposure.assets_within_100m,
                
                    "assets_within_250m":
                        exposure.assets_within_250m,
                
                    "total_assets":
                        exposure.total_assets,
                }
                structured_findings["hazard_metrics"] = {

                    "polygon_count": len(hazard_assessment.zones),
                
                    "municipality_area_km2":
                        hazard_metrics.municipality_area_km2,
                
                    "hazard_area_km2":
                        hazard_metrics.total_hazard_area_km2,
                
                    "largest_polygon_km2":
                        hazard_metrics.largest_hazard_polygon_km2,
                
                    "percent_area_affected":
                        hazard_metrics.percent_area_affected,
                }

                flood = compute_flood_assessment(
                
                    structured_findings["environmental_assessment"],
                
                    structured_findings["hazard_metrics"],
                
                    structured_findings["exposure_assessment"],
                
                )
                
                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Engineering Assessment Completed",
                    }
                )

                modal.empty()

                with modal:
                    render_analysis_modal(8)

                structured_findings["flood_assessment"] = flood.__dict__


                st.session_state.findings = structured_findings
                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Spatial Analysis Completed",
                    }
                )

                modal.empty()

                with modal:
                    render_analysis_modal(7)

                # 5. Generate Situation Brief
                st.info("Generating Infrastructure Review Brief...")
                logger.info("Generating Infrastructure Review Brief.")
                timer = Timer()
                try:

                    brief = generate_situation_brief(
                        structured_findings,
                        api_key=gemini_key,
                    )
                
                except SummaryServiceError:
                
                    logger.warning(
                        "Gemini unavailable. Falling back to deterministic report."
                    )
                
                    brief = """
                # Infrastructure Review Brief
                
                AI summary unavailable.
                
                Deterministic engineering assessment completed successfully.
                
                Please review the Engineering Assessment and Supporting Evidence.
                """
                st.session_state.brief = brief
                performance.gemini = timer.elapsed()
                performance.total = overall_timer.elapsed()
                structured_findings["performance"] = performance.__dict__
                quality = build_quality_assessment(

                    weather=forecast_data,
                
                    gpm=gpm,
                
                    sentinel=sentinel,
                
                    terrain=terrain,
                
                    findings=structured_findings,
                                
                    brief=brief,

                )

                structured_findings[
                    "quality_assessment"
                ] = quality.__dict__

                st.session_state.last_analysis = datetime.datetime.now()
                st.session_state.last_update = st.session_state.last_analysis
                st.session_state.status_message = "Analysis workflow successfully executed!"
                st.session_state.status_type = "success"
                modal.empty()
                st.toast("Analysis complete!", icon="✅")
                st.session_state.activity.append(
                    {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "message": "✓ Situation Brief Generated",
                    }
                )               

                modal.empty()

                with modal:
                    render_analysis_modal(8)  

            except (WeatherServiceError, HazardServiceError, InfrastructureRetrievalError, SummaryServiceError) as e:
                logger.exception("Pipeline execution failed.")
                st.session_state.status_message = f"Pipeline execution failed: {str(e)}"
                st.session_state.status_type = "error"
                st.session_state.brief = ""
                st.session_state.findings = None
                st.session_state.review_status = "Awaiting Analysis"
            except Exception as e:
                st.exception(e)
                print(traceback.format_exc())
                st.session_state.status_message = f"An unexpected error occurred: {str(e)}"
                st.session_state.status_type = "error"
                st.session_state.brief = ""
                st.session_state.findings = None
                st.session_state.review_status = "Awaiting Analysis"

    # Status Notification
    if st.session_state.status_message:
        if st.session_state.status_type == "success":
            st.success(st.session_state.status_message)
        elif st.session_state.status_type == "error":
            st.error(st.session_state.status_message)

st.markdown("---")

render_infrastructure(
    st.session_state.findings,
)

st.write("")

render_evidence(
    st.session_state.findings,
)

st.write("")

render_activity()

st.markdown("---")

left, right = st.columns(
    [1.4, 1.0],
    gap="large",
)

with left:

    render_earth_center(
        study_area,
        st.session_state.get("gpm"),
        st.session_state.get("environment"),
        st.session_state.get("sentinel"),
        st.session_state.get("terrain"),
        st.session_state.hazard_gdf,
        st.session_state.infra_gdfs,
    )

with right:

    render_brief(
        st.session_state.brief,
    )

st.write("")

render_data_sources(
        st.session_state.findings,
    )

st.markdown("---")

# Bottom Section: Human Review Decision Panel
approve_clicked, needs_review_clicked, reject_clicked, reviewer_comments = render_review(
    has_brief=bool(st.session_state.brief),
    review_status=st.session_state.review_status,
    review_message=st.session_state.review_message,
    review_message_type=st.session_state.review_message_type,
)
        
if approve_clicked:
    logger.info("Approving Infrastructure Review Brief.")
    try:
        # Connect the sqlite registry saving logic
        row_id = save_report(
            st.session_state.brief,
            st.session_state.findings,
            "Approved",
            reviewer_comments
        )
        logger.info(f"Report {row_id} successfully stored.")
        st.session_state.review_status = "Approved"
        st.session_state.activity.append(
            {
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "message": "✓ Report Approved",
            }
        )
        st.session_state.review_message = f"Report #{row_id} has been Approved and successfully saved into the registry database."
        st.session_state.review_message_type = "success"
        st.success("Analysis completed.")
        logger.info("Pipeline completed successfully.")
        st.toast("Report Approved & Saved!", icon="🟢")
    except RegistryError as e:
        st.session_state.review_message = f"Failed to store approved report in registry: {str(e)} (The report remains available in memory)."
        st.session_state.review_message_type = "error"
            
elif needs_review_clicked:
    logger.info("Report marked as Needs Review.")
    st.session_state.review_status = "Needs Review"
    st.session_state.review_message = "Report status updated to 'Needs Review'. Draft changes kept in volatile memory."
    st.session_state.review_message_type = "warning"
    st.toast("Marked as Needs Review", icon="🟡")
        
elif reject_clicked:
    logger.info("Report rejected by reviewer.")
    st.session_state.review_status = "Rejected"
    st.session_state.review_message = "Report status updated to 'Rejected'. Report discarded."
    st.session_state.review_message_type = "error"
    st.toast("Report Rejected", icon="🔴")

render_export(
    st.session_state.findings,
    st.session_state.brief,
    st.session_state.review_status,
)

# Footer Disclaimer
st.markdown(
    '<div class="disclaimer">'
    'Municipal Climate Intelligence Platform is a Human-in-the-Loop AI decision support platform. It does not predict flood events, '
    'nor does it execute or recommend emergency response actions. All actions are subject to human command.'
    '</div>', 
    unsafe_allow_html=True
)
