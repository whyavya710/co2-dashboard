import os

BASE_DIR = os.path.dirname(__file__)

df_path = os.path.join(BASE_DIR, "co2_emissions_kt_by_country.csv")
fuel_path = os.path.join(BASE_DIR, "fossil_fuel_co2_emissions-by-nation_with_continent.csv")

df = pd.read_csv(df_path)
fuel = pd.read_csv(fuel_path)
