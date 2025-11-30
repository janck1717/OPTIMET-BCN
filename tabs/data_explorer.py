import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd
import pydeck as pdk
import os

# ======================================
# CONFIGURACIÓN DE LA PÁGINA
# ======================================
st.set_page_config(
    page_title="Exploración y Calidad de Datos",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Exploración y Calidad de Datos")
st.markdown("### Análisis estructural y calidad de los datasets de movilidad")


# ======================================
# FUNCIÓN PARA CARGAR DATASETS LOCALES
# ======================================
@st.cache_data
def load_local_dataset(year):
    base_path = "dataset_optimet/"
    filename = f"final_combined_with_events_{year}.csv"
    full_path = os.path.join(base_path, filename)
    return pd.read_csv(full_path)

# CARGA DE DATASETS 2023 Y 2024
try:
    df_2023 = load_local_dataset(2023)
    df_2024 = load_local_dataset(2024)
    df = pd.concat([df_2023, df_2024], ignore_index=True)  # Dataset combinado

    st.success("Datasets 2023 y 2024 cargados correctamente")

except Exception as e:
    st.error(f"Error al cargar datasets locales: {e}")
    st.stop()

# ======================================
# SECCIÓN: RESUMEN GENERAL
# ======================================
st.header("📊 Resumen general de datasets")

summary_data = []

for name, df in datasets.items():
    summary_data.append({
        "Dataset": name,
        "Registros": len(df),
        "Columnas": len(df.columns),
        "Tamaño (MB)": round(df.memory_usage(deep=True).sum() / 1e6, 2),
        "Fecha mínima": df["day"].min() if "day" in df else "-",
        "Fecha máxima": df["day"].max() if "day" in df else "-",
        "Unidades espaciales": df["origin"].nunique() if "origin" in df else "-"
    })

st.dataframe(pd.DataFrame(summary_data))


# ======================================
# SECCIÓN: KPIs CLAVE
# ======================================
st.header("📈 Indicadores clave")

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

df_mun = datasets["Municipios"]

kpi_col1.metric("Total viajes registrados", f"{df_mun['viajes'].sum():,}")
kpi_col2.metric("Municipios únicos", df_mun["origin"].nunique())
kpi_col3.metric("Días cubiertos", len(df_mun["day"].unique()))


# ======================================
# SECCIÓN: HISTOGRAMAS
# ======================================
st.header("📊 Histogramas y distribuciones")

df = df_mun.copy()
df["day"] = pd.to_datetime(df["day"])
df["weekday"] = df["day"].dt.day_name()

h1, h2, h3 = st.columns(3)

with h1:
    st.subheader("📅 Viajes por día")
    daily = df.groupby("day")["viajes"].sum().reset_index()
    fig = px.bar(daily, x="day", y="viajes")
    st.plotly_chart(fig, use_container_width=True)

with h2:
    st.subheader("📆 Viajes por día de la semana")
    week = df.groupby("weekday")["viajes"].sum().reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ])
    fig = px.bar(week, x=week.index, y=week.values)
    st.plotly_chart(fig, use_container_width=True)

with h3:
    st.subheader("🌍 Distribución por tipo de origen")
    if "origen" in df.columns:
        fig = px.pie(df, names="origen")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Columna 'origen' no encontrada")


# ======================================
# SECCIÓN: DETECCIÓN DE OUTLIERS
# ======================================
st.header("🚨 Detección de outliers")

daily["zscore"] = (daily["viajes"] - daily["viajes"].mean()) / daily["viajes"].std()

outliers = daily[np.abs(daily["zscore"]) > 3]

st.subheader("📌 Días con valores anómalos (|z-score| > 3)")
st.dataframe(outliers)

faltantes = df[df["viajes"] == 0]

st.subheader("📍 Registros con viajes = 0")
st.dataframe(faltantes.head(20))


# ======================================
# SECCIÓN: MINI MAPA DE MUNICIPIOS
# ======================================
st.header("🗺️ Mapa de densidad de registros por municipio")

muni_path = data_folder + "municipios.geojson"

if os.path.exists(muni_path):
    gdf = gpd.read_file(muni_path)
    gdf = gdf.merge(
        df.groupby("origin")["viajes"].sum().reset_index(),
        left_on="code",
        right_on="origin",
        how="left"
    ).fillna(0)

    midpoint = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]

    layer = pdk.Layer(
        "GeoJsonLayer",
        data=gdf,
        get_fill_color="[255 * (viajes / viajes.max()), 50, 50, 150]",
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(latitude=midpoint[0], longitude=midpoint[1], zoom=8)

    st.pydeck_chart(pdk.Deck(
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{name}: {viajes} viajes"}
    ))
else:
    st.warning("No se encontró el archivo municipios.geojson")


st.markdown("---")
st.caption("Módulo 1 · Exploración y Calidad de Datos · OPTIMET-BCN")

