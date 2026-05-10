import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="CO₂ Explorer", layout="wide")

st.title("🌍 CO₂ Emissions Dashboard")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("co2_emissions_kt_by_country.csv")
fuel = pd.read_csv("fossil_fuel_co2_emissions-by-nation_with_continent.csv")

# ---------------- CLEAN MAIN DATASET ----------------
df = df.rename(columns={"value": "co2"})

df["country_name_clean"] = df["country_name"].str.lower()

invalid = [
    "world",
    "high income",
    "low income",
    "lower middle income",
    "upper middle income",
    "europe & central asia",
    "east asia & pacific",
    "north america",
    "south asia",
    "sub-saharan africa",
    "middle east & north africa",
    "latin america & caribbean",
    "european union"
]

df = df[~df["country_name_clean"].isin(invalid)]

# ---------------- CLEAN FUEL DATASET ----------------
fuel["country_clean"] = fuel["country"].str.lower()

# ---------------- COUNTRY LIST ----------------
valid_countries = sorted(df["country_name"].dropna().unique())

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs([
    "CO₂ Trends",
    "Fossil Fuel Emissions",
    "Compare Countries"
])

# =====================================================
# TAB 1 - CO₂ TRENDS
# =====================================================
with tab1:

    country = st.selectbox("Select a Country", valid_countries)

    # FILTER DATA
    country_data = df[
        df["country_name_clean"] == country.lower()
    ].sort_values("year")

    # METRIC
    if not country_data.empty:
        st.metric(
            "Latest CO₂ Emissions",
            f"{country_data['co2'].iloc[-1]:,.0f} kt"
        )

    st.markdown("---")

    # GRAPH
    fig1 = px.line(
        country_data,
        x="year",
        y="co2",
        title=f"CO₂ Emissions for {country}"
    )

    fig1.update_layout(
        xaxis_title="Year",
        yaxis_title="CO₂ Emissions (kt)",
        xaxis_tickangle=0
    )

    st.plotly_chart(fig1, use_container_width=True)

# =====================================================
# TAB 2 - FOSSIL FUEL EMISSIONS
# =====================================================
with tab2:

    st.subheader(
        f"Fossil Fuel Emissions (Coal, Oil, Gas) for {country}"
    )

    fuel_country = fuel[
        fuel["country_clean"] == country.lower()
    ].sort_values("year")

    if not fuel_country.empty:

        fig2 = px.line(
            fuel_country,
            x="year",
            y=["coal_co2", "oil_co2", "gas_co2"]
        )

        fig2.update_layout(
            xaxis_title="Year",
            yaxis_title="Fossil Fuel Emissions",
            xaxis_tickangle=0
        )

        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.warning("No fossil fuel data available for this country.")

# =====================================================
# TAB 3 - COMPARE COUNTRIES
# =====================================================
with tab3:

    st.subheader("Compare Countries")

    c1 = st.selectbox("Country 1", valid_countries)
    c2 = st.selectbox("Country 2", valid_countries, index=1)

    d1 = df[df["country_name_clean"] == c1.lower()]
    d2 = df[df["country_name_clean"] == c2.lower()]

    compare_df = pd.DataFrame({
        c1.title(): d1.set_index("year")["co2"],
        c2.title(): d2.set_index("year")["co2"]
    }).dropna()

    if not compare_df.empty:

        # NORMALIZE
        compare_df = compare_df / compare_df.iloc[0] * 100

        compare_df = compare_df.reset_index()

        fig3 = px.line(
            compare_df,
            x="year",
            y=compare_df.columns[1:]
        )

        fig3.update_layout(
            xaxis_title="Year",
            yaxis_title="Normalized CO₂ Emissions",
            xaxis_tickangle=0
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.caption("Normalized comparison (both start at 100)")

    else:
        st.warning("Not enough data for comparison.")
