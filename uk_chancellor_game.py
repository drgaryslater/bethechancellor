import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# BE THE CHANCELLOR
# LUBS2281 teaching simulator
#
# This is a simplified open-economy New Keynesian teaching model.
# It is not a Bank of England forecast and should not be presented
# as an official DSGE model.
# ============================================================

st.set_page_config(
    page_title="Be the Chancellor",
    page_icon="🏛️",
    layout="wide"
)

# ------------------------------------------------------------
# Baseline policy settings
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
        "description": "The economy begins close to potential, with inflation at target and monetary policy broadly neutral."
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
        "description": "Inflation starts well above target. Fiscal loosening risks provoking a stronger Bank of England response."
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
    This captures delayed supply-side effects of education, health,
    infrastructure and investment-supporting policy.
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
    This is a stylised teaching indicator, not a public finance forecast.
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


def simulate_economy(settings, scenario_name, quarters=12):
    scenario = SCENARIOS[scenario_name]

    demand = fiscal_demand_impulse(settings) * scenario["demand_sensitivity"]
    supply = supply_impulse(settings)
    deficit = deficit_impulse(settings)

    output_gap = scenario["initial_output_gap"]
    inflation = scenario["initial_inflation"]
    bank_rate = scenario["initial_bank_rate"]
    employment = scenario["initial_employment"]
    exchange_rate = scenario["initial_exchange_rate"]

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

        # Inflation dynamics:
        # partly persistent, pulled to 2%, affected by output gap,
        # fiscal credibility pressure and supply-side improvement.
        inflation = (
            0.65 * inflation
            + 0.35 * 2.0
            + scenario["inflation_sensitivity"] * 0.28 * output_gap
            + scenario["fiscal_risk_sensitivity"] * 0.05 * deficit
            - 0.08 * supply_build
        )

        # Taylor-style monetary policy rule
        desired_rate = (
            4.0
            + scenario["monetary_sensitivity"] * 1.35 * (inflation - 2.0)
            + 0.35 * output_gap
        )

        bank_rate = 0.72 * bank_rate + 0.28 * desired_rate

        # Exchange rate:
        # higher rates support sterling; deficit pressure weakens it.
        exchange_rate = (
            scenario["initial_exchange_rate"]
            + 1.7 * (bank_rate - scenario["initial_bank_rate"])
            - scenario["fiscal_risk_sensitivity"] * 0.32 * deficit
        )

        # Growth and employment
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
    summary = pd.DataFrame({
        "Indicator": [
            "Peak GDP growth",
            "Lowest GDP growth",
            "Peak inflation",
            "Peak Bank Rate",
            "Highest employment rate",
            "Lowest exchange rate index",
            "End-period output gap",
            "Deficit pressure"
        ],
        "Value": [
            f"{df['GDP growth (%)'].max():.2f}%",
            f"{df['GDP growth (%)'].min():.2f}%",
            f"{df['Inflation (%)'].max():.2f}%",
            f"{df['Bank Rate (%)'].max():.2f}%",
            f"{df['Employment rate (%)'].max():.2f}%",
            f"{df['Exchange rate index'].min():.1f}",
            f"{df['Output gap (%)'].iloc[-1]:.2f}%",
            f"{df['Deficit pressure'].iloc[-1]:.2f}"
        ]
    })

    return summary


def generate_briefing(df, settings, scenario_name):
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

    if demand > 0.5:
        fiscal_stance = "expansionary"
    elif demand < -0.5:
        fiscal_stance = "contractionary"
    else:
        fiscal_stance = "broadly neutral"

    if supply > 0.2:
        supply_message = "The package also contains meaningful supply-side support, mainly through education, health and infrastructure spending."
    elif supply < -0.1:
        supply_message = "The package weakens the supply side slightly, mainly because higher business taxation offsets productive spending effects."
    else:
        supply_message = "The package has only a limited supply-side effect, so most of the short-run impact works through aggregate demand."

    if peak_inflation > 4:
        inflation_message = "Inflation rises materially above target, creating a clear monetary policy trade-off."
    elif peak_inflation > 2.5:
        inflation_message = "Inflation moves above target, requiring some monetary tightening."
    else:
        inflation_message = "Inflation remains relatively close to target."

    if peak_rate > 5.5:
        mpc_message = "The simulated MPC response is strong: Bank Rate rises sharply to lean against inflationary pressure."
    elif peak_rate > 4.75:
        mpc_message = "The simulated MPC response is moderate: Bank Rate rises as inflation and the output gap increase."
    else:
        mpc_message = "The simulated MPC response is limited because inflationary pressure remains contained."

    briefing = f"""
### Chancellor's briefing

**Scenario:** {scenario_name}

Your Budget is assessed as **{fiscal_stance}**. The model estimates a fiscal demand impulse of **{demand:.2f}** and deficit pressure of **{deficit:.2f}**.

{supply_message}

The forward simulation shows peak GDP growth of **{peak_growth:.2f}%**, with growth ending at **{final_growth:.2f}%** by the final quarter. The output gap ends at **{final_output_gap:.2f}%**.

{inflation_message} Peak inflation reaches **{peak_inflation:.2f}%**, compared with the 2% target.

{mpc_message} The peak simulated Bank Rate is **{peak_rate:.2f}%**.

Sterling falls as low as an index value of **{min_fx:.1f}**. In this teaching model, sterling is affected by both the interest-rate response and fiscal credibility pressure.

### Questions for students

1. What was your main policy objective: growth, inflation control, employment, public services or fiscal credibility?
2. Which transmission channel dominated: demand, supply, monetary policy, exchange rate or deficit pressure?
3. Did the Bank of England reinforce or offset your fiscal policy?
4. Was your package more effective in the short run or medium run?
5. What would you change if you had to present a revised Budget?
"""

    return briefing


