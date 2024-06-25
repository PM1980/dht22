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

    elif selected == "Warehouse":
        st.subheader(f"**You Have selected {selected}**")
        # Snowflake connection and querying would go here

    elif selected == "Contato":
        st.subheader(f"**Informações para contato e redes sociais**")
        st.markdown("https://www.instagram.com/projeto_ecivil/")
        # Contact form or information would go here

if __name__ == "__main__":
    main()
