import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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
        font-size: 2.05rem;
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

    .risk-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }

    .risk-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }

    .risk-low {
        background-color: #dcfce7;
        color: #166534;
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
        "initial_exchange_rate": 100.0,
        "initial_output_gap": 0.0,
        "demand_sensitivity": 1.0,
        "inflation_sensitivity": 1.0,
        "monetary_sensitivity": 1.0,
        "fiscal_risk_sensitivity": 1.0,
        "description": "The economy begins close to potential. Inflation is at target and policy is broadly neutral."
    },
    "Recession": {
        "initial_growth": -0.4,
        "initial_inflation": 1.4,
        "initial_bank_rate": 3.5,
        "initial_employment": 73.5,
        "initial_exchange_rate": 98.0,
        "initial_output_gap": -1.8,
        "demand_sensitivity": 1.25,
        "inflation_sensitivity": 0.75,
        "monetary_sensitivity": 0.85,
        "fiscal_risk_sensitivity": 0.8,
        "description": "Weak demand and spare capacity mean fiscal expansion has a larger output effect and less immediate inflation pressure."
    },
    "High inflation": {
        "initial_growth": 0.8,
        "initial_inflation": 5.5,
        "initial_bank_rate": 5.25,
        "initial_employment": 74.7,
        "initial_exchange_rate": 99.0,
        "initial_output_gap": 0.3,
        "demand_sensitivity": 0.9,
        "inflation_sensitivity": 1.45,
        "monetary_sensitivity": 1.35,
        "fiscal_risk_sensitivity": 1.2,
        "description": "Inflation starts above target. Fiscal loosening risks provoking a stronger monetary policy response."
    },
    "Weak productivity": {
        "initial_growth": 0.6,
        "initial_inflation": 3.0,
        "initial_bank_rate": 4.75,
        "initial_employment": 74.8,
        "initial_exchange_rate": 97.5,
        "initial_output_gap": 0.2,
        "demand_sensitivity": 0.85,
        "inflation_sensitivity": 1.25,
        "monetary_sensitivity": 1.1,
        "fiscal_risk_sensitivity": 1.1,
        "description": "Low supply growth means demand stimulus quickly meets capacity constraints unless policy improves potential output."
    },
    "Fiscal credibility pressure": {
        "initial_growth": 0.9,
        "initial_inflation": 3.4,
        "initial_bank_rate": 5.0,
        "initial_employment": 74.5,
        "initial_exchange_rate": 94.0,
        "initial_output_gap": -0.3,
        "demand_sensitivity": 0.8,
        "inflation_sensitivity": 1.2,
        "monetary_sensitivity": 1.25,
        "fiscal_risk_sensitivity": 1.8,
        "description": "Markets are sensitive to unfunded fiscal loosening. Larger deficits weaken sterling and add to inflation pressure."
    },
}

EVENTS = {
    "No additional event": {
        "description": "No additional shock is applied after the Budget.",
        "demand_shock": 0.0,
        "inflation_shock": 0.0,
        "rate_shock": 0.0,
        "fx_shock": 0.0,
        "deficit_shock": 0.0,
        "supply_shock": 0.0
    },
    "Global energy price shock": {
        "description": "Energy prices rise sharply. Inflation increases, real incomes weaken and sterling comes under pressure.",
        "demand_shock": -0.25,
        "inflation_shock": 1.20,
        "rate_shock": 0.30,
        "fx_shock": -2.0,
        "deficit_shock": 0.25,
        "supply_shock": -0.10
    },
    "Gilt market pressure": {
        "description": "Investors become concerned about fiscal credibility. Sterling weakens and borrowing pressure rises.",
        "demand_shock": -0.15,
        "inflation_shock": 0.45,
        "rate_shock": 0.50,
        "fx_shock": -4.0,
        "deficit_shock": 0.60,
        "supply_shock": -0.05
    },
    "Global recession": {
        "description": "External demand weakens. Export growth slows and investment confidence falls.",
        "demand_shock": -0.80,
        "inflation_shock": -0.20,
        "rate_shock": -0.20,
        "fx_shock": -1.0,
        "deficit_shock": 0.35,
        "supply_shock": -0.05
    },
    "Positive productivity surprise": {
        "description": "Business investment and productivity improve faster than expected.",
        "demand_shock": 0.25,
        "inflation_shock": -0.35,
        "rate_shock": -0.10,
        "fx_shock": 1.5,
        "deficit_shock": -0.20,
        "supply_shock": 0.35
    },
    "NHS winter pressure": {
        "description": "Unexpected health pressures require emergency spending and reduce labour-market capacity.",
        "demand_shock": 0.15,
        "inflation_shock": 0.25,
        "rate_shock": 0.10,
        "fx_shock": -0.5,
        "deficit_shock": 0.45,
        "supply_shock": -0.15
    },
    "Sterling depreciation": {
        "description": "Sterling falls after a deterioration in external confidence, raising import-price inflation.",
        "demand_shock": -0.10,
        "inflation_shock": 0.70,
        "rate_shock": 0.20,
        "fx_shock": -5.0,
        "deficit_shock": 0.20,
        "supply_shock": -0.05
    }
}


