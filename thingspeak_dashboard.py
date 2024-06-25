import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Use Streamlit secrets for ThingSpeak credentials
CHANNEL_ID = st.secrets["thingspeak"]["channel_id"]
READ_API_KEY = st.secrets["thingspeak"]["read_api_key"]

def fetch_data():
    # Fetch data from ThingSpeak
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=1000"
    response = requests.get(url)
    data = response.json()
    
    # Convert to DataFrame
    df = pd.DataFrame(data['feeds'])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['field1'] = pd.to_numeric(df['field1'])  # Temperature
    df['field2'] = pd.to_numeric(df['field2'])  # Humidity
    return df

def main():
    st.set_page_config(page_title="ThingSpeak Dashboard", layout="wide")
    st.title("Dados de Temperatura e Umidade do laboratório LabTag")

    # Fetch data
    df = fetch_data()

    # Create two columns for the charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Temperatura")
        fig_temp = px.line(df, x='created_at', y='field1', 
                           labels={'field1': 'Temperature (°C)', 'created_at': 'Time'},
                           line_shape='spline')
        fig_temp.update_layout(height=400)
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        st.subheader("Umidade (%)")
        fig_humidity = px.line(df, x='created_at', y='field2', 
                               labels={'field2': 'Humidity (%)', 'created_at': 'Time'},
                               line_shape='spline')
        fig_humidity.update_layout(height=400)
        st.plotly_chart(fig_humidity, use_container_width=True)

    # Display recent data in a table
    st.subheader("Recent Data")
    st.dataframe(df.tail(10).sort_values('created_at', ascending=False))

    # Add a date range selector
    st.sidebar.subheader("Date Range Selection")
    start_date = st.sidebar.date_input("Start Date", df['created_at'].min().date())
    end_date = st.sidebar.date_input("End Date", df['created_at'].max().date())

    # Filter data based on selected date range
    mask = (df['created_at'].dt.date >= start_date) & (df['created_at'].dt.date <= end_date)
    filtered_df = df.loc[mask]

    # Display summary statistics
    st.sidebar.subheader("Summary Statistics")
    st.sidebar.write(f"Average Temperature: {filtered_df['field1'].mean():.2f} °C")
    st.sidebar.write(f"Average Humidity: {filtered_df['field2'].mean():.2f} %")

if __name__ == "__main__":
    main()
