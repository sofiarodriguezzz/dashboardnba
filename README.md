
# NBA Dashboard (Streamlit)

Dashboard de Streamlit que muestra el acumulado de victorias/derrotas por **temporada** y **franquicia** usando el dataset `nba_all_elo.csv`.

## Estructura
```
nba-dashboard/
├─ app.py
├─ requirements.txt
└─ data/
   └─ nba_all_elo.csv
```

## Ejecutar local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Community Cloud
1. Sube este repo a GitHub.
2. En https://share.streamlit.io/ crea una nueva app.
3. Selecciona tu repo, rama `main` y archivo principal `app.py`.
4. Deploy.
