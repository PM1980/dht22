import streamlit as st
import pandas as pd
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
        url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=1000"
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

def main():
    st.set_page_config(page_title="ThingSpeak Dashboard", layout="wide")

    with st.sidebar:
        img = Image.open("Logo e-Civil.png")
        st.image(img)
        
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Warehouse", "Query Optimization and Processing", "Storage", "Contato"],
            icons=["house", "gear", "activity", "snowflake", "envelope"],
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
            
        with col2:
            st.subheader("Umidade Atual")
            current_humidity = df['field2'].iloc[-1]  # Get the latest humidity value
            st.write(f"Atual: {current_humidity:.2f} %")

        # Calculate maximum and minimum temperatures in the last 10 days
        ten_days_ago = datetime.now() - timedelta(days=10)
        ten_days_ago = ten_days_ago.replace(tzinfo=UTC)  # Convert to UTC timezone
        recent_data = df[df['created_at'] >= ten_days_ago]
        max_temp = recent_data['field1'].max()
        min_temp = recent_data['field1'].min()
        max_temp_time = recent_data.loc[recent_data['field1'].idxmax(), 'created_at']
        min_temp_time = recent_data.loc[recent_data['field1'].idxmin(), 'created_at']

        max_humidity = recent_data['field2'].max()
        min_humidity = recent_data['field2'].min()
        max_humidity_time = recent_data.loc[recent_data['field2'].idxmax(), 'created_at']
        min_humidity_time = recent_data.loc[recent_data['field2'].idxmin(), 'created_at']

        # Display maximum and minimum values with timestamps
        st.subheader("Temperaturas Extremas (Últimos 10 dias)")
        st.markdown(
            f"**Máxima Temperatura:** {max_temp:.2f} °C\n"
            f"Registrada em: {max_temp_time.strftime('%Y-%m-%d %H:%M:%S')} UTC-3\n\n"
            f"**Mínima Temperatura:** {min_temp:.2f} °C\n"
            f"Registrada em: {min_temp_time.strftime('%Y-%m-%d %H:%M:%S')} UTC-3"
        )

        st.subheader("Umidades Extremas (Últimos 10 dias)")
        st.markdown(
            f"**Máxima Umidade:** {max_humidity:.2f} %\n"
            f"Registrada em: {max_humidity_time.strftime('%Y-%m-%d %H:%M:%S')} UTC-3\n\n"
            f"**Mínima Umidade:** {min_humidity:.2f} %\n"
            f"Registrada em: {min_humidity_time.strftime('%Y-%m-%d %H:%M:%S')} UTC-3"
        )

if __name__ == "__main__":
    main()
