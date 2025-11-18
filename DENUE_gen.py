import pandas as pd
from pathlib import Path
from collections import Counter

SOURCE = Path("Base de datos/INEGI_denue_62.csv")  
OUT_DIR = Path("Base de datos/denue_by_codigo")
OUT_DIR.mkdir(exist_ok=True, parents=True)

def pick_column(cols, candidates):
    cols_lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None

codes_counter = Counter()
first_write = {}  

chunks = pd.read_csv(
    SOURCE,
    chunksize=200_000,
    low_memory=True,
    encoding="latin-1",
    sep=None,          
    engine="python",
    dtype=str
)

for i, chunk in enumerate(chunks, start=1):
    chunk.columns = [c.strip() for c in chunk.columns]

    nom_estab   = pick_column(chunk.columns, ["nom_estab"])
    codigo_act = pick_column(chunk.columns, ["codigo_act"])
    nom_act   = pick_column(chunk.columns, ["nombre_act"])
    alcaldia    = pick_column(chunk.columns, ["alcaldia"])
    lat    = pick_column(chunk.columns, ["latitud"])
    lon    = pick_column(chunk.columns, ["longitud"])

    if not all([codigo_act, nom_act, lat, lon]):
        raise KeyError("Missing required columns in chunk. Found columns: " + ", ".join(chunk.columns))

    sub = chunk[[nom_estab, codigo_act, nom_act, alcaldia, lat, lon] ]
    sub.columns = ["nom_estab","codigo_act", "nom_act", "alcaldia", "lat", "lon"]
    sub["lat"] = pd.to_numeric(sub["lat"], errors="coerce")
    sub["lon"] = pd.to_numeric(sub["lon"], errors="coerce")
    sub = sub.dropna(subset=["lat","lon"])
    sub["codigo_act"] = sub["codigo_act"].str.strip()

    sub = sub[sub["codigo_act"].notna() & (sub["codigo_act"] != "")]

    for code, group in sub.groupby("codigo_act"):
        out_file = OUT_DIR / f"{code}.csv"
        mode = "w" if first_write.get(code, True) else "a"
        header = first_write.get(code, True)
        group.to_csv(out_file, index=False, encoding="utf-8", mode=mode, header=header)
        first_write[code] = False
        codes_counter[code] += len(group)

idx = pd.DataFrame(sorted(codes_counter.items()), columns=["codigo","cantidad"])
idx.to_csv(OUT_DIR / "_index_by_codigo.csv", index=False, encoding="utf-8")
idx.head(10)
