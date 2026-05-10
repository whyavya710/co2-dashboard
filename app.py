import streamlit as st
import pandas as pd

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="CO₂ Explorer", layout="wide")
st.title("🌍 CO₂ Emissions Dashboard")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("co2_emissions_kt_by_country.csv")
fuel = pd.read_csv("GCB2022v27_MtCO2_flat.csv")

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

    country_data = df[
        df["country_name_clean"] == country.lower()
    ].sort_values("year")

    if not country_data.empty:
        st.metric(
            "Latest CO₂ Emissions",
            f"{country_data['co2'].iloc[-1]:,.0f} kt"
        )

    st.markdown("---")

    st.subheader(f"CO₂ Emissions for {country}")

    if not country_data.empty:
        chart1 = country_data.set_index("year")[["co2"]]
        st.line_chart(chart1)
        st.caption("X-axis: Year | Y-axis: CO₂ Emissions (kt)")
    else:
        st.warning("No data available.")

# =====================================================
# TAB 2 - FOSSIL FUEL EMISSIONS
# =====================================================
with tab2:

    st.subheader(f"Fossil Fuel Emissions for {country}")

    fuel_country = fuel[
        fuel["country_clean"] == country.lower()
    ].sort_values("year")

    # NOTE: This dataset may NOT have coal/oil/gas columns
    # so we safely check before plotting

    possible_cols = [c for c in fuel_country.columns if "co2" in c.lower()]

    if not fuel_country.empty and len(possible_cols) > 0:

        chart2 = fuel_country.set_index("year")[possible_cols]
        st.line_chart(chart2)

        st.caption("X-axis: Year | Y-axis: CO₂ from fossil fuels")

    else:
        st.warning("No fossil fuel breakdown data available for this country.")

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

        compare_df = compare_df / compare_df.iloc[0] * 100

        st.line_chart(compare_df)

        st.caption(
            "X-axis: Year | Y-axis: Normalized CO₂ Emissions (start = 100)"
        )

    else:
        st.warning("Not enough data for comparison.")
