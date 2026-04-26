import streamlit as st
import pandas as pd

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="CO₂ Explorer", layout="wide")

# ---------------- MAIN DATASET ----------------
df = pd.read_csv("co2_emissions_kt_by_country.csv")
df = df.rename(columns={"value": "co2"})

# Clean country names in main dataset
df["country_name_clean"] = df["country_name"].astype(str).str.strip().str.lower()

# ---------------- FOSSIL DATASET ----------------
fuel = pd.read_csv("GCB2022v27_MtCO2_flat.csv")
fuel.columns = fuel.columns.str.strip().str.lower()

# Rename column if needed
if "entity" in fuel.columns:
    fuel = fuel.rename(columns={"entity": "country"})

# Clean fossil country names
fuel["country_clean"] = fuel["country"].astype(str).str.strip().str.lower()

# Fix USA naming issues
fuel["country_clean"] = fuel["country_clean"].replace({
    "united states of america": "united states",
    "usa": "united states",
    "us": "united states"
})

# ---------------- KEEP ONLY MATCHING COUNTRIES ----------------
valid_countries = sorted(
    set(df["country_name_clean"]).intersection(set(fuel["country_clean"]))
)

# ---------------- TITLE ----------------
st.title("🌍 CO₂ Emissions Explorer")

# ---------------- SIDEBAR ----------------
country = st.sidebar.selectbox(
    "Select a country",
    [c.title() for c in valid_countries]
)

# ---------------- FILTER DATA ----------------
country_data = df[df["country_name_clean"] == country.lower()].sort_values("year")
fuel_country = fuel[fuel["country_clean"] == country.lower()].sort_values("year")

# ---------------- METRIC ----------------
if not country_data.empty:
    st.metric("Latest CO₂ Emissions", f"{country_data['co2'].iloc[-1]:,.0f} kt")

st.markdown("---")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["Total Emissions", "Fossil Fuel Breakdown", "Compare Countries"])

# ---------------- TAB 1 ----------------
with tab1:
    st.subheader(f"CO₂ Emissions Over Time — {country}")

    if not country_data.empty:
        st.line_chart(country_data.set_index("year")["co2"])
    else:
        st.warning("No CO₂ data available.")

# ---------------- TAB 2 ----------------
with tab2:
    st.subheader("Fossil Fuel Emissions (Coal, Oil, Gas)")

    if fuel_country.empty:
        st.warning("No fossil fuel data available for this country.")
    else:
        latest = fuel_country.iloc[-1]

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

    c1 = st.selectbox("Country 1", valid_countries)
    c2 = st.selectbox("Country 2", valid_countries, index=1)

    d1 = df[df["country_name_clean"] == c1]
    d2 = df[df["country_name_clean"] == c2]

    compare_df = pd.DataFrame({
        c1.title(): d1.set_index("year")["co2"],
        c2.title(): d2.set_index("year")["co2"]
    }).dropna()

    if not compare_df.empty:
        compare_df = compare_df / compare_df.iloc[0] * 100
        st.line_chart(compare_df)
        st.caption("Normalized comparison (both start at 100)")
    else:
        st.warning("Not enough data for comparison.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("Built with Streamlit | CO₂ + Fossil Fuel Analysis")
