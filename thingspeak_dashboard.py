import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# Use Streamlit secrets for ThingSpeak credentials
CHANNEL_ID = st.secrets["thingspeak"]["channel_id"]
READ_API_KEY = st.secrets["thingspeak"]["read_api_key"]

def fetch_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=1000"
    response = requests.get(url)
    data = response.json()
    
    df = pd.DataFrame(data['feeds'])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['field1'] = pd.to_numeric(df['field1'])  # Temperature
    df['field2'] = pd.to_numeric(df['field2'])  # Humidity
    
    # Sort the dataframe by date
    df = df.sort_values('created_at')
    
    # Calculate moving averages using a fixed window of 72 periods (assuming 4 readings per hour, this is roughly 3 days)
    window_size = 72
    df['temp_ma'] = df['field1'].rolling(window=window_size, min_periods=1).mean()
    df['humidity_ma'] = df['field2'].rolling(window=window_size, min_periods=1).mean()
    
    return df

# The rest of the code remains the same

def create_plot(df, y_col, ma_col, title, y_label):
    fig = go.Figure()
    
    # Add main data
    fig.add_trace(go.Scatter(x=df['created_at'], y=df[y_col], mode='lines+markers', name=y_label))
    
    # Add moving average
    fig.add_trace(go.Scatter(x=df['created_at'], y=df[ma_col], mode='lines', name=f'Moving Avg', line=dict(color='red')))
    
    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title=y_label,
        legend_title='Legend',
        font=dict(family="Arial", size=12),
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        xaxis_rangeslider_visible=True
    )
    
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    
    return fig

def main():
    st.set_page_config(page_title="ThingSpeak Dashboard", layout="wide")
    st.title("ThingSpeak Temperature and Humidity Dashboard")

    df = fetch_data()

    col1, col2 = st.columns(2)

    with col1:
        fig_temp = create_plot(df, 'field1', 'temp_ma', 'Temperature Over Time', 'Temperature (°C)')
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        fig_humidity = create_plot(df, 'field2', 'humidity_ma', 'Humidity Over Time', 'Humidity (%)')
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
