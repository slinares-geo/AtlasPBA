import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
APP_DIR = ROOT / "03_Tableros" / "01_MapaElectoral_0106"
OUT_DIR = APP_DIR / "docs"

SOURCES = {
    "2023": ROOT / "02_Datos" / "01_DINE" / "01_2023" / "presentacionDeResultados_presidenciales_2023.csv",
    "2025": ROOT / "02_Datos" / "01_DINE" / "02_2025" / "presentacionDeResultados_Diputados_2025.csv",
}

GEOJSON = ROOT / "02_Datos" / "02_Poblaciones 2023" / "04_DepartamentosElecciones.geojson"
CIRCUIT_GEOJSON = ROOT / "02_Datos" / "03_circuitoselectoralespba" / "circuitos-electorales-pba.geojson"
XLS_2025 = ROOT / "02_Datos" / "01_DINE" / "02_2025" / "Libro3_normalizado_mapas.xls"
DICT_XLSX = (
    ROOT
    / "02_Datos"
    / "02_Poblaciones 2023"
    / "Departamentos - Elecciones presidenciales 2023 (generales y balotaje) - Diccionario de datos.xlsx"
)


def as_int(value):
    try:
        if value is None or value == "":
            return 0
        return int(float(str(value).replace(",", ".")))
    except ValueError:
        return 0


def norm_text(value):
    return (value or "").strip()


def norm_name(value):
    text = norm_text(value).upper()
    text = text.replace("Ñ", "N")
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    aliases = {
        "A GONZALES CHAVES": "ADOLFO GONZALES CHAVES",
        "CA UELAS": "CANUELAS",
        "CNEL DE MARINA L ROSALES": "CORONEL DE MARINA L ROSALES",
        "9 DE JULIO": "NUEVE DE JULIO",
        "25 DE MAYO": "VEINTICINCO DE MAYO",
        "CORONEL ROSALES": "CORONEL DE MARINA L ROSALES",
        "GENERAL LAMADRID": "GENERAL LA MADRID",
    }
    return aliases.get(text, text)


def norm_circuit(value):
    text = norm_text(value).upper()
    if re.fullmatch(r"\d+", text):
        return str(int(text))
    match = re.fullmatch(r"0*(\d+)([A-Z]+)", text)
    if match:
        return f"{int(match.group(1))}{match.group(2)}"
    return text.lstrip("0") or text


def mesa_key(row):
    return (
        norm_text(row.get("distrito_id")),
        norm_text(row.get("seccion_id")),
        norm_text(row.get("circuito_id")),
        norm_text(row.get("mesa_id")),
        norm_text(row.get("mesa_tipo")),
    )


def circuit_key(row):
    return (
        norm_text(row.get("distrito_id")),
        norm_text(row.get("seccion_id")),
        norm_text(row.get("circuito_id")),
    )


def circuit_name_key(row):
    return (
        norm_name(row.get("seccion_nombre")),
        norm_circuit(row.get("circuito_id")),
    )


