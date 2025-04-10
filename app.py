
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Cargar los datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("finanzas_hogar.csv")

df = cargar_datos()

# Menú de navegación
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["Inicio", "Análisis", "Mapa"])


# Página 1: Inicio
if opcion == "Inicio":
    st.title("App de Finanzas del Hogar")
    st.image("https://cdn-icons-png.flaticon.com/512/3448/3448537.png", width=150)
    st.write("""
        Esta app analiza datos sobre finanzas del hogar en Colombia.
        Puedes explorar estadísticas y un mapa interactivo por departamentos.
    """)


# Página 2: Análisis



# Página 2: Análisis
elif opcion == "Análisis":
    st.title("📊 Análisis de Datos")

    

    if 'Departamento' in df.columns:
        st.subheader("Conteo de registros por Departamento")
        conteo = df['Departamento'].value_counts().reset_index()
        conteo.columns = ['Departamento', 'Cantidad']
        fig = px.bar(
            conteo, 
            x='Departamento', 
            y='Cantidad', 
            color='Cantidad',
            title='Número de registros por departamento',
            labels={'Cantidad': 'Número de registros', 'Departamento': 'Departamento'}
        )
        st.plotly_chart(fig)
     # Histograma del gasto en alimentación con estilo
    if 'Gasto_Alimentacion' in df.columns:
        st.subheader("Distribución del Gasto en Alimentación")
        fig3 = px.histogram(
            df,
            x='Gasto_Alimentacion',
            nbins=30,
            title="Distribución del Gasto en Alimentación",
            color_discrete_sequence=['#4a90e2'],  # Azul bonito
            opacity=0.8
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Gasto en Alimentación",
            yaxis_title="Frecuencia",
            title_font_size=20
        )
        st.plotly_chart(fig3)





# Página 3: Mapa

elif opcion == "Mapa":
    st.title("Mapa Interactivo")
    st.markdown("Este mapa muestra el gasto promedio en alimentación por hogar en cada departamento de Colombia, basado en las coordenadas del dataset.")
    
    
    
    # Agrupar por departamento para obtener la media del gasto
    gasto_departamento = df.groupby('Departamento')['Gasto_Alimentacion'].mean().reset_index()

    # Coordenadas promedio por departamento
    coordenadas = df.groupby('Departamento')[['Latitud', 'Longitud']].mean().reset_index()

    # Unir gasto con coordenadas
    df_mapa = pd.merge(gasto_departamento, coordenadas, on='Departamento')

    # Crear el mapa centrado en Colombia
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=5)

    # Añadir círculos por departamento
    for i, row in df_mapa.iterrows():
        folium.CircleMarker(
            location=[row['Latitud'], row['Longitud']],
            radius=8,
            popup=folium.Popup(f"{row['Departamento']}<br>Gasto promedio: ${row['Gasto_Alimentacion']:.2f}", max_width=200),
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6
        ).add_to(m)

    # Mostrar el mapa en Streamlit
    st_folium(m, width=700, height=500)

