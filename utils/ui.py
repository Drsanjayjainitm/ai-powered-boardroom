"""Competition presentation theme shared by Streamlit pages."""
import streamlit as st

CSS = """
<style>
:root { --navy:#10233f; --teal:#087e85; --muted:#61738b; }
.block-container {max-width: 1360px; padding-top: 1.15rem; padding-bottom: 3rem;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#edf5f8 0%,#f8fafc 100%);}
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {color:var(--navy);}
h1,h2,h3 {letter-spacing:-.025em;color:var(--navy);}
h1 {font-weight:800 !important;}
[data-testid="stMetric"] {background:#fff; border:1px solid #dfe8ef; padding:1.05rem;
 border-radius:16px; box-shadow:0 5px 18px rgba(18,38,68,.055); min-width:0; overflow-wrap:normal;}
[data-testid="stMetricLabel"] {color:#506780; font-size:.83rem;}
[data-testid="stMetricValue"] > div {white-space:nowrap;}
[data-testid="stMetricValue"] {color:#10233f;}
[data-testid="stAlert"] {border-radius:12px;}
[data-testid="stForm"] {background:#fbfdff;border:1px solid #dce8ee;border-radius:16px;padding:1rem;}
[data-testid="stExpander"] {border-radius:12px;}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
 background:linear-gradient(105deg,#087e85,#1459a5);border:0;border-radius:10px;
 box-shadow:0 4px 14px rgba(8,126,133,.18);font-weight:650;}
.stDownloadButton > button {border-radius:10px;}
.hero {background:linear-gradient(110deg,#10233f,#155b75);color:#fff;
 padding:1.4rem 1.65rem;border-radius:18px;margin:.15rem 0 1.1rem;}
.hero .eyebrow {color:#91e6df;font-size:.75rem;font-weight:750;letter-spacing:.13em;text-transform:uppercase;}
.hero h1 {color:white !important;margin:.3rem 0 .35rem;font-size:2rem;}
.hero p {color:#d8e7f2;margin:0;max-width:850px;line-height:1.6;}
.pill {display:inline-block;border:1px solid #bfdfe0;border-radius:30px;padding:.25rem .65rem;
 color:#086a70;background:#eefafa;font-size:.78rem;font-weight:700;}
/* Spacious, legible competition dashboard with robust narrow-screen behavior. */
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:16px;}
[data-testid="stHorizontalBlock"] {align-items:stretch;}
[data-testid="stDataFrame"] {max-width:100%;}
[data-testid="stMetricDelta"] {font-weight:600;}
[data-testid="stSidebarNav"] a {border-radius:9px;}
[data-testid="stSidebarNav"] a:hover {background:rgba(8,126,133,.09);}
[data-testid="stButton"] button {min-height:2.45rem;transition:box-shadow .15s ease, transform .15s ease;}
[data-testid="stButton"] button:hover {box-shadow:0 5px 18px rgba(18,38,68,.12);}
@media print { [data-testid="stSidebar"], header, footer, [data-testid="stToolbar"] {display:none!important;}
 .block-container {max-width:100%!important;padding:.4rem!important;}
 [data-testid="stHorizontalBlock"] {break-inside:avoid;}
 [data-testid="stMetric"] {box-shadow:none;break-inside:avoid;}
 .hero {print-color-adjust:exact;-webkit-print-color-adjust:exact;} }
@media(max-width:700px){.hero {padding:1.05rem}.hero h1{font-size:1.55rem}.block-container{padding-left:.85rem;padding-right:.85rem}}
</style>
"""

def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)

def hero(eyebrow, title, subtitle):
    # All arguments are fixed application strings, never user-provided HTML.
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>',
                unsafe_allow_html=True)
