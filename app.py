
import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# CONFIGURACIÓN DE LA APP
# -----------------------------
st.set_page_config(page_title="Valoración de Empresas - DCF", layout="wide")
st.title("💰 Valoración de Empresas por Flujos de Caja Descontados (DCF)")

# -----------------------------
# SUBIDA DE ARCHIVO
# -----------------------------
archivo = st.file_uploader("📂 Sube tu archivo Excel con las hojas 'ER' (Estado de Resultados) y 'BG' (Balance General)", type=["xlsx"])

# -----------------------------
# CARGA DE DATOS
# -----------------------------
if archivo is not None:
    try:
        datos = pd.read_excel(archivo, sheet_name=None)

        # Hojas esperadas
        estado_resultados = datos.get("ER")
        balance_general = datos.get("BG")

        if estado_resultados is not None and balance_general is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Estado de Resultados")
                st.dataframe(estado_resultados)
            with col2:
                st.subheader("📉 Balance General")
                st.dataframe(balance_general)

            st.divider()

            # -----------------------------
            # PARÁMETROS DE VALORACIÓN
            # -----------------------------
            st.subheader("⚙️ Parámetros de Valoración")

            tasa_descuento = st.number_input("Tasa de descuento (WACC)", min_value=0.01, max_value=0.30, value=0.10, step=0.01)
            crecimiento_terminal = st.number_input("Tasa de crecimiento a perpetuidad (g)", min_value=0.00, max_value=0.10, value=0.03, step=0.01)
            numero_acciones = st.number_input("Número de acciones en circulación", min_value=1_000, value=1_000_000)

            # -----------------------------
            # CÁLCULO DEL FLUJO DE CAJA LIBRE
            # -----------------------------
            st.subheader("💵 Cálculo del Flujo de Caja Libre (FCL)")

            # Creamos datos de ejemplo si no existen
            if "Utilidad Neta" in estado_resultados.columns:
                utilidad_neta = estado_resultados["Utilidad Neta"].values
            else:
                utilidad_neta = np.array([1000, 1200, 1400, 1600, 1800])

            if "Depreciación" in estado_resultados.columns:
                depreciacion = estado_resultados["Depreciación"].values
            else:
                depreciacion = np.array([200, 220, 240, 260, 280])

            if "CAPEX" in balance_general.columns:
                capex = balance_general["CAPEX"].values
            else:
                capex = np.array([300, 320, 340, 360, 380])

            if "ΔCapitalTrabajo" in balance_general.columns:
                delta_ct = balance_general["ΔCapitalTrabajo"].values
            else:
                delta_ct = np.array([50, 60, 70, 80, 90])

            fcl = utilidad_neta + depreciacion - capex - delta_ct

            df_fcl = pd.DataFrame({
                "Año": np.arange(1, len(fcl) + 1),
                "Utilidad Neta": utilidad_neta,
                "Depreciación": depreciacion,
                "CAPEX": capex,
                "Δ Capital de Trabajo": delta_ct,
                "FCL": fcl
            })

            st.dataframe(df_fcl.style.format({"FCL": "{:,.0f}"}))

            # -----------------------------
            # VALOR PRESENTE DE LOS FLUJOS
            # -----------------------------
            st.subheader("📈 Valoración por DCF")

            flujos_desc = [f / ((1 + tasa_descuento) ** t) for t, f in enumerate(fcl, start=1)]

            # Valor terminal (último flujo)
            valor_terminal = fcl[-1] * (1 + crecimiento_terminal) / (tasa_descuento - crecimiento_terminal)
            valor_terminal_desc = valor_terminal / ((1 + tasa_descuento) ** len(fcl))

            valor_empresa = np.sum(flujos_desc) + valor_terminal_desc
            valor_equity = valor_empresa  # sin deuda
            valor_accion = valor_equity / numero_acciones

            resultados = {
                "Valor Empresa (EV)": [valor_empresa],
                "Valor Terminal": [valor_terminal],
                "Valor del Patrimonio (Equity)": [valor_equity],
                "Valor por Acción": [valor_accion]
            }

            st.dataframe(pd.DataFrame(resultados).style.format("{:,.2f}"))

            # -----------------------------
            # GRÁFICO DE FLUJOS
            # -----------------------------
            st.subheader("📊 Gráfico de Flujos de Caja")
            st.bar_chart(df_fcl.set_index("Año")["FCL"])

            st.success("✅ Valoración completada con éxito.")
        else:
            st.warning("Por favor asegúrate de que el archivo contenga las hojas 'ER' y 'BG'.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")