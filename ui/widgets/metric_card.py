import streamlit as st


def metric_card(
    title,
    value,
    subtitle="",
    icon="📊",
):
    st.markdown(
        f"""
<div style="
background:white;
border-radius:14px;
padding:18px;
border:1px solid #E5E7EB;
box-shadow:0 2px 10px rgba(0,0,0,0.05);
height:145px;
">

<div style="
font-size:28px;
">
{icon}
</div>

<div style="
font-size:13px;
color:#6B7280;
margin-top:8px;
">
{title}
</div>

<div style="
font-size:30px;
font-weight:700;
margin-top:8px;
color:#111827;
">
{value}
</div>

<div style="
font-size:12px;
color:#9CA3AF;
margin-top:8px;
">
{subtitle}
</div>

</div>
""",
        unsafe_allow_html=True,
    )