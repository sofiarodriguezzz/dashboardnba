#Huerta Rodríguez Sofía
#Martínez Salinas Emiliano 5AM1

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(page_title="Dashboard de la NBA", layout="wide")

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path)
    df["date_game"]= pd.to_datetime(df["date_game"])
    df["is_playoffs"] = pd.to_numeric(df["is_playoffs"], errors="coerce").fillna(0).astype(int)
    return df                             

df = cargar_datos("nba_all_elo.csv")
st.title ("Visualización de estadísticas históricas de la NBA")

#Barra lateral
st.sidebar.header("Filtrar por")
years = sorted(df["year_id"].unique().tolist())
year= st.sidebar.selectbox("Selecciona el año", years, index=len(years)-1)


#Equipos dependiendo del año
if "team_id" in df.columns:
    equipos_disponibles = df[df["year_id"] == year]["team_id"].unique()
else:
    equipos_disponibles = df[df["year_id"] == year]["fran_id"].unique()
    
equipos_disponibles = sorted(equipos_disponibles)
equipo = st.sidebar.selectbox("Selecciona un equipo", equipos_disponibles)
tipos_juego = ["Temporada regular", "Playoffs", "Ambos"]
modo = st.sidebar.radio("Tipo de juegos", tipos_juego, index=0)
    

#Filtrar por
mask_base = (df["year_id"] == year) & ((df["team_id"] == equipo) if "team_id" in df.columns else (df["fran_id"] == equipo))
if modo == "Temporada regular":
    mask = mask_base&(df["is_playoffs"] == 0)
elif modo == "Playoffs":
    mask = mask_base&(df["is_playoffs"] == 1)
else:
    mask = mask_base
base = df.loc[mask].sort_values("date_game").copy()

#En caso de que no haya datos
if base.empty:
    st.warning("No hay juegos disponibles :(")
    st.stop()

#Acumulados W/L
base["win_flag"] = (base["game_result"] == "W").astype(int)
base["loss_flag"] = (base["game_result"] == "L").astype(int)
base["Wins_cum"] = base["win_flag"].cumsum()
base["Losses_cum"] = base["loss_flag"].cumsum()

columna1,columna2 = st.columns([2,1], gap="large")

with columna1:
    st.subheader("Acumulado de juegos ganados y perdidos")
    fig1 = plt.figure(figsize=(10,4))
    plt.plot(base["date_game"], base["Wins_cum"], label="Ganados", linewidth=2)
    plt.plot(base["date_game"], base["Losses_cum"], label="Perdidos", linewidth=2)
    plt.xlabel("Fecha del juego"); plt.ylabel("Acumulado"); plt.legend(); plt.tight_layout()
    st.pyplot(fig1)

with columna2:
    st.subheader("Porcentaje de juegos ganados y perdidos")
    wins = int(base["win_flag"].sum())
    losses = int(base["loss_flag"].sum())
    total = wins + losses
    st.metric("Total de juegos", total)

    if total == 0:
        st.info("No hay juegos para graficar :(")
    else:
        fig2 = plt.figure(figsize=(4,4))
        plt.pie([wins, losses], labels=["Ganados", "Perdidos"], autopct="%1.1f%%", startangle=90)
        plt.axis("equal")
        st.pyplot(fig2)
    