# ------------------------------------------------------------
# Model functions
# ------------------------------------------------------------

def fiscal_demand_impulse(settings):
    """
    Positive values raise short-run aggregate demand.
    Negative values reduce short-run aggregate demand.
    """

    tax_drag = (
        0.035 * (settings["basic_income_tax"] - BASE["basic_income_tax"])
        + 0.018 * (settings["higher_income_tax"] - BASE["higher_income_tax"])
        + 0.028 * (settings["corporation_tax"] - BASE["corporation_tax"])
        - 0.100 * (settings["personal_allowance"] - BASE["personal_allowance"])
    )

    spending_push = (
        0.012 * (settings["health"] - BASE["health"])
        + 0.015 * (settings["education"] - BASE["education"])
        + 0.010 * (settings["welfare"] - BASE["welfare"])
        + 0.009 * (settings["defence"] - BASE["defence"])
        + 0.018 * (settings["infrastructure"] - BASE["infrastructure"])
    )

    return spending_push - tax_drag


def supply_impulse(settings):
    """
    Positive values raise potential output gradually.
    This is a stylised delayed supply-side effect.
    """

    return (
        0.004 * (settings["education"] - BASE["education"])
        + 0.003 * (settings["health"] - BASE["health"])
        + 0.007 * (settings["infrastructure"] - BASE["infrastructure"])
        - 0.003 * max(0, settings["corporation_tax"] - BASE["corporation_tax"])
    )


def deficit_impulse(settings):
    """
    Positive values indicate higher deficit pressure.
    This is a teaching indicator rather than a fiscal forecast.
    """

    revenue_gain = (
        0.18 * (settings["basic_income_tax"] - BASE["basic_income_tax"])
        + 0.08 * (settings["higher_income_tax"] - BASE["higher_income_tax"])
        + 0.12 * (settings["corporation_tax"] - BASE["corporation_tax"])
        - 0.50 * (settings["personal_allowance"] - BASE["personal_allowance"])
    )

    spending_increase = (
        0.20 * (settings["health"] - BASE["health"])
        + 0.16 * (settings["education"] - BASE["education"])
        + 0.18 * (settings["welfare"] - BASE["welfare"])
        + 0.14 * (settings["defence"] - BASE["defence"])
        + 0.13 * (settings["infrastructure"] - BASE["infrastructure"])
    )

    return spending_increase - revenue_gain


def classify_fiscal_stance(demand):
    if demand > 0.50:
        return "Expansionary"
    if demand < -0.50:
        return "Contractionary"
    return "Broadly neutral"


def classify_risk(value, low_cutoff, high_cutoff):
    if value >= high_cutoff:
        return "High", "risk-high"
    if value >= low_cutoff:
        return "Medium", "risk-medium"
    return "Low", "risk-low"


