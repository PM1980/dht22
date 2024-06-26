import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from pytz import UTC
from PIL import Image
from streamlit_option_menu import option_menu
import plotly.express as px

# Use Streamlit secrets for ThingSpeak credentials
CHANNEL_ID = st.secrets["thingspeak"]["channel_id"]
READ_API_KEY = st.secrets["thingspeak"]["read_api_key"]

# Define the timezone offset
TZ_OFFSET = timedelta(hours=-3)  # UTC-3

def fetch_data():
    try:
        url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=15000"
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        
        df = pd.DataFrame(data['feeds'])
        df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
        df['created_at'] = df['created_at'] + TZ_OFFSET  # Adjust for UTC-3
        df['field1'] = pd.to_numeric(df['field1'], errors='coerce')  # Temperature
        df['field2'] = pd.to_numeric(df['field2'], errors='coerce')  # Humidity
        
        # Sort the dataframe by date
        df = df.sort_values('created_at')
        
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from ThingSpeak: {e}")
        return pd.DataFrame()  # Return an empty DataFrame
    except KeyError as e:
        st.error(f"Error processing ThingSpeak data: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

def create_plot(df, y_col, title, y_label, color):
    fig = go.Figure()
    
    # Add main data
    fig.add_trace(go.Scatter(
        x=df['created_at'], y=df[y_col], 
        mode='lines', 
        name=y_label, 
        line=dict(color=color, width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Time (UTC-3)',
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

def create_heatmap(df):
    # Create a heatmap of temperature over time
    fig = px.density_heatmap(df, x='created_at', y='field1', 
                             title='Temperature Heatmap',
                             labels={'created_at': 'Time', 'field1': 'Temperature (°C)'},
                             color_continuous_scale='Viridis')
    return fig

def main():
    # ... (rest of the main function)

if __name__ == "__main__":
    main()
