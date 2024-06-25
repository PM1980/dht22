import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from pytz import UTC  # Import UTC timezone from pytz
from PIL import Image, ImageFont
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
            fig_temp = create_plot(df, 'field1', 'Temperatura vs tempo', 'Temperatura (°C)', 'blue')
            st.plotly_chart(fig_temp, use_container_width=True)

        with col2:
            fig_humidity = create_plot(df, 'field2', 'Umidade vs tempo', 'Umidade (%)', 'blue')
            st.plotly_chart(fig_humidity, use_container_width=True)

        # Display recent data with selected columns in a styled table
        st.subheader("Dados Recentes (UTC-3)")
        recent_data_table = df.tail(10).sort_values('created_at', ascending=False).reset_index(drop=True)[['created_at', 'field1', 'field2']]
        st.table(recent_data_table.style.set_properties(**{
            'font-family': 'Arial, sans-serif',  # Example of a more fancy font style
            'text-align': 'center',
            'background-color': 'lightblue',
            'color': 'black'
        }))

        # Calculate maximum and minimum temperatures in the last 10 days
        ten_days_ago = datetime.now() - timedelta(days=10)
        ten_days_ago = ten_days_ago.replace(tzinfo=UTC)  # Convert to UTC timezone
        recent_data = df[df['created_at'] >= ten_days_ago]
        max_temps = recent_data.nlargest(3, 'field1')  # Top 3 maximum temperatures
        min_temps = recent_data.nsmallest(3, 'field1')  # Top 3 minimum temperatures

        # Prepare styled tables for extreme temperatures without index
        max_temps_table = pd.DataFrame({
            'Data e Hora': max_temps['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S'),
            'Temperatura (°C)': max_temps['field1']
        })
        min_temps_table = pd.DataFrame({
            'Data e Hora': min_temps['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S'),
            'Temperatura (°C)': min_temps['field1']
        })

        # Display styled extreme temperatures tables without index
        st.subheader("Temperaturas Máximas (Últimos 10 dias)")
        st.table(max_temps_table.style.set_properties(**{
            'text-align': 'center',
            'background-color': 'lightgreen',
            'color': 'black'
        }).hide_index())

        st.subheader("Temperaturas Mínimas (Últimos 10 dias)")
        st.table(min_temps_table.style.set_properties(**{
            'text-align': 'center',
            'background-color': 'lightcoral',
            'color': 'black'
        }).hide_index())

    elif selected == "Warehouse":
        st.subheader(f"**You Have selected {selected}**")
        # Snowflake connection and querying would go here

    elif selected == "Contato":
        st.subheader(f"**Informações para contato e redes sociais**")
        st.markdown("https://www.instagram.com/projeto_ecivil/")
        # Contact form or information would go here

if __name__ == "__main__":
    main()