# ------------------------------------------------------------
# Interface
# ------------------------------------------------------------

st.title("🏛️ Be the Chancellor")
st.subheader("A LUBS2281 fiscal policy simulation game")

st.markdown(
    """
This app lets students choose tax and spending settings, then examine simulated forward paths for
growth, inflation, employment, Bank Rate and the exchange rate.

It is a **simplified teaching simulator inspired by open-economy New Keynesian policy models**.
It is **not** an official forecast and should be used to support economic reasoning rather than prediction.
"""
)

with st.sidebar:
    st.header("1. Choose the economy")

    scenario_name = st.selectbox(
        "Starting scenario",
        list(SCENARIOS.keys())
    )

    st.info(SCENARIOS[scenario_name]["description"])

    st.header("2. Choose your Budget")

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

df = simulate_economy(settings, scenario_name)
summary = make_summary_table(df)

demand = fiscal_demand_impulse(settings)
supply = supply_impulse(settings)
deficit = deficit_impulse(settings)

# ------------------------------------------------------------
# Headline cards
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Fiscal demand impulse", f"{demand:.2f}")

with col2:
    st.metric("Supply capacity impulse", f"{supply:.2f}")

with col3:
    st.metric("Deficit pressure", f"{deficit:.2f}")

with col4:
    st.metric("Final inflation", f"{df['Inflation (%)'].iloc[-1]:.2f}%")

# ------------------------------------------------------------
# Tabs
# ------------------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Budget choices",
    "Macro paths",
    "Policy response",
    "Summary table",
    "Briefing"
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
        ]
    })

    st.dataframe(budget_rows, use_container_width=True, hide_index=True)

    st.markdown(
        """
### Interpretation

- A positive **fiscal demand impulse** means the Budget raises short-run aggregate demand.
- A positive **supply capacity impulse** means the Budget gradually raises potential output.
- A positive **deficit pressure** value means the package increases pressure on borrowing.
"""
    )

with tab2:
    st.header("Forward macroeconomic paths")

    st.markdown(
        """
These are simulated forward paths over the next **12 quarters**.
The purpose is to encourage students to reason through the mechanisms, not to produce a literal forecast.
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
        xaxis_title="Period",
        yaxis_title="Percent / index value",
        legend_title="Variable"
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
        xaxis_title="Period",
        yaxis_title="Percent / index value",
        legend_title="Variable"
    )

    st.plotly_chart(fig_policy, use_container_width=True)

    st.markdown(
        """
### Teaching interpretation

The model uses a Taylor-style reaction function. If inflation rises above target and the output gap is positive,
Bank Rate increases. The exchange rate responds to interest-rate differentials and fiscal credibility pressure.
"""
    )

with tab4:
    st.header("Simulation summary")

    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("### Full quarterly data")

    st.dataframe(df, use_container_width=True, hide_index=True)

with tab5:
    st.header("Chancellor's briefing")

    briefing = generate_briefing(df, settings, scenario_name)
    st.markdown(briefing)

    st.download_button(
        label="Download briefing as text",
        data=briefing,
        file_name="chancellors_briefing.txt",
        mime="text/plain"
    )

st.divider()

st.caption(
    "Teaching caveat: This is a stylised policy simulator for LUBS2281. "
    "It uses simplified behavioural equations inspired by open-economy New Keynesian models. "
    "It is not an official forecast, OBR model or Bank of England model."
)
