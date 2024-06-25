import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from pytz import UTC  # Import UTC timezone from pytz
from PIL import Image
from streamlit_option_menu import option_menu

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

def main():
    st.set_page_config(page_title="ThingSpeak Dashboard", layout="wide")

    with st.sidebar:
        img = Image.open("Logo e-Civil.png")
        st.image(img)
        
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Setup", "Código", "Contato"],
            icons=["house", "activity", "gear", "envelope"],
            menu_icon="cast",
            default_index=0
        )

    if selected == "Home":
        st.header("Monitoramento da temperatura e umidade")
        st.header("Laboratório LabTag/UFPE")

        df = fetch_data()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Temperatura Atual")
            current_temp = df['field1'].iloc[-1]  # Get the latest temperature value
            st.write(f"Atual: {current_temp:.2f} °C")
            
            fig_temp = create_plot(df, 'field1', 'Temperatura vs tempo', 'Temperatura (°C)', 'blue')
            st.plotly_chart(fig_temp, use_container_width=True)

        with col2:
            st.subheader("Umidade Atual")
            current_humidity = df['field2'].iloc[-1]  # Get the latest humidity value
            st.write(f"Atual: {current_humidity:.2f} %")
            
            fig_humidity = create_plot(df, 'field2', 'Umidade vs tempo', 'Umidade (%)', 'green')
            st.plotly_chart(fig_humidity, use_container_width=True)

        # Calculate maximum and minimum temperatures in the last 10 days
        ten_days_ago = datetime.now() - timedelta(days=10)
        ten_days_ago = ten_days_ago.replace(tzinfo=UTC)  # Convert to UTC timezone
        recent_data = df[df['created_at'] >= ten_days_ago]
        max_temp = recent_data['field1'].max()
        min_temp = recent_data['field1'].min()
        max_temp_time = recent_data.loc[recent_data['field1'].idxmax(), 'created_at']
        min_temp_time = recent_data.loc[recent_data['field1'].idxmin(), 'created_at']

        # Display captions with maximum and minimum temperatures and corresponding datetime
        st.subheader("Temperaturas Extremas (Últimos 10 dias)")
        st.write(f"Máxima: {max_temp:.2f} °C, Registrada em {max_temp_time.strftime('%Y-%m-%d %H:%M:%S')} UTC-3")
        st.write(f"Mínima: {min_temp:.2f} °C, Registrada em {min_temp_time.strftime('%Y-%m-%d %H:%M:%S')} UTC-3")
        
        # Display first and last timestamps
        st.subheader("Primeiro e Último Registro")
        first_timestamp = df['created_at'].iloc[0]
        last_timestamp = df['created_at'].iloc[-1]
        st.write(f"Primeiro Registro: {first_timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC-3")
        st.write(f"Último Registro: {last_timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC-3")    
    
    elif selected == "Setup":
        st.subheader("Detalhamento do microcontrolador e sensor")
        st.image("setup_esp_dht22.png", use_column_width=True)
    
    elif selected == "Código":
        st.markdown("[Código fonte do Dashboard](https://github.com/PM1980/dht22/blob/main/thingspeak_dashboard.py)")

    elif selected == "Contato":
        st.markdown("https://www.instagram.com/projeto_ecivil/")

if __name__ == "__main__":
    main()
