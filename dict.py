import pandas as pd
from collections import OrderedDict, Counter
from pathlib import Path

SOURCE = Path("Base de datos/INEGI_denue_62.csv")          # <- change to your file
OUT_JSON = Path("Base de datos/codigo_act_dict.json")        # optional: save mapping

def pick_col(cols, candidates):
    cols_lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None

# candidates for description column (DENUE/SCIAN often uses "Clase_actividad")
DESC_CANDIDATES = ["nombre_act"
]

codigo_to_desc = OrderedDict()
codigo_counts = Counter()

chunks = pd.read_csv(
    SOURCE,
    chunksize=200_000,
    low_memory=True,
    encoding="latin-1",  # DENUE commonly Latin-1
    sep=None,            # let pandas infer delimiter
    engine="python",
    dtype=str
)

for chunk in chunks:
    # normalize columns
    chunk.columns = [c.strip() for c in chunk.columns]
    codigo_col = pick_col(chunk.columns, ["codigo_act"])
    desc_col   = pick_col(chunk.columns, DESC_CANDIDATES)

    if not codigo_col:
        raise KeyError(f"Couldn't find 'codigo_act' in columns: {chunk.columns.tolist()}")

    # Use description if present; otherwise we’ll fill later with empty string
    cols_to_keep = [codigo_col] + ([desc_col] if desc_col else [])
    sub = chunk[cols_to_keep].dropna(subset=[codigo_col]).copy()
    sub[codigo_col] = sub[codigo_col].astype(str).str.strip()

    # update counts
    codigo_counts.update(sub[codigo_col])

    # update first-seen description per code
    if desc_col:
        sub[desc_col] = sub[desc_col].astype(str).str.strip()
        for code, desc in sub[[codigo_col, desc_col]].drop_duplicates().itertuples(index=False):
            if code and code not in codigo_to_desc and desc:
                codigo_to_desc[code] = desc

# merge into a single dict
codigo_dict = {}
all_codes = set(codigo_counts.keys()) | set(codigo_to_desc.keys())
for code in sorted(all_codes):
    codigo_dict[code] = {
        "name": codigo_to_desc.get(code, ""),  # may be blank if source lacks desc
        "count": int(codigo_counts.get(code, 0))
    }

# save (optional)
import json
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(codigo_dict, f, ensure_ascii=False, indent=2)

# quick peek
for k in list(codigo_dict.keys())[:10]:
    print(k, "→", codigo_dict[k])
