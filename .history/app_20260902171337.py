"""Dashboard interactivo de finanzas de hogares colombianos."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(__file__).with_name("finanzas_hogar.csv")
MONEY = ["Ingreso_Mensual", "Gasto_Alimentacion", "Gasto_Educacion", "Ahorro_Mensual"]
COLOR = {"navy": "#13213C", "blue": "#2878FF", "cyan": "#36C5F0", "green": "#19B394", "amber": "#F6AD55", "red": "#F0656B"}

st.set_page_config(page_title="Finanzas de los hogares | Colombia", page_icon="🇨🇴", layout="wide")


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    """Carga y valida los datos, y calcula indicadores financieros."""
    data = pd.read_csv(path, encoding="utf-8")
    required = {"ID", "Departamento", "Latitud", "Longitud", *MONEY}
    if missing := required.difference(data.columns):
        raise ValueError(f"Faltan columnas: {', '.join(sorted(missing))}")
    data = data.drop_duplicates("ID").copy()
    data["Gasto_Esencial"] = data["Gasto_Alimentacion"] + data["Gasto_Educacion"]
    data["Balance_Disponible"] = data["Ingreso_Mensual"] - data["Gasto_Esencial"]
    data["Tasa_Ahorro"] = data["Ahorro_Mensual"] / data["Ingreso_Mensual"] * 100
    data["Carga_Gastos"] = data["Gasto_Esencial"] / data["Ingreso_Mensual"] * 100
    data["Segmento_Ingreso"] = pd.qcut(data["Ingreso_Mensual"], 4, labels=["Bajo", "Medio-bajo", "Medio-alto", "Alto"])
    return data


def cop(value: float, compact: bool = False) -> str:
    if compact:
        return f"${value / 1_000_000:,.2f} M".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"${value:,.0f}".replace(",", ".")


def polish(fig: go.Figure, height: int = 410) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=20, r=20, t=65, b=25), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, Arial", color=COLOR["navy"]),
        title_font_size=19, legend=dict(orientation="h", y=1.02, x=1, xanchor="right"),
        hoverlabel=dict(bgcolor="white", font_size=13),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(102,112,133,.14)", zeroline=False)
    return fig


def card(label: str, value: str, note: str, tone: str) -> None:
    st.markdown(f"<div class='metric-card {tone}'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note'>{note}</div></div>", unsafe_allow_html=True)


def insights(data: pd.DataFrame) -> None:
    regional = data.groupby("Departamento").agg(tasa=("Tasa_Ahorro", "mean"), carga=("Carga_Gastos", "mean"))
    correlation = data["Ingreso_Mensual"].corr(data["Ahorro_Mensual"])
    over_budget = (data["Gasto_Esencial"] + data["Ahorro_Mensual"] > data["Ingreso_Mensual"]).mean() * 100
    items = [
        ("🏆", "Mayor tasa de ahorro", regional["tasa"].idxmax(), f"{regional['tasa'].max():.1f}% promedio"),
        ("⚠️", "Mayor carga de gastos", regional["carga"].idxmax(), f"{regional['carga'].max():.1f}% del ingreso"),
        ("🔗", "Ingreso vs. ahorro", f"r = {correlation:.2f}", "Correlación lineal"),
        ("🧭", "Presupuesto exigido", f"{over_budget:.1f}%", "Gastos + ahorro superan ingreso"),
    ]
    st.markdown("### Insights del filtro actual")
    for col, (icon, title, value, detail) in zip(st.columns(4), items):
        with col:
            st.markdown(f"<div class='insight-card'><span>{icon}</span><div class='insight-title'>{title}</div><div class='insight-value'>{value}</div><div class='insight-detail'>{detail}</div></div>", unsafe_allow_html=True)


st.markdown("""
<style>
.stApp{background:#F6F8FC}[data-testid="stSidebar"]{background:#13213C}[data-testid="stSidebar"] *{color:#F8FAFC}.block-container{padding-top:2rem;max-width:1500px}
h1,h2,h3{color:#13213C;letter-spacing:-.02em}.hero{background:linear-gradient(125deg,#13213C,#1E3B67 65%,#2878FF 130%);padding:2rem 2.2rem;border-radius:20px;color:white;margin-bottom:1.4rem;box-shadow:0 12px 35px #13213c22}.hero h1{color:white;margin:.25rem 0}.hero p{color:#D7E3F4;margin:0}.eyebrow{color:#62A0FF;font-size:.78rem;font-weight:800;letter-spacing:.13em}
.metric-card{background:white;border-radius:15px;padding:1.15rem 1.25rem;border-top:4px solid #2878FF;min-height:128px;box-shadow:0 5px 18px #13213c0f}.metric-card.green{border-color:#19B394}.metric-card.amber{border-color:#F6AD55}.metric-card.cyan{border-color:#36C5F0}.metric-label,.insight-title{color:#667085;font-size:.78rem;font-weight:700;text-transform:uppercase}.metric-value{color:#13213C;font-size:1.7rem;font-weight:800;margin:.25rem 0}.metric-note,.insight-detail{color:#8490A3;font-size:.79rem}
.insight-card{background:white;padding:1rem 1.1rem;border:1px solid #E7ECF3;border-radius:14px;min-height:145px}.insight-title{margin-top:.5rem}.insight-value{color:#13213C;font-size:1.12rem;font-weight:800;margin:.2rem 0}div[data-testid="stPlotlyChart"]{background:white;border:1px solid #E7ECF3;border-radius:16px;padding:.35rem}
</style>""", unsafe_allow_html=True)

try:
    df = load_data(DATA_PATH)
except (FileNotFoundError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"No fue posible cargar el dataset: {exc}")
    st.stop()

with st.sidebar:
    st.markdown("## 🇨🇴 FINANZAS")
    st.caption("Household Intelligence")
    st.divider()
    page = st.radio("Navegación", ["Resumen ejecutivo", "Análisis financiero", "Mapa regional", "Explorar datos"])
    st.divider()
    st.markdown("#### Filtros")
    departments = st.multiselect("Departamentos", sorted(df["Departamento"].unique()), placeholder="Todos")
    min_income, max_income = int(df["Ingreso_Mensual"].min()), int(df["Ingreso_Mensual"].max())
    income = st.slider("Ingreso mensual", min_income, max_income, (min_income, max_income), step=100_000, format="$%d")
    st.caption("Los filtros afectan todas las páginas.")

filtered = df[df["Ingreso_Mensual"].between(*income)].copy()
if departments:
    filtered = filtered[filtered["Departamento"].isin(departments)]
if filtered.empty:
    st.warning("No hay hogares que coincidan con los filtros.")
    st.stop()

st.markdown(f"<div class='hero'><div class='eyebrow'>MIDIENDO LA REALIDAD CON DATOS</div><h1>Finanzas de los hogares colombianos</h1><p>Ingresos, gastos y capacidad de ahorro de {len(filtered)} hogares de la muestra.</p></div>", unsafe_allow_html=True)

if page == "Resumen ejecutivo":
    values = [
        ("Ingreso promedio", cop(filtered.Ingreso_Mensual.mean(), True), f"Mediana: {cop(filtered.Ingreso_Mensual.median(), True)}", "blue"),
        ("Ahorro promedio", cop(filtered.Ahorro_Mensual.mean(), True), f"{filtered.Tasa_Ahorro.mean():.1f}% del ingreso", "green"),
        ("Gasto esencial", cop(filtered.Gasto_Esencial.mean(), True), "Alimentación + educación", "amber"),
        ("Balance disponible", cop(filtered.Balance_Disponible.mean(), True), "Ingreso menos gastos", "cyan"),
    ]
    for col, args in zip(st.columns(4), values):
        with col: card(*args)
    st.write("")
    left, right = st.columns((1.25, 1))
    summary = filtered.groupby("Departamento").agg(Ingreso=("Ingreso_Mensual", "mean"), Ahorro=("Ahorro_Mensual", "mean"), Hogares=("ID", "count")).reset_index().sort_values("Ingreso")
    with left:
        fig = px.bar(summary, x="Ingreso", y="Departamento", orientation="h", color="Ahorro", color_continuous_scale=["#DDEAFE", COLOR["blue"]], title="Ingreso y ahorro promedio por departamento", custom_data=["Ahorro", "Hogares"])
        fig.update_traces(hovertemplate="<b>%{y}</b><br>Ingreso: $%{x:,.0f}<br>Ahorro: $%{customdata[0]:,.0f}<br>Hogares: %{customdata[1]}<extra></extra>")
        st.plotly_chart(polish(fig), use_container_width=True)
    with right:
        composition = pd.DataFrame({"Categoría": ["Alimentación", "Educación", "Ahorro"], "Valor": [filtered.Gasto_Alimentacion.mean(), filtered.Gasto_Educacion.mean(), filtered.Ahorro_Mensual.mean()]})
        fig = px.pie(composition, values="Valor", names="Categoría", hole=.62, color="Categoría", color_discrete_map={"Alimentación": COLOR["amber"], "Educación": COLOR["cyan"], "Ahorro": COLOR["green"]}, title="Asignación financiera promedio")
        fig.update_traces(textposition="outside", textinfo="percent+label", hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<extra></extra>")
        st.plotly_chart(polish(fig), use_container_width=True)
    insights(filtered)

elif page == "Análisis financiero":
    tab1, tab2, tab3 = st.tabs(["Distribuciones", "Relaciones", "Segmentos"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(filtered, x="Ingreso_Mensual", nbins=22, marginal="box", color_discrete_sequence=[COLOR["blue"]], title="Distribución del ingreso mensual")
            fig.update_traces(hovertemplate="Ingreso: $%{x:,.0f}<br>Hogares: %{y}<extra></extra>")
            st.plotly_chart(polish(fig), use_container_width=True)
        with c2:
            long = filtered.melt(id_vars="ID", value_vars=["Gasto_Alimentacion", "Gasto_Educacion", "Ahorro_Mensual"], var_name="Categoría", value_name="Valor")
            long["Categoría"] = long["Categoría"].map({"Gasto_Alimentacion": "Alimentación", "Gasto_Educacion": "Educación", "Ahorro_Mensual": "Ahorro"})
            fig = px.box(long, x="Categoría", y="Valor", color="Categoría", color_discrete_sequence=[COLOR["amber"], COLOR["cyan"], COLOR["green"]], title="Variabilidad de gastos y ahorro")
            st.plotly_chart(polish(fig), use_container_width=True)
    with tab2:
        c1, c2 = st.columns((1.2, 1))
        with c1:
            fig = px.scatter(filtered, x="Ingreso_Mensual", y="Ahorro_Mensual", color="Departamento", size="Gasto_Esencial", opacity=.72, title="Relación entre ingreso y ahorro", hover_name="Departamento")
            fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Ingreso: $%{x:,.0f}<br>Ahorro: $%{y:,.0f}<extra></extra>")
            st.plotly_chart(polish(fig, 470), use_container_width=True)
        with c2:
            corr = filtered[MONEY + ["Gasto_Esencial", "Tasa_Ahorro"]].corr()
            labels = ["Ingreso", "Alimentación", "Educación", "Ahorro", "Gasto esencial", "Tasa ahorro"]
            fig = px.imshow(corr, x=labels, y=labels, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale=[COLOR["red"], "white", COLOR["blue"]], title="Matriz de correlaciones")
            st.plotly_chart(polish(fig, 470), use_container_width=True)
    with tab3:
        segment = filtered.groupby("Segmento_Ingreso", observed=True).agg(Alimentación=("Gasto_Alimentacion", "mean"), Educación=("Gasto_Educacion", "mean"), Ahorro=("Ahorro_Mensual", "mean")).reset_index()
        long = segment.melt("Segmento_Ingreso", var_name="Categoría", value_name="Valor")
        fig = px.bar(long, x="Segmento_Ingreso", y="Valor", color="Categoría", barmode="group", color_discrete_map={"Alimentación": COLOR["amber"], "Educación": COLOR["cyan"], "Ahorro": COLOR["green"]}, title="Perfil financiero por cuartil de ingreso")
        st.plotly_chart(polish(fig, 480), use_container_width=True)
        st.caption("Los segmentos se calculan sobre la muestra completa para permitir comparaciones consistentes.")

elif page == "Mapa regional":
    regional = filtered.groupby("Departamento").agg(Latitud=("Latitud", "mean"), Longitud=("Longitud", "mean"), Ingreso=("Ingreso_Mensual", "mean"), Ahorro=("Ahorro_Mensual", "mean"), Alimentación=("Gasto_Alimentacion", "mean"), Tasa_Ahorro=("Tasa_Ahorro", "mean"), Hogares=("ID", "count")).reset_index()
    metric = st.selectbox("Indicador", ["Ingreso", "Ahorro", "Alimentación", "Tasa_Ahorro"], format_func=lambda x: x.replace("_", " "))
    fig = px.scatter_map(regional, lat="Latitud", lon="Longitud", size="Hogares", color=metric, hover_name="Departamento", custom_data=["Ingreso", "Ahorro", "Alimentación", "Tasa_Ahorro", "Hogares"], color_continuous_scale=["#DDEAFE", COLOR["blue"]], size_max=34, zoom=4.2, center={"lat": 4.6, "lon": -74.3}, map_style="carto-positron", title="Panorama financiero regional")
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Ingreso: $%{customdata[0]:,.0f}<br>Ahorro: $%{customdata[1]:,.0f}<br>Alimentación: $%{customdata[2]:,.0f}<br>Tasa de ahorro: %{customdata[3]:.1f}%<br>Hogares: %{customdata[4]}<extra></extra>")
    st.plotly_chart(polish(fig, 620), use_container_width=True)
    st.info("El tamaño representa el número de hogares y el color, el indicador seleccionado. Las ubicaciones son referencias departamentales del dataset.")

else:
    st.markdown("### Explorador de datos")
    for col, (name, value) in zip(st.columns(4), [("Filas", len(filtered)), ("Departamentos", filtered.Departamento.nunique()), ("Datos faltantes", filtered.isna().sum().sum()), ("IDs duplicados", filtered.ID.duplicated().sum())]):
        col.metric(name, int(value))
    display = ["ID", "Departamento", *MONEY, "Gasto_Esencial", "Balance_Disponible", "Tasa_Ahorro"]
    formats = {column: "${:,.0f}" for column in MONEY + ["Gasto_Esencial", "Balance_Disponible"]} | {"Tasa_Ahorro": "{:.1f}%"}
    st.dataframe(filtered[display].style.format(formats), use_container_width=True, hide_index=True, height=480)
    st.download_button("Descargar datos filtrados (.csv)", filtered.to_csv(index=False).encode("utf-8-sig"), "finanzas_hogares_filtrado.csv", "text/csv", type="primary")

st.divider()
st.caption("Análisis descriptivo sobre una muestra de 200 hogares · Valores en COP · Python, Streamlit y Plotly")
