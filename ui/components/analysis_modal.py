import streamlit as st

FACTS = [

# Weather
"OpenWeather provides real-time meteorological observations and weather alerts.",
"NASA GPM estimates global precipitation every 30 minutes.",

# Satellite
"Sentinel-2 imagery detects standing surface water using the NDWI index.",
"Copernicus DEM provides elevation and terrain information for flood interpretation.",

# GIS
"OpenStreetMap provides hospitals, schools, emergency services, roads and utilities.",
"Exposure analysis identifies infrastructure intersecting hazard zones.",

# Engineering
"Engineering Assessment combines rainfall, terrain, satellite imagery and infrastructure exposure.",
"The AI-generated Infrastructure Review Brief summarizes deterministic engineering findings.",
"Approved engineering reports are archived into the municipal registry."

]
@st.dialog("🏛 Municipal Climate Intelligence")
def show_analysis_brief():

    if not st.session_state.analysis_started:

        st.markdown(
            """
        <h2 style="
        color:#0F172A;
        font-size:32px;
        margin-bottom:12px;
        ">
        Preparing Municipal Climate Analysis
        </h2>
        """,
            unsafe_allow_html=True,
        )
    
        st.markdown(
        """
        <div style="
        color:#334155;
        font-size:17px;
        line-height:1.7;
        ">
    
        The platform will integrate weather observations, Earth observation imagery, terrain analysis, GIS infrastructure, and deterministic engineering assessment to generate a municipal climate intelligence report.
    
        </div>
        """,
        unsafe_allow_html=True,
        )
    
        st.markdown(
        """
        <div style="
        background:#DBEAFE;
        border-left:6px solid #2563EB;
        padding:18px;
        border-radius:10px;
        color:#1E3A8A;
        font-size:16px;
        line-height:1.6;
        ">
    
        📍
        <b>When the analysis finishes</b>
        
        Double-click the Municipal Operations Map
        to refresh the newest GIS layers.
    
        </div>
        """,
        unsafe_allow_html=True,
        )
    
        st.markdown("---")
    
        import random
    
        facts = random.sample(FACTS, k=min(3, len(FACTS)))
    
        st.markdown(
            f"""
        <div class="did-you-know">
        
        <div class="did-you-know-title">
        💡 Did You Know?
        </div>
        
        <div class="did-you-know-body">
    
        <ul>
            <li>{facts[0]}</li>
            <li>{facts[1]}</li>
            <li>{facts[2]}</li>
        </ul>
    
        </div>
        
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🚨 Start Municipal Analysis",
            type="primary",
            use_container_width=True,
        ):
    
            st.session_state.run_analysis = True
            st.rerun()

    else:

        render_analysis_modal()

        if not st.session_state.analysis_ready:
            st.session_state.analysis_ready = True
            st.rerun()
    
def render_analysis_modal(step: int):

    st.markdown(
        """
<div class="analysis-modal">

<h2>🏛 Municipal Climate Intelligence Platform</h2>

<h3>Analysis in Progress</h3>

<p>
The platform is integrating weather observations,
Earth observation imagery,
GIS infrastructure,
and engineering analysis
to generate the municipal assessment.
</p>

<hr>

<p>
<b>
📍 Once the analysis finishes,
double-click the Municipal Operations Map
to refresh and display the latest GIS layers.
</b>
</p>

<hr>

<h4>Did You Know?</h4>

</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
    """
    <div class="progress-bar">
    
    <div class="progress-fill"></div>
    
    </div>
    """,
    unsafe_allow_html=True,
    )

    st.info("🌧 Collecting weather observations...")

    st.info("🛰 Processing Earth observation imagery...")

    st.info("🏗 Running engineering assessment...")