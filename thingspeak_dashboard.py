import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
from pytz import UTC
from PIL import Image
from streamlit_option_menu import option_menu
from plotly.subplots import make_subplots

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
    fig = make_subplots(rows=1, cols=1, subplot_titles=[title])
    
    fig.add_trace(
        go.Scatter(
            x=df['created_at'], 
            y=df[y_col], 
            mode='lines', 
            name=y_label, 
            line=dict(color=color, width=2),
            fill='tozeroy'
        )
    )
    
    fig.update_layout(
        height=400,  # Set a fixed height
        margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins
        xaxis_title='Time (UTC-3)',
        yaxis_title=y_label,
        font=dict(family="Arial", size=12, color='white'),
        plot_bgcolor='black',
        paper_bgcolor='black',
        xaxis=dict(showgrid=True, gridcolor='grey', linecolor='white'),
        yaxis=dict(showgrid=True, gridcolor='grey', linecolor='white'),
    )
    
    return fig

def create_heatmap(df):
    fig = px.density_heatmap(
        df, 
        x='created_at', 
        y='field1', 
        title='Temperature Heatmap',
        labels={'created_at': 'Time', 'field1': 'Temperature (°C)'},
        color_continuous_scale='Viridis',
        height=400
    )
    fig.update_layout(
        margin=dict(l=50, r=50, t=50, b=50),
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )
    return fig

def main():
    st.set_page_config(page_title="Enhanced ThingSpeak Dashboard", layout="wide", initial_sidebar_state="expanded")

    # Custom CSS to apply dark theme
    st.markdown("""
        <style>
        .stApp {
            background-color: #1e1e1e;
            color: white;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        .stProgress .st-bo {
            background-color: #4CAF50;
        }
        .css-17eq0hr a {
            color: white;
        }
        .css-1v3fvcr {
            background-color: #333;
            color: white;
        }
        .css-1v3fvcr a {
            color: white;
        }
        .css-1v3fvcr .css-qbe2hs {
            color: white;
        }
        .css-1v3fvcr .css-qbe2hs a {
            color: white;
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
                "container": {"padding": "5!important", "background-color": "#333"},
                "icon": {"color": "orange", "font-size": "25px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#444"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )

    if selected == "Home":
        st.title("🌡️ Temperature and Humidity Monitor")
        st.subheader("LabTag/UFPE Laboratory")

        df = fetch_data()

        if not df.empty:
            col1, col2 = st.columns(2)

            with col1:
                current_temp = df['field1'].iloc[-1]
                st.metric("Current Temperature", f"{current_temp:.2f} °C", f"{current_temp - df['field1'].iloc[-2]:.2f} °C")
                fig_temp = create_plot(df, 'field1', '', 'Temperature (°C)', 'red')
                st.plotly_chart(fig_temp, use_container_width=True, config={'displayModeBar': False})

            with col2:
                current_humidity = df['field2'].iloc[-1]
                st.metric("Current Humidity", f"{current_humidity:.2f}%", f"{current_humidity - df['field2'].iloc[-2]:.2f}%")
                fig_humidity = create_plot(df, 'field2', '', 'Humidity (%)', 'blue')
                st.plotly_chart(fig_humidity, use_container_width=True, config={'displayModeBar': False})

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
        else:
            st.error("No data available. Please check your ThingSpeak connection.")

    elif selected == "Analytics":
        st.title("📈 Advanced Analytics")
        df = fetch_data()

        if not df.empty:
            # Temperature distribution
            fig_temp_dist = px.histogram(df, x='field1', nbins=30, title='Temperature Distribution', height=400)
            fig_temp_dist.update_layout(
                margin=dict(l=50, r=50, t=50, b=50),
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white')
            )
            st.plotly_chart(fig_temp_dist, use_container_width=True, config={'displayModeBar': False})

            # Temperature heatmap
            fig_heatmap = create_heatmap(df)
            st.plotly_chart(fig_heatmap, use_container_width=True, config={'displayModeBar': False})

            # Correlation between temperature and humidity
            fig_scatter = px.scatter(
                df, 
                x='field1', 
                y='field2', 
                title='Temperature vs Humidity',
                labels={'field1': 'Temperature (°C)', 'field2': 'Humidity (%)'},
                height=400
            )
            fig_scatter.update_layout(
                margin=dict(l=50, r=50, t=50, b=50),
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white')
            )
            st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
        else:
            st.error("No data available for analytics. Please check your ThingSpeak connection.")

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
            background-color: #333;
            color: white;
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
