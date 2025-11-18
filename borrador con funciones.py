with open("diccionario.json", "r", encoding="utf-8") as f:
    original = json.load(f)

modificado = {}

for clave, datos in original.items():
    base_especialidad = clave.split("__")[0]
    sector = datos["sector"]
    codigo = datos["codigo"]

    modificado[clave] = datos

    if sector == "privado":
        nueva_clave = f"{base_especialidad}__público"

        if nueva_clave not in original:
            a = str(int(codigo)+1)
            modificado[nueva_clave] = {
                "codigo": a,
                "sector": "público"
            }

# guardar
out = "diccionario_v1.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(modificado, f, ensure_ascii=False, indent=2)

print(f"Diccionario con {len(modificado)} especialidades, '{out}'")


# para la verificaion previa de las claves de sector público y privado
# ver si las entradas del diccionario estan bien definidas

no_sector = []

for key, value in diccionario.items():
    sector = value.get("sector", "").lower()
    if "privado" not in sector and "público" not in sector:
        no_sector.append((key, sector))

if no_sector:
    print("Entradas sin 'privado' ni 'público' detectadas:\n")
    for term, text in no_sector:
        print(f" - {term}: '{text}'")
    print(f"\Total: {len(no_sector)} entradas necesitan revisión.")
else:
    print("0 entradas mal clasificadas.")