def simulate_economy(settings, scenario_name, event_name, quarters=12):
    scenario = SCENARIOS[scenario_name]
    event = EVENTS[event_name]

    demand = (
        fiscal_demand_impulse(settings) * scenario["demand_sensitivity"]
        + event["demand_shock"]
    )

    supply = supply_impulse(settings) + event["supply_shock"]

    deficit = (
        deficit_impulse(settings)
        + event["deficit_shock"]
    )

    output_gap = scenario["initial_output_gap"]
    inflation = scenario["initial_inflation"] + event["inflation_shock"]
    bank_rate = scenario["initial_bank_rate"] + event["rate_shock"]
    employment = scenario["initial_employment"]
    exchange_rate = scenario["initial_exchange_rate"] + event["fx_shock"]

    rows = []

    for t in range(quarters):
        year = 1 + t // 4
        quarter = 1 + t % 4
        period = f"Y{year} Q{quarter}"

        demand_decay = 0.78 ** t
        supply_build = supply * (1 - 0.80 ** (t + 1))

        # Output gap dynamics
        output_gap = (
            0.72 * output_gap
            + demand * demand_decay
            + 0.35 * supply_build
            - 0.10 * (bank_rate - scenario["initial_bank_rate"])
        )

        # Inflation dynamics
        inflation = (
            0.65 * inflation
            + 0.35 * 2.0
            + scenario["inflation_sensitivity"] * 0.28 * output_gap
            + scenario["fiscal_risk_sensitivity"] * 0.05 * deficit
            - 0.08 * supply_build
        )

        # Taylor-style monetary reaction function
        desired_rate = (
            4.0
            + scenario["monetary_sensitivity"] * 1.35 * (inflation - 2.0)
            + 0.35 * output_gap
        )

        bank_rate = 0.72 * bank_rate + 0.28 * desired_rate

        # Exchange-rate channel
        exchange_rate = (
            scenario["initial_exchange_rate"]
            + event["fx_shock"]
            + 1.7 * (bank_rate - scenario["initial_bank_rate"])
            - scenario["fiscal_risk_sensitivity"] * 0.32 * deficit
        )

        # Output growth and employment
        growth = scenario["initial_growth"] + output_gap + 0.25 * supply_build

        employment = (
            scenario["initial_employment"]
            + 0.22 * output_gap
            + 0.04 * supply_build
        )

        rows.append({
            "Period": period,
            "Quarter": t + 1,
            "GDP growth (%)": round(growth, 2),
            "Output gap (%)": round(output_gap, 2),
            "Inflation (%)": round(inflation, 2),
            "Bank Rate (%)": round(bank_rate, 2),
            "Employment rate (%)": round(employment, 2),
            "Exchange rate index": round(exchange_rate, 1),
            "Deficit pressure": round(deficit, 2),
            "Supply capacity effect": round(supply_build, 2),
        })

    return pd.DataFrame(rows)


def make_summary_table(df):
    return pd.DataFrame({
        "Indicator": [
            "Peak GDP growth",
            "Lowest GDP growth",
            "Peak inflation",
            "Final inflation",
            "Peak Bank Rate",
            "Highest employment rate",
            "Lowest exchange-rate index",
            "End-period output gap",
            "Deficit pressure"
        ],
        "Value": [
            f"{df['GDP growth (%)'].max():.2f}%",
            f"{df['GDP growth (%)'].min():.2f}%",
            f"{df['Inflation (%)'].max():.2f}%",
            f"{df['Inflation (%)'].iloc[-1]:.2f}%",
            f"{df['Bank Rate (%)'].max():.2f}%",
            f"{df['Employment rate (%)'].max():.2f}%",
            f"{df['Exchange rate index'].min():.1f}",
            f"{df['Output gap (%)'].iloc[-1]:.2f}%",
            f"{df['Deficit pressure'].iloc[-1]:.2f}"
        ]
    })


