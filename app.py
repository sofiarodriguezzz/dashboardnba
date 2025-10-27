
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="NBA Dashboard (ELO dataset)", page_icon="🏀", layout="wide")
st.title("🏀 Dashboard NBA – Acumulado W/L por temporada y equipo (nba_all_elo.csv)")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Renombrar columnas del dataset 'nba_all_elo.csv' a nombres estándar
    df = df.rename(columns={
        "year_id": "season",
        "fran_id": "team",
        "date_game": "game_date"
    })

    # Tipos y limpieza
    df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce", format="%m/%d/%Y")
    df = df.dropna(subset=["game_date"])

    if "is_playoffs" in df.columns:
        df["is_playoffs"] = df["is_playoffs"].astype(int).astype(bool)
    else:
        df["is_playoffs"] = False

    df["game_result"] = df["game_result"].astype(str).upper().str.strip()
    df = df[df["game_result"].isin(["W", "L"])]

    if "gameorder" in df.columns:
        df = df.sort_values(["game_date", "gameorder"])
    else:
        df = df.sort_values("game_date")

    return df

DATA_PATH = Path("data") / "nba_all_elo.csv"
df = load_data(str(DATA_PATH))

# --------- Sidebar ---------
st.sidebar.header("Filtros")
years = sorted(df["season"].unique().tolist())
year = st.sidebar.selectbox("Año (season)", years, index=years.index(max(years)) if years else 0)
teams_in_year = sorted(df.loc[df["season"] == year, "team"].unique().tolist())
team = st.sidebar.selectbox("Equipo (franquicia)", teams_in_year, index=0 if teams_in_year else None)

try:
    choice = st.pills("Tipo de juegos", ["Ambos", "Temporada regular", "Playoffs"], selection_mode="single")
except Exception:
    choice = st.radio("Tipo de juegos", ["Ambos", "Temporada regular", "Playoffs"], index=0)

# --------- Filtrado ---------
subset = df[(df["season"] == year) & (df["team"] == team)].copy()
if choice == "Temporada regular":
    subset = subset[subset["is_playoffs"] == False]
elif choice == "Playoffs":
    subset = subset[subset["is_playoffs"] == True]
subset = subset.sort_values(["game_date", "gameorder"] if "gameorder" in subset.columns else "game_date")

# --------- Acumulados ---------
subset["win"] = (subset["game_result"] == "W").astype(int)
subset["loss"] = (subset["game_result"] == "L").astype(int)
subset["cum_wins"] = subset["win"].cumsum()
subset["cum_losses"] = subset["loss"].cumsum()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Acumulado W/L – {team} · {year}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=subset["game_date"], y=subset["cum_wins"], mode="lines+markers", name="Ganados (acumulado)"))
    fig.add_trace(go.Scatter(x=subset["game_date"], y=subset["cum_losses"], mode="lines+markers", name="Perdidos (acumulado)"))
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Juegos acumulados",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=30, b=20),
        height=520
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Porcentaje de la temporada")
    wins = int(subset["win"].sum())
    losses = int(subset["loss"].sum())
    pie = go.Figure(data=[go.Pie(labels=["Ganados", "Perdidos"], values=[wins, losses], hole=0.35)])
    pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=520)
    st.plotly_chart(pie, use_container_width=True)

st.divider()
c1, c2, c3 = st.columns(3)
total = wins + losses
pct = (wins / total * 100) if total > 0 else 0
c1.metric("Total de juegos", f"{total}")
c2.metric("Ganados", f"{wins}")
c3.metric("Win %", f"{pct:.1f}%")

with st.expander("Ver tabla de juegos"):
    cols = ["game_date", "team", "game_result", "is_playoffs", "pts", "opp_fran", "opp_pts"]
    cols = [c for c in cols if c in subset.columns]
    st.dataframe(subset[cols], use_container_width=True)