def inspect_csv(path):
    counters = {
        "eleccion_tipo": Counter(),
        "cargo_nombre": Counter(),
        "votos_tipo": Counter(),
        "estado_final": Counter(),
        "agrupacion_nombre": Counter(),
        "seccion_nombre": Counter(),
    }
    circuits = set()
    circuits_by_name = set()
    sections = set()
    mesas = {}
    votes_by_type = Counter()
    positive_by_group = Counter()
    sample_rows = []
    row_count = 0
    total_votes = 0

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        for row in reader:
            row_count += 1
            if len(sample_rows) < 3:
                sample_rows.append({key: row.get(key, "") for key in columns[:10]})

            for field, counter in counters.items():
                counter[norm_text(row.get(field))] += 1

            sections.add((norm_text(row.get("distrito_id")), norm_text(row.get("seccion_id"))))
            circuits.add(circuit_key(row))
            circuits_by_name.add(circuit_name_key(row))

            key = mesa_key(row)
            electors = as_int(row.get("mesa_electores"))
            if key not in mesas:
                mesas[key] = electors
            elif electors and mesas[key] != electors:
                mesas[key] = max(mesas[key], electors)

            votes = as_int(row.get("votos_cantidad"))
            total_votes += votes
            vote_type = norm_text(row.get("votos_tipo")) or "SIN_TIPO"
            votes_by_type[vote_type] += votes

            if vote_type == "POSITIVO":
                group = norm_text(row.get("agrupacion_nombre")) or "SIN_AGRUPACION"
                positive_by_group[group] += votes

    electors_total = sum(mesas.values())
    turnout = total_votes / electors_total if electors_total else None

    return {
        "path": str(path.relative_to(ROOT)),
        "size_mb": round(path.stat().st_size / 1024 / 1024, 2),
        "columns": columns,
        "row_count": row_count,
        "sample_rows": sample_rows,
        "sections_count": len(sections),
        "circuits_count": len(circuits),
        "mesas_count": len(mesas),
        "electors_total_from_unique_mesas": electors_total,
        "votes_total_from_rows": total_votes,
        "turnout_estimate": turnout,
        "votes_by_type": dict(votes_by_type.most_common()),
        "positive_by_group_top": dict(positive_by_group.most_common(20)),
        "counters": {key: dict(counter.most_common(20)) for key, counter in counters.items()},
        "keys": {
            "sections": sorted(list(sections)),
            "circuits": sorted(list(circuits)),
            "circuits_by_name": sorted(list(circuits_by_name)),
        },
    }


def inspect_geojson(path, layer_kind="departamentos"):
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    features = data.get("features", [])
    prop_counter = Counter()
    geom_counter = Counter()
    sample_props = []
    circuit_keys_by_name = set()
    features_without_join_key = 0
    for feature in features:
        props = feature.get("properties", {}) or {}
        prop_counter.update(props.keys())
        geom = feature.get("geometry", {}) or {}
        geom_counter[geom.get("type", "SIN_GEOMETRIA")] += 1
        if len(sample_props) < 3:
            sample_props.append(props)
        if layer_kind == "circuitos":
            dep = norm_name(props.get("departamen"))
            circuit = norm_circuit(props.get("circuito"))
            if dep and circuit:
                circuit_keys_by_name.add((dep, circuit))
            else:
                features_without_join_key += 1

    property_names = sorted(prop_counter.keys())
    circuit_like = [
        name
        for name in property_names
        if "CIRC" in name.upper() or "CIRCU" in name.upper()
    ]

    return {
        "path": str(path.relative_to(ROOT)),
        "size_mb": round(path.stat().st_size / 1024 / 1024, 2),
        "feature_count": len(features),
        "geometry_types": dict(geom_counter),
        "property_names": property_names,
        "circuit_like_properties": circuit_like,
        "circuit_keys_by_name": sorted(list(circuit_keys_by_name)),
        "features_without_join_key": features_without_join_key,
        "sample_properties": sample_props,
    }


def file_probe(path):
    first_bytes = path.read_bytes()[:8] if path.exists() else b""
    signature = " ".join(f"{byte:02X}" for byte in first_bytes)
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "size_mb": round(path.stat().st_size / 1024 / 1024, 2) if path.exists() else 0,
        "signature": signature,
    }


def pct(value):
    if value is None:
        return "s/d"
    return f"{value * 100:.2f}%"


