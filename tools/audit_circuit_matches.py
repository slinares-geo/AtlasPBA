import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
APP_DIR = Path(__file__).resolve().parents[1]
GEO_PATH = ROOT / "02_Datos" / "03_circuitoselectoralespba" / "01_CircuitosElectorales2025_PBA2.geojson"
CSV_PATHS = {
    "2023": ROOT / "02_Datos" / "01_DINE" / "01_2023" / "01_ResultadosGeneralesPresidencialesPBA2023.csv",
    "2025": ROOT / "02_Datos" / "01_DINE" / "02_2025" / "01_ResultadosDiputadosGeneralesPBA2025.csv",
}
OUT_PATH = APP_DIR / "docs" / "circuitos_geojson_sin_datos_2023_2025.csv"
OUT_UNIQUE_PATH = APP_DIR / "docs" / "circuitos_unicos_sin_datos_2023_2025.csv"


def norm_circuit(value):
    text = str(value or "").strip().upper()
    if re.fullmatch(r"\d+", text):
        return str(int(text))
    match = re.fullmatch(r"0*(\d+)([A-Z]+)", text)
    if match:
        return f"{int(match.group(1))}{match.group(2)}"
    return text.lstrip("0") or text


def csv_circuit_keys(path):
    keys = set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            keys.add(norm_circuit(row.get("circuito_id")))
    return keys


def main():
    geo = json.loads(GEO_PATH.read_text(encoding="utf-8"))
    geo_by_key = defaultdict(list)
    for index, feature in enumerate(geo.get("features", []), 1):
        props = feature.get("properties", {}) or {}
        key = norm_circuit(props.get("circuito"))
        geo_by_key[key].append({
            "feature_index": index,
            "circuito_key": key,
            "circuito_geo": props.get("circuito"),
            "partido_geo": props.get("departamen"),
            "indec_p": props.get("indec_p"),
            "indec_d": props.get("indec_d"),
            "cde_from_circuit": f"{str(props.get('indec_p') or '').strip()}{str(props.get('indec_d') or '').strip()}",
            "gid": props.get("gid"),
        })

    csv_keys = {year: csv_circuit_keys(path) for year, path in CSV_PATHS.items()}
    missing = {
        year: sorted(set(geo_by_key) - keys, key=lambda value: (len(value), value))
        for year, keys in csv_keys.items()
    }
    common = sorted(set(missing["2023"]) & set(missing["2025"]), key=lambda value: (len(value), value))
    only_2023 = sorted(set(missing["2023"]) - set(missing["2025"]), key=lambda value: (len(value), value))
    only_2025 = sorted(set(missing["2025"]) - set(missing["2023"]), key=lambda value: (len(value), value))

    rows = []
    unique_rows = []
    for year in ("2023", "2025"):
        other_year = "2025" if year == "2023" else "2023"
        for key in missing[year]:
            first_geo_row = geo_by_key[key][0]
            unique_rows.append({
                "anio_sin_datos": year,
                "tambien_sin_datos_otro_anio": key in missing[other_year],
                "circuito_key": key,
                "circuito_geo": first_geo_row["circuito_geo"],
                "partido_geo": first_geo_row["partido_geo"],
                "indec_p": first_geo_row["indec_p"],
                "indec_d": first_geo_row["indec_d"],
                "cde_from_circuit": first_geo_row["cde_from_circuit"],
                "features_con_mismo_circuito": len(geo_by_key[key]),
            })
            for geo_row in geo_by_key[key]:
                rows.append({
                    "anio_sin_datos": year,
                    "tambien_sin_datos_otro_anio": key in missing[other_year],
                    **geo_row,
                })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "anio_sin_datos",
            "tambien_sin_datos_otro_anio",
            "circuito_key",
            "circuito_geo",
            "partido_geo",
            "indec_p",
            "indec_d",
            "cde_from_circuit",
            "gid",
            "feature_index",
        ])
        writer.writeheader()
        writer.writerows(rows)

    with OUT_UNIQUE_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "anio_sin_datos",
            "tambien_sin_datos_otro_anio",
            "circuito_key",
            "circuito_geo",
            "partido_geo",
            "indec_p",
            "indec_d",
            "cde_from_circuit",
            "features_con_mismo_circuito",
        ])
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"out={OUT_PATH}")
    print(f"out_unique={OUT_UNIQUE_PATH}")
    print(f"geo_unique_circuits={len(geo_by_key)}")
    print(f"missing_2023_unique={len(missing['2023'])}")
    print(f"missing_2025_unique={len(missing['2025'])}")
    print(f"common_unique={len(common)}")
    print(f"only_2023_unique={len(only_2023)} {only_2023}")
    print(f"only_2025_unique={len(only_2025)} {only_2025}")
    print(f"export_rows={len(rows)}")
    print(f"export_unique_rows={len(unique_rows)}")
    print("common_list=circuito_key|partido_geo|indec_p|indec_d")
    for key in common:
        row = geo_by_key[key][0]
        print(f"{key}|{row['partido_geo']}|{row['indec_p']}|{row['indec_d']}")


if __name__ == "__main__":
    main()
