import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# BE THE CHANCELLOR
# LUBS2281 fiscal policy simulation game
#
# A simplified open-economy New Keynesian teaching simulator.
# This is not an official forecast, OBR model or Bank of England model.
# ============================================================

st.set_page_config(
    page_title="Be the Chancellor",
    page_icon="🏛️",
    layout="wide"
)

# ------------------------------------------------------------
# Custom dashboard styling
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .treasury-header {
        background: linear-gradient(135deg, #06162b 0%, #12355b 55%, #1f6f8b 100%);
        padding: 2.1rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 30px rgba(15,23,42,0.24);
    }

    .treasury-eyebrow {
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        color: #bfdbfe;
    }

    .treasury-title {
        font-size: 3.2rem;
        font-weight: 900;
        margin-top: 0.25rem;
        line-height: 1.05;
    }

    .treasury-subtitle {
        color: #dbeafe;
        font-size: 1.05rem;
        margin-top: 0.65rem;
        max-width: 980px;
    }

    .dashboard-card {
        background: white;
        padding: 1.15rem 1.2rem;
        border-radius: 20px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 18px rgba(15,23,42,0.08);
        min-height: 138px;
    }

    .kpi-label {
        font-size: 0.76rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 900;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }

    .kpi-note {
        font-size: 0.84rem;
        color: #64748b;
        line-height: 1.3;
    }

    .scenario-panel {
        background: #f8fafc;
        padding: 1rem 1.15rem;
        border-radius: 18px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }

    .event-card {
        background: linear-gradient(135deg, #111827 0%, #1e293b 100%);
        color: white;
        padding: 1.25rem 1.35rem;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(15,23,42,0.22);
        margin-bottom: 1rem;
    }

    .event-title {
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .event-text {
        color: #cbd5e1;
        font-size: 0.94rem;
        line-height: 1.45;
    }

    .briefing-box {
        background: white;
        padding: 1.35rem 1.45rem;
        border-radius: 20px;
        border-left: 7px solid #1d4ed8;
        box-shadow: 0 5px 18px rgba(15,23,42,0.08);
        margin-bottom: 1rem;
    }

    .briefing-box h3 {
        margin-top: 0;
        color: #0f172a;
    }

    .briefing-box p {
        color: #334155;
        font-size: 0.96rem;
        line-height: 1.55;
    }

    .rule-pass {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }

    .rule-fail {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }

    .rule-warning {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }

    .small-muted {
        color: #64748b;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Baseline settings
# ------------------------------------------------------------

BASE = {
    "basic_income_tax": 20.0,
    "higher_income_tax": 40.0,
    "corporation_tax": 25.0,
    "personal_allowance": 12.57,
    "health": 100.0,
    "education": 100.0,
    "welfare": 100.0,
    "defence": 100.0,
    "infrastructure": 100.0,
}

SCENARIOS = {
    "Normal conditions": {
        "initial_growth": 1.4,
        "initial_inflation": 2.0,
        "initial_bank_rate": 4.5,
        "initial_employment": 75.0,
