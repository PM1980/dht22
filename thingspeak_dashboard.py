import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from pytz import UTC
from PIL import Image
from streamlit_option_menu import option_menu
import plotly.express as px

# ... (keep existing imports and constants)

def fetch_data():
    # ... (keep existing fetch_data function)

def create_plot(df, y_col, title, y_label, color):
    # ... (keep existing create_plot function)

def create_heatmap(df):
    # Create a heatmap of temperature over time
    fig = px.density_heatmap(df, x='created_at', y='field1', 
                             title='Temperature Heatmap',
                             labels={'created_at': 'Time', 'field1': 'Temperature (°C)'},
                             color_continuous_scale='Viridis')
    return fig

def main():
    st.set_page_config(page_title="Enhanced ThingSpeak Dashboard", layout="wide", initial_sidebar_state="expanded")

    # Custom CSS to improve the overall look
    st.markdown("""
        <style>
        .stApp {
            background-color: #f0f2f6;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        .stProgress .st-bo {
            background-color: #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        img = Image.open("Logo e-Civil.png")
        st.image(img)
        
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Analytics", "Setup", "Code", "Contact"],
            icons=["house", "graph-up", "gear", "code-slash", "envelope"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )

    if selected == "Home":
        st.title("🌡️ Temperature and Humidity Monitor")
        st.subheader("LabTag/UFPE Laboratory")

        df = fetch_data()

        col1, col2 = st.columns(2)

        with col1:
            current_temp = df['field1'].iloc[-1]
            st.metric("Current Temperature", f"{current_temp:.2f} °C", f"{current_temp - df['field1'].iloc[-2]:.2f} °C")
            fig_temp = create_plot(df, 'field1', 'Temperature over Time', 'Temperature (°C)', 'red')
            st.plotly_chart(fig_temp, use_container_width=True)

        with col2:
            current_humidity = df['field2'].iloc[-1]
            st.metric("Current Humidity", f"{current_humidity:.2f}%", f"{current_humidity - df['field2'].iloc[-2]:.2f}%")
            fig_humidity = create_plot(df, 'field2', 'Humidity over Time', 'Humidity (%)', 'blue')
            st.plotly_chart(fig_humidity, use_container_width=True)

        # Display first and last timestamps
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Data Range")
            first_timestamp = df['created_at'].iloc[0]
            last_timestamp = df['created_at'].iloc[-1]
            st.info(f"First Record: {first_timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC-3")
            st.info(f"Last Record: {last_timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC-3")
            days_passed = (last_timestamp - first_timestamp).days
            st.success(f"Total Measurement Interval: {days_passed} days")

        with col2:
            st.subheader("🌡️ Temperature Extremes")
            max_temp = df['field1'].max()
            min_temp = df['field1'].min()
            max_temp_time = df.loc[df['field1'].idxmax(), 'created_at']
            min_temp_time = df.loc[df['field1'].idxmin(), 'created_at']
            st.error(f"Maximum: {max_temp:.2f} °C, Recorded on {max_temp_time.strftime('%Y-%m-%d %H:%M:%S')} UTC-3")
            st.success(f"Minimum: {min_temp:.2f} °C, Recorded on {min_temp_time.strftime('%Y-%m-%d %H:%M:%S')} UTC-3")

    elif selected == "Analytics":
        st.title("📈 Advanced Analytics")
        df = fetch_data()

        # Temperature distribution
        fig_temp_dist = px.histogram(df, x='field1', nbins=30, title='Temperature Distribution')
        st.plotly_chart(fig_temp_dist, use_container_width=True)

        # Temperature heatmap
        fig_heatmap = create_heatmap(df)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Correlation between temperature and humidity
        fig_scatter = px.scatter(df, x='field1', y='field2', title='Temperature vs Humidity',
                                 labels={'field1': 'Temperature (°C)', 'field2': 'Humidity (%)'})
        st.plotly_chart(fig_scatter, use_container_width=True)

    elif selected == "Setup":
        st.title("🔧 Hardware Setup")
        st.subheader("Microcontroller and Sensor Details")
        st.image("setup_esp_dht22.png", use_column_width=True)
        st.write("This setup uses an ESP8266 microcontroller connected to a DHT22 temperature and humidity sensor.")

    elif selected == "Code":
        st.title("💻 Source Code")
        st.markdown("View the source code for this dashboard on GitHub:")
        st.markdown("[GitHub Repository](https://github.com/PM1980/dht22/blob/main/thingspeak_dashboard.py)")
        
        if st.button("Show Sample Code"):
            st.code("""
            def fetch_data():
                try:
                    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=15000"
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    df = pd.DataFrame(data['feeds'])
                    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
                    df['created_at'] = df['created_at'] + TZ_OFFSET
                    df['field1'] = pd.to_numeric(df['field1'], errors='coerce')
                    df['field2'] = pd.to_numeric(df['field2'], errors='coerce')
                    
                    return df.sort_values('created_at')
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    return pd.DataFrame()
            """, language="python")

    elif selected == "Contact":
        st.title("📬 Contact Us")
        st.write("Follow us on Instagram for updates and more information:")
        st.markdown("[Instagram: projeto_ecivil](https://www.instagram.com/projeto_ecivil/)")
        
        st.write("Or reach out to us directly:")
        contact_form = """
        <form action="https://formsubmit.co/YOUR_EMAIL_HERE" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Your name" required>
            <input type="email" name="email" placeholder="Your email" required>
            <textarea name="message" placeholder="Your message here"></textarea>
            <button type="submit">Send</button>
        </form>
        """
        st.markdown(contact_form, unsafe_allow_html=True)
        
        # Add custom CSS to make the form look nicer
        st.markdown("""
        <style>
        input[type=text], input[type=email], textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            margin-top: 6px;
            margin-bottom: 16px;
            resize: vertical;
        }
        button[type=submit] {
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button[type=submit]:hover {
            background-color: #45a049;
        }
        </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
