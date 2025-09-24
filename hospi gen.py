import overpy

api = overpy.Overpass()

query = """
[out:json][timeout:60];
(
  node["amenity"="hospital"](19.0,-99.35,19.7,-98.9);
  node["amenity"="clinic"](19.0,-99.35,19.7,-98.9);
  node["amenity"="dentist"](19.0,-99.35,19.7,-98.9);
);
out body;
"""
result = api.query(query)

locations = []
for node in result.nodes:
    locations.append({
        "nombre": node.tags.get("name", "Unnamed"),
        "tipo": node.tags.get("amenity"),
        "lat": node.lat,
        "lon": node.lon
    })

import pandas as pd
clinics_df = pd.DataFrame(locations)
clinics_df.to_csv("Base de datos/Hospiclin_CDMX.csv", index=False)
print("listo pa'")