def md_table(rows, headers):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def build_report(audit):
    csv_rows = []
    for year, info in audit["csv"].items():
        csv_rows.append(
            {
                "anio": year,
                "archivo": info["path"],
                "filas": f"{info['row_count']:,}".replace(",", "."),
                "secciones": info["sections_count"],
                "circuitos": info["circuits_count"],
                "mesas": f"{info['mesas_count']:,}".replace(",", "."),
                "electores": f"{info['electors_total_from_unique_mesas']:,}".replace(",", "."),
                "votos": f"{info['votes_total_from_rows']:,}".replace(",", "."),
                "participacion_est": pct(info["turnout_estimate"]),
            }
        )

    compare = audit["comparison"]
    geo = audit["geojson"]
    circuit_geo = audit["circuit_geojson"]
    circuit_compare = audit["circuit_geo_comparison"]

    lines = [
        "# Auditoria de datos electorales PBA",
        "",
        f"Generado: {audit['generated_at']}",
        "",
        "## Resumen ejecutivo",
        "",
        "- Los CSV DINE 2023 y 2025 tienen estructura compatible para una primera normalizacion electoral.",
        "- Ambos archivos incluyen `seccion_id`, `seccion_nombre`, `circuito_id`, `circuito_nombre`, `mesa_id`, `mesa_electores`, `agrupacion_nombre`, `votos_tipo` y `votos_cantidad`.",
        "- La unidad electoral de resultados puede reconstruirse a nivel mesa, circuito, partido/departamento y provincia.",
        "- La cartografia departamental disponible en `04_DepartamentosElecciones.geojson` esta a nivel partido/departamento.",
        "- La nueva cartografia `circuitos-electorales-pba.geojson` permite avanzar con el objetivo principal a nivel circuito, usando una clave normalizada partido + circuito.",
        "",
        "## Inventario de resultados",
        "",
        md_table(
            csv_rows,
            [
                "anio",
                "archivo",
                "filas",
                "secciones",
                "circuitos",
                "mesas",
                "electores",
                "votos",
                "participacion_est",
            ],
        ),
        "",
        "Nota: `participacion_est` se calcula como suma de votos registrados / electores unicos por mesa. Debe validarse contra totales oficiales antes de publicar.",
        "",
        "## Compatibilidad territorial 2023-2025",
        "",
        f"- Circuitos 2023: {compare['circuits_2023']}",
        f"- Circuitos 2025: {compare['circuits_2025']}",
        f"- Circuitos en ambos anios: {compare['circuits_intersection']}",
        f"- Circuitos solo en 2023: {compare['circuits_only_2023']}",
        f"- Circuitos solo en 2025: {compare['circuits_only_2025']}",
        "",
        "La comparacion por circuito es viable en datos tabulares y la nueva capa permite mapearla con cobertura casi completa.",
        "",
        "## Fuerzas principales detectadas",
        "",
    ]

    for year, info in audit["csv"].items():
        rows = [
            {"fuerza": name, "votos_positivos": f"{votes:,}".replace(",", ".")}
            for name, votes in list(info["positive_by_group_top"].items())[:12]
        ]
        lines.extend([f"### {year}", "", md_table(rows, ["fuerza", "votos_positivos"]), ""])

    lines.extend(
        [
            "## Tipos de voto",
            "",
        ]
    )
    for year, info in audit["csv"].items():
        rows = [
            {"tipo": name, "votos": f"{votes:,}".replace(",", ".")}
            for name, votes in info["votes_by_type"].items()
        ]
        lines.extend([f"### {year}", "", md_table(rows, ["tipo", "votos"]), ""])

    lines.extend(
        [
            "## Cartografia disponible",
            "",
            "### Departamentos",
            "",
            f"- Archivo: `{geo['path']}`",
            f"- Features: {geo['feature_count']}",
            f"- Tamanio: {geo['size_mb']} MB",
            f"- Tipos geometricos: {geo['geometry_types']}",
            f"- Campos con apariencia de circuito: {geo['circuit_like_properties'] or 'ninguno'}",
            "",
            "Campos principales observados:",
            "",
            ", ".join(geo["property_names"][:80]),
            "",
            "Conclusion: esta capa sirve para un MVP departamental, pero no para pintar circuitos.",
            "",
            "### Circuitos electorales",
            "",
            f"- Archivo: `{circuit_geo['path']}`",
            f"- Features: {circuit_geo['feature_count']}",
            f"- Tamanio: {circuit_geo['size_mb']} MB",
            f"- Tipos geometricos: {circuit_geo['geometry_types']}",
            f"- Campos principales de union: `departamen`, `circuito`.",
            f"- Features sin clave de union aparente: {circuit_geo['features_without_join_key']}",
            "",
            "Compatibilidad contra resultados DINE usando `seccion_nombre/departamen` normalizado + `circuito_id/circuito` normalizado:",
            "",
            f"- Claves cartograficas de circuito: {circuit_compare['geo_circuit_keys']}",
            f"- Match con circuitos 2023: {circuit_compare['matched_2023']} de {circuit_compare['dine_circuits_2023']} DINE; cobertura DINE {circuit_compare['coverage_dine_2023_pct']}%; cobertura geometrica {circuit_compare['coverage_geo_2023_pct']}%.",
            f"- Match con circuitos 2025: {circuit_compare['matched_2025']} de {circuit_compare['dine_circuits_2025']} DINE; cobertura DINE {circuit_compare['coverage_dine_2025_pct']}%; cobertura geometrica {circuit_compare['coverage_geo_2025_pct']}%.",
            f"- Circuitos DINE 2023 sin geometria: {circuit_compare['dine_only_2023']}.",
            f"- Circuitos DINE 2025 sin geometria: {circuit_compare['dine_only_2025']}.",
            f"- Geometrias sin resultados 2023: {circuit_compare['geo_only_2023']}.",
            f"- Geometrias sin resultados 2025: {circuit_compare['geo_only_2025']}.",
            "",
            "Muestras de no apareados:",
            "",
            f"- DINE 2023 sin geometria: {circuit_compare['sample_dine_only_2023']}",
            f"- DINE 2025 sin geometria: {circuit_compare['sample_dine_only_2025']}",
            f"- Geometrias sin DINE 2023: {circuit_compare['sample_geo_only_2023']}",
            f"- Geometrias sin DINE 2025: {circuit_compare['sample_geo_only_2025']}",
            "",
            "## Observaciones para homologacion politica",
            "",
            "- La comparacion solicitada entre La Libertad Avanza y peronismo/kirchnerismo requiere una tabla de homologacion de fuerzas.",
            "- Homologacion inicial sugerida:",
            "  - `LA LIBERTAD AVANZA` (2023) -> bloque `LLA`.",
            "  - `ALIANZA LA LIBERTAD AVANZA` (2025) -> bloque `LLA`.",
            "  - `UNION POR LA PATRIA` (2023) -> bloque `PERONISMO_K`.",
            "  - `ALIANZA FUERZA PATRIA` (2025) -> bloque `PERONISMO_K`.",
            "- El resto de fuerzas deberia conservarse como agrupacion propia y, en paralelo, clasificarse en bloques amplios si el analisis politico lo requiere.",
            "",
            "## Circuitos no apareados",
            "",
            "Muestra de claves con formato `(distrito_id, seccion_id, circuito_id)`:",
            "",
            f"- Solo 2023: {compare['sample_only_2023']}",
            f"- Solo 2025: {compare['sample_only_2025']}",
            "",
            "## Archivos auxiliares",
            "",
            f"- `Libro3_normalizado_mapas.xls`: firma `{audit['xls_2025_probe']['signature']}`. Es un Excel binario historico `.xls`; requiere conversion o lector `xlrd` para auditar hojas.",
            f"- Diccionario `.xlsx`: firma `{audit['dict_xlsx_probe']['signature']}`. Es un `.xlsx` valido y puede inspeccionarse luego si necesitamos documentar campos de la capa departamental.",
            "",
            "## Recomendacion para el proximo paso",
            "",
            "1. Construir un ETL que produzca agregados por circuito para 2023 y 2025, mas una tabla de comparacion.",
            "2. Preparar una capa GeoJSON liviana de circuitos con clave normalizada `partido_norm + circuito_norm`.",
            "3. Desarrollar el MVP estatico con Leaflet/Argenmap usando datos preprocesados.",
            "4. Revisar manualmente los pocos circuitos no apareados antes de publicar indicadores finales.",
            "",
            "## Indicadores calculables con los insumos actuales",
            "",
            "- Electores por mesa/circuito/partido/provincia.",
            "- Votantes como suma de votos por mesa/circuito/partido/provincia.",
            "- Participacion y ausentismo.",
            "- Voto positivo por fuerza.",
            "- Blanco, nulo y otros tipos disponibles en `votos_tipo`.",
            "- Ranking de variaciones 2023-2025 por circuito si se usa la tabla electoral.",
            "- Mapa de variaciones por circuito con la nueva cartografia, sujeto a resolver no apareados.",
        ]
    )

    return "\n".join(lines) + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_audit = {year: inspect_csv(path) for year, path in SOURCES.items()}

    circuits_2023 = set(tuple(item) for item in csv_audit["2023"]["keys"]["circuits"])
    circuits_2025 = set(tuple(item) for item in csv_audit["2025"]["keys"]["circuits"])

    geo_circuits = inspect_geojson(CIRCUIT_GEOJSON, layer_kind="circuitos")
    geo_circuit_keys = set(tuple(item) for item in geo_circuits["circuit_keys_by_name"])
    dine_circuits_2023_by_name = set(tuple(item) for item in csv_audit["2023"]["keys"]["circuits_by_name"])
    dine_circuits_2025_by_name = set(tuple(item) for item in csv_audit["2025"]["keys"]["circuits_by_name"])
    matched_2023 = dine_circuits_2023_by_name & geo_circuit_keys
    matched_2025 = dine_circuits_2025_by_name & geo_circuit_keys

    def coverage(part, total):
        return round(part / total * 100, 2) if total else 0

    audit = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "csv": csv_audit,
        "geojson": inspect_geojson(GEOJSON),
        "circuit_geojson": geo_circuits,
        "xls_2025_probe": file_probe(XLS_2025),
        "dict_xlsx_probe": file_probe(DICT_XLSX),
        "comparison": {
            "circuits_2023": len(circuits_2023),
            "circuits_2025": len(circuits_2025),
            "circuits_intersection": len(circuits_2023 & circuits_2025),
            "circuits_only_2023": len(circuits_2023 - circuits_2025),
            "circuits_only_2025": len(circuits_2025 - circuits_2023),
            "sample_only_2023": sorted(list(circuits_2023 - circuits_2025))[:20],
            "sample_only_2025": sorted(list(circuits_2025 - circuits_2023))[:20],
        },
        "circuit_geo_comparison": {
            "geo_circuit_keys": len(geo_circuit_keys),
            "dine_circuits_2023": len(dine_circuits_2023_by_name),
            "dine_circuits_2025": len(dine_circuits_2025_by_name),
            "matched_2023": len(matched_2023),
            "matched_2025": len(matched_2025),
            "coverage_dine_2023_pct": coverage(len(matched_2023), len(dine_circuits_2023_by_name)),
            "coverage_dine_2025_pct": coverage(len(matched_2025), len(dine_circuits_2025_by_name)),
            "coverage_geo_2023_pct": coverage(len(matched_2023), len(geo_circuit_keys)),
            "coverage_geo_2025_pct": coverage(len(matched_2025), len(geo_circuit_keys)),
            "dine_only_2023": len(dine_circuits_2023_by_name - geo_circuit_keys),
            "dine_only_2025": len(dine_circuits_2025_by_name - geo_circuit_keys),
            "geo_only_2023": len(geo_circuit_keys - dine_circuits_2023_by_name),
            "geo_only_2025": len(geo_circuit_keys - dine_circuits_2025_by_name),
            "sample_dine_only_2023": sorted(list(dine_circuits_2023_by_name - geo_circuit_keys))[:30],
            "sample_dine_only_2025": sorted(list(dine_circuits_2025_by_name - geo_circuit_keys))[:30],
            "sample_geo_only_2023": sorted(list(geo_circuit_keys - dine_circuits_2023_by_name))[:30],
            "sample_geo_only_2025": sorted(list(geo_circuit_keys - dine_circuits_2025_by_name))[:30],
        },
    }

    (OUT_DIR / "auditoria_datos.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "auditoria_datos.md").write_text(build_report(audit), encoding="utf-8")

    print(OUT_DIR / "auditoria_datos.md")
    print(OUT_DIR / "auditoria_datos.json")


if __name__ == "__main__":
    main()
