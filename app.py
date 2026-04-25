import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="CO₂ Explorer", layout="wide")

# ---------------- MAIN DATASET ----------------
df = pd.read_csv("co2_emissions_kt_by_country.csv")
df = df.rename(columns={"value": "co2"})

# ---------------- FOSSIL DATASET ----------------
fuel = pd.read_csv("GCB2022v27_MtCO2_flat.csv")
fuel.columns = fuel.columns.str.lower()

# FIX: standardize country name mismatch
fuel["country"] = fuel["country"].replace({
    "United States of America": "United States"
})

# ---------------- TITLE ----------------
st.title("CO₂ Emissions Explorer")
st.markdown("Explore total CO₂ emissions and fossil fuel sources (coal, oil, gas).")

# ---------------- SIDEBAR ----------------
countries = sorted(df["country_name"].unique())
country = st.sidebar.selectbox("Select a country", countries)

# ---------------- TOTAL EMISSIONS ----------------
country_data = df[df["country_name"] == country].sort_values("year")

latest_value = country_data["co2"].iloc[-1]
st.metric("Latest CO₂ Emissions", f"{latest_value:,.0f} kt")

st.markdown("---")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["Total Emissions", "Fossil Fuel Breakdown", "Compare Countries"])

# ---------------- TAB 1 ----------------
with tab1:
    st.subheader(f"CO₂ Emissions Over Time — {country}")
    st.line_chart(country_data.set_index("year")["co2"])

# ---------------- TAB 2 ----------------
with tab2:
    st.subheader("Fossil Fuel Emissions (Coal, Oil, Gas)")

    fuel_country = fuel[fuel["country"] == country]

    if fuel_country.empty:
        st.warning("No fossil fuel data available for this country.")
    else:
        latest = fuel_country.sort_values("year").iloc[-1]

        st.write("Latest Fossil Fuel Breakdown:")

        st.metric("Coal", f"{latest.get('coal', 0):,.0f} MtCO₂")
        st.metric("Oil", f"{latest.get('oil', 0):,.0f} MtCO₂")
        st.metric("Gas", f"{latest.get('gas', 0):,.0f} MtCO₂")

        st.bar_chart({
            "Coal": latest.get("coal", 0),
            "Oil": latest.get("oil", 0),
            "Gas": latest.get("gas", 0)
        })

# ---------------- TAB 3 ----------------
with tab3:
    st.subheader("Compare Countries")

    c1 = st.selectbox("Country 1", countries)
    c2 = st.selectbox("Country 2", countries, index=1)

    data1 = df[df["country_name"] == c1].sort_values("year")
    data2 = df[df["country_name"] == c2].sort_values("year")

    compare_df = pd.DataFrame({
        c1: data1.set_index("year")["co2"],
        c2: data2.set_index("year")["co2"]
    })

    # Normalize comparison (fix graph issue)
    compare_df = compare_df / compare_df.iloc[0] * 100

    st.line_chart(compare_df)
    st.caption("Normalized comparison (both start at 100 for fair trend comparison)")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("🌱 Built with Streamlit | CO₂ + Fossil Fuel Analysis")
