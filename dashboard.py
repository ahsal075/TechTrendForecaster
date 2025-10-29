import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="TechTrend Forecaster", layout="wide")

st.title("📈 TechTrend Forecaster")
st.markdown("Forecast future tech trends using historical data and AI-powered models.")

# -------------------------------
# Data Upload Section
# -------------------------------
st.sidebar.header("Upload Your Dataset")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Display raw data
        st.subheader("📊 Uploaded Data Preview")
        st.dataframe(df.head())

        # Ensure proper column naming
        if {"Date", "Value"}.issubset(df.columns):
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.rename(columns={"Date": "ds", "Value": "y"})

            # Display data trend
            fig = px.line(df, x="ds", y="y", title="Historical Trend", markers=True)
            st.plotly_chart(fig, use_container_width=True)

            # -------------------------------
            # Forecasting
            # -------------------------------
            st.subheader("🔮 Forecast (Next 6 Months)")

            try:
                # Initialize Prophet with cmdstanpy backend
                model = Prophet()
                model.fit(df)

                future = model.make_future_dataframe(periods=180)
                forecast = model.predict(future)

                # Plot forecast
                fig_forecast = plot_plotly(model, forecast)
                st.plotly_chart(fig_forecast, use_container_width=True)

                st.success("✅ Forecast generated successfully!")

            except Exception as e:
                st.error("⚠️ Forecast generation failed. Please check your data format or dependencies.")
                st.code(str(e))

        else:
            st.warning("Please ensure your dataset has **Date** and **Value** columns.")

    except Exception as e:
        st.error("Error loading CSV file.")
        st.code(str(e))

else:
    st.info("👈 Upload a CSV file to begin forecasting.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Built by Ahsal Noushad | Powered by Streamlit + Prophet")
