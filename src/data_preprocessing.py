#codigo base para probar
import streamlit as st
import pandas as pd

def show(data):
    st.header("🧩 Exploración y calidad de datos")

    st.subheader("Vista general del dataset")
    st.write(f"Filas: {data.shape[0]} | Columnas: {data.shape[1]}")
    st.dataframe(data.head())

    st.subheader("Información básica")
    st.write(data.describe())

    st.subheader("Valores nulos por columna")
    st.bar_chart(data.isnull().sum())

    st.subheader("Distribución de registros por fecha")
    if 'date' in data.columns:
        counts = data['date'].value_counts().sort_index()
        st.line_chart(counts)