def generate_briefing_text(df, settings, scenario_name, event_name):
    peak_growth = df["GDP growth (%)"].max()
    peak_inflation = df["Inflation (%)"].max()
    peak_rate = df["Bank Rate (%)"].max()
    final_growth = df["GDP growth (%)"].iloc[-1]
    final_inflation = df["Inflation (%)"].iloc[-1]
    final_output_gap = df["Output gap (%)"].iloc[-1]
    min_fx = df["Exchange rate index"].min()

    demand = fiscal_demand_impulse(settings)
    supply = supply_impulse(settings)
    deficit = deficit_impulse(settings)

    stance = classify_fiscal_stance(demand)

    briefing = f"""
TREASURY BRIEFING PACK

Scenario:
{scenario_name}

Event:
{event_name}

1. Headline judgement

The Budget is classified as {stance.lower()}. The simulation produces peak GDP growth of {peak_growth:.2f}% and final-period growth of {final_growth:.2f}%. Inflation peaks at {peak_inflation:.2f}% and ends at {final_inflation:.2f}%.

2. Transmission channels

The fiscal demand impulse is {demand:.2f}. The supply capacity impulse is {supply:.2f}. Deficit pressure is {deficit:.2f}. Students should explain whether the main effect comes through aggregate demand, supply capacity, monetary policy, exchange-rate movements or fiscal credibility.

3. MPC response

The simulated Bank Rate peaks at {peak_rate:.2f}%. If inflation moves above target and the output gap is positive, the model assumes that the Bank of England raises Bank Rate, partly offsetting the Chancellor's fiscal policy.

4. Sterling and external risk

The exchange-rate index falls as low as {min_fx:.1f}. In this teaching model, sterling is influenced by the interest-rate response and by fiscal credibility pressure.

5. End-period position

By the final quarter, the output gap is {final_output_gap:.2f}%. Students should consider whether the Budget delivers only a short-run demand boost or whether it also improves the economy's medium-run supply capacity.

Student task:
Prepare a 90-second Chancellor's statement explaining your objective, the main transmission mechanism, the Bank of England response and one unintended consequence.
"""

    return briefing


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown(
    """
    <div class="treasury-header">
        <div class="treasury-eyebrow">LUBS2281 macroeconomic policy simulation</div>
        <div class="treasury-title">Be the Chancellor</div>
        <div class="treasury-subtitle">
            Design a Budget, face economic events, and explain the consequences for growth,
            inflation, employment, sterling and monetary policy.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    This app is a **simplified teaching simulator inspired by open-economy New Keynesian policy models**.
    It is designed to support economic reasoning and classroom debate. It is **not** an official forecast,
    OBR model or Bank of England model.
    """
)


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:
    st.header("1. Economic context")

    scenario_name = st.selectbox(
        "Starting scenario",
        list(SCENARIOS.keys())
    )

    st.info(SCENARIOS[scenario_name]["description"])

    st.header("2. Economic event")

    event_name = st.selectbox(
        "Event shock",
        list(EVENTS.keys())
    )

    if event_name == "No additional event":
        st.success(EVENTS[event_name]["description"])
    else:
        st.warning(EVENTS[event_name]["description"])

    st.header("3. Budget choices")

    st.markdown("### Tax policy")

    basic_income_tax = st.slider(
        "Basic rate income tax (%)",
        min_value=15.0,
        max_value=30.0,
        value=BASE["basic_income_tax"],
        step=0.5
    )

    higher_income_tax = st.slider(
        "Higher rate income tax (%)",
        min_value=35.0,
        max_value=50.0,
        value=BASE["higher_income_tax"],
        step=0.5
    )

    corporation_tax = st.slider(
        "Corporation tax (%)",
        min_value=15.0,
        max_value=35.0,
        value=BASE["corporation_tax"],
        step=0.5
    )

    personal_allowance = st.slider(
        "Personal allowance (£000s)",
        min_value=8.0,
        max_value=18.0,
        value=BASE["personal_allowance"],
        step=0.25
    )

    st.markdown("### Spending policy")
    st.caption("Spending variables are indices where 100 is the baseline.")

    health = st.slider(
        "Health spending",
        min_value=80.0,
        max_value=130.0,
        value=BASE["health"],
        step=1.0
    )

    education = st.slider(
        "Education spending",
        min_value=80.0,
        max_value=130.0,
        value=BASE["education"],
        step=1.0
    )

    welfare = st.slider(
        "Welfare spending",
        min_value=80.0,
        max_value=130.0,
        value=BASE["welfare"],
        step=1.0
    )

    defence = st.slider(
        "Defence spending",
        min_value=80.0,
        max_value=130.0,
        value=BASE["defence"],
        step=1.0
    )

    infrastructure = st.slider(
        "Green / infrastructure investment",
        min_value=70.0,
        max_value=150.0,
        value=BASE["infrastructure"],
        step=1.0
    )


settings = {
    "basic_income_tax": basic_income_tax,
    "higher_income_tax": higher_income_tax,
    "corporation_tax": corporation_tax,
    "personal_allowance": personal_allowance,
    "health": health,
    "education": education,
    "welfare": welfare,
    "defence": defence,
    "infrastructure": infrastructure,
}

df = simulate_economy(settings, scenario_name, event_name)
summary = make_summary_table(df)

demand = fiscal_demand_impulse(settings)
supply = supply_impulse(settings)
deficit = deficit_impulse(settings)

peak_growth = df["GDP growth (%)"].max()
peak_inflation = df["Inflation (%)"].max()
peak_rate = df["Bank Rate (%)"].max()
final_inflation = df["Inflation (%)"].iloc[-1]
final_growth = df["GDP growth (%)"].iloc[-1]
final_employment = df["Employment rate (%)"].iloc[-1]
min_exchange_rate = df["Exchange rate index"].min()

fiscal_stance = classify_fiscal_stance(demand)
inflation_risk_label, inflation_risk_class = classify_risk(peak_inflation, 2.7, 4.0)
fiscal_risk_label, fiscal_risk_class = classify_risk(deficit, 0.75, 2.0)
mpc_risk_label, mpc_risk_class = classify_risk(peak_rate, 4.75, 5.5)


# ------------------------------------------------------------
# Scenario and event panels
# ------------------------------------------------------------

left_panel, right_panel = st.columns([1.2, 1])

with left_panel:
    st.markdown(
        f"""
        <div class="scenario-panel">
            <strong>Current scenario:</strong> {scenario_name}<br>
            <span class="small-muted">{SCENARIOS[scenario_name]["description"]}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with right_panel:
    st.markdown(
        f"""
        <div class="event-card">
            <div class="event-title">Economic event: {event_name}</div>
            <div class="event-text">{EVENTS[event_name]["description"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# KPI cards
# ------------------------------------------------------------

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="kpi-label">Fiscal stance</div>
            <div class="kpi-value">{fiscal_stance}</div>
            <div class="kpi-note">Demand impulse: {demand:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="kpi-label">Peak growth</div>
            <div class="kpi-value">{peak_growth:.2f}%</div>
            <div class="kpi-note">Highest simulated GDP growth</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="kpi-label">Peak inflation</div>
            <div class="kpi-value">{peak_inflation:.2f}%</div>
            <div class="kpi-note">Target is 2%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="kpi-label">Peak Bank Rate</div>
            <div class="kpi-value">{peak_rate:.2f}%</div>
            <div class="kpi-note">Taylor-style policy response</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k5:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="kpi-label">Final employment</div>
            <div class="kpi-value">{final_employment:.2f}%</div>
            <div class="kpi-note">Illustrative employment rate</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# Tabs
# ------------------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Budget",
    "Macro paths",
    "Policy response",
    "Risk assessment",
    "Summary data",
    "Briefing pack"
])


with tab1:
    st.header("Your Budget package")

    budget_rows = pd.DataFrame({
        "Policy instrument": [
            "Basic rate income tax",
            "Higher rate income tax",
            "Corporation tax",
            "Personal allowance",
            "Health spending",
            "Education spending",
            "Welfare spending",
            "Defence spending",
            "Green / infrastructure investment"
        ],
        "Your setting": [
            f"{basic_income_tax:.1f}%",
            f"{higher_income_tax:.1f}%",
            f"{corporation_tax:.1f}%",
            f"£{personal_allowance:.2f}k",
            f"{health:.0f}",
            f"{education:.0f}",
            f"{welfare:.0f}",
            f"{defence:.0f}",
            f"{infrastructure:.0f}"
        ],
        "Baseline": [
            "20.0%",
            "40.0%",
            "25.0%",
            "£12.57k",
            "100",
            "100",
            "100",
            "100",
            "100"
        ],
        "Direction": [
            "Tax rise" if basic_income_tax > BASE["basic_income_tax"] else "Tax cut" if basic_income_tax < BASE["basic_income_tax"] else "Unchanged",
            "Tax rise" if higher_income_tax > BASE["higher_income_tax"] else "Tax cut" if higher_income_tax < BASE["higher_income_tax"] else "Unchanged",
            "Tax rise" if corporation_tax > BASE["corporation_tax"] else "Tax cut" if corporation_tax < BASE["corporation_tax"] else "Unchanged",
            "Higher threshold" if personal_allowance > BASE["personal_allowance"] else "Lower threshold" if personal_allowance < BASE["personal_allowance"] else "Unchanged",
            "Increase" if health > BASE["health"] else "Cut" if health < BASE["health"] else "Unchanged",
            "Increase" if education > BASE["education"] else "Cut" if education < BASE["education"] else "Unchanged",
            "Increase" if welfare > BASE["welfare"] else "Cut" if welfare < BASE["welfare"] else "Unchanged",
            "Increase" if defence > BASE["defence"] else "Cut" if defence < BASE["defence"] else "Unchanged",
            "Increase" if infrastructure > BASE["infrastructure"] else "Cut" if infrastructure < BASE["infrastructure"] else "Unchanged",
        ]
    })

    st.dataframe(budget_rows, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Fiscal demand impulse", f"{demand:.2f}")
    c2.metric("Supply capacity impulse", f"{supply:.2f}")
    c3.metric("Deficit pressure", f"{deficit:.2f}")

    st.markdown(
        """
        ### Teaching interpretation

        - A positive **fiscal demand impulse** means the Budget raises short-run aggregate demand.
        - A positive **supply capacity impulse** means the Budget gradually raises potential output.
        - A positive **deficit pressure** value means the package increases pressure on borrowing.
        """
    )


with tab2:
    st.header("Forward macroeconomic paths")

    st.markdown(
        """
        These charts show simulated paths over the next **12 quarters**.
        The purpose is to support policy reasoning, not to produce a literal forecast.
        """
    )

    macro_long = df.melt(
        id_vars=["Period", "Quarter"],
        value_vars=[
            "GDP growth (%)",
            "Inflation (%)",
            "Employment rate (%)",
            "Output gap (%)"
        ],
        var_name="Variable",
        value_name="Value"
    )

    fig_macro = px.line(
        macro_long,
        x="Period",
        y="Value",
        color="Variable",
        markers=True,
        title="Growth, inflation, employment and output gap"
    )

    fig_macro.update_layout(
        template="plotly_white",
        height=520,
        xaxis_title="Period",
        yaxis_title="Percent",
        legend_title="Variable",
        hovermode="x unified"
    )

    st.plotly_chart(fig_macro, use_container_width=True)


with tab3:
    st.header("Bank of England and exchange-rate response")

    policy_long = df.melt(
        id_vars=["Period", "Quarter"],
        value_vars=[
            "Bank Rate (%)",
            "Exchange rate index"
        ],
        var_name="Variable",
        value_name="Value"
    )

    fig_policy = px.line(
        policy_long,
        x="Period",
        y="Value",
        color="Variable",
        markers=True,
        title="Policy rate and exchange-rate response"
    )

    fig_policy.update_layout(
        template="plotly_white",
        height=520,
        xaxis_title="Period",
        yaxis_title="Percent / index",
        legend_title="Variable",
        hovermode="x unified"
    )

    st.plotly_chart(fig_policy, use_container_width=True)

    st.markdown(
        """
        ### Teaching interpretation

        The model uses a Taylor-style reaction function. If inflation rises above target and the output gap is positive,
        Bank Rate increases. The exchange rate responds to interest-rate movements and fiscal credibility pressure.
        """
    )


with tab4:
    st.header("Risk assessment")

    st.markdown(
        f"""
        <div class="briefing-box">
            <h3>Dashboard risk indicators</h3>
            <p>
                <span class="{inflation_risk_class}">{inflation_risk_label} inflation risk</span>
                <span class="{mpc_risk_class}">{mpc_risk_label} MPC tightening risk</span>
                <span class="{fiscal_risk_class}">{fiscal_risk_label} fiscal risk</span>
            </p>
            <p>
                Peak inflation is <strong>{peak_inflation:.2f}%</strong>, peak Bank Rate is
                <strong>{peak_rate:.2f}%</strong>, and deficit pressure is
                <strong>{deficit:.2f}</strong>.
            </p>
        </div>

        <div class="briefing-box">
            <h3>Main policy trade-off</h3>
            <p>
                The Chancellor must trade off short-run growth, inflation control, employment,
                fiscal credibility and sterling stability. A package that raises demand strongly may
                increase output and employment initially, but it may also raise inflation and trigger
                a Bank of England response.
            </p>
        </div>

        <div class="briefing-box">
            <h3>External vulnerability</h3>
            <p>
                The lowest simulated exchange-rate index is <strong>{min_exchange_rate:.1f}</strong>.
                In this model, sterling is weakened by fiscal pressure and supported by higher interest rates.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


with tab5:
    st.header("Simulation summary")

    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("### Full quarterly data")

    st.dataframe(df, use_container_width=True, hide_index=True)


with tab6:
    st.header("Treasury briefing pack")

    briefing_text = generate_briefing_text(df, settings, scenario_name, event_name)

    st.markdown(
        f"""
        <div class="briefing-box">
            <h3>1. Headline judgement</h3>
            <p>
            The Budget is classified as <strong>{fiscal_stance.lower()}</strong>.
            Peak GDP growth is <strong>{peak_growth:.2f}%</strong>, while final-period growth is
            <strong>{final_growth:.2f}%</strong>. Inflation peaks at
            <strong>{peak_inflation:.2f}%</strong> and ends at
            <strong>{final_inflation:.2f}%</strong>.
            </p>
        </div>

        <div class="briefing-box">
            <h3>2. Transmission channels</h3>
            <p>
            The fiscal demand impulse is <strong>{demand:.2f}</strong>.
            The supply capacity impulse is <strong>{supply:.2f}</strong>.
            Deficit pressure is <strong>{deficit:.2f}</strong>.
            Students should explain whether the dominant channel is aggregate demand,
            supply capacity, monetary policy, exchange-rate pressure or fiscal credibility.
            </p>
        </div>

        <div class="briefing-box">
            <h3>3. MPC response</h3>
            <p>
            The simulated Bank Rate peaks at <strong>{peak_rate:.2f}%</strong>.
            If inflation moves above target and the output gap is positive, the model assumes
            that the Bank of England raises Bank Rate, partly offsetting the fiscal stimulus.
            </p>
        </div>

        <div class="briefing-box">
            <h3>4. Event assessment</h3>
            <p>
            <strong>{event_name}</strong>: {EVENTS[event_name]["description"]}
            Students should explain how this event changes the policy trade-off facing the Chancellor.
            </p>
        </div>

        <div class="briefing-box">
            <h3>5. Chancellor's speaking note</h3>
            <p>
            Prepare a 90-second statement explaining your Budget. You should defend your policy objective,
            identify the main transmission mechanism, explain the Bank of England response and acknowledge
            one unintended consequence.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.download_button(
        label="Download briefing pack as text",
        data=briefing_text,
        file_name="treasury_briefing_pack.txt",
        mime="text/plain"
    )


st.divider()

st.caption(
    "Teaching caveat: This is a stylised LUBS2281 policy simulator. "
    "It uses simplified behavioural equations inspired by open-economy New Keynesian models. "
    "It is not an official forecast, OBR model or Bank of England model."
)
