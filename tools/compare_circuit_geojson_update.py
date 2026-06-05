import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
DOCS_DIR = APP_DIR / "docs"

APP_CIRCUITS = DATA_DIR / "circuitos_pba.geojson"
APP_ELECTORAL_DATA = DATA_DIR / "electoral_data.json"
OLD_SOURCE = ROOT / "02_Datos" / "03_circuitoselectoralespba" / "01_CircuitosElectorales2025_PBA.geojson"
NEW_SOURCE = ROOT / "02_Datos" / "03_circuitoselectoralespba" / "01_CircuitosElectorales2025_PBA2.geojson"
PARTY_GEOJSON = ROOT / "02_Datos" / "03_circuitoselectoralespba" / "02_PartidosPBA.geojson"
REPORT_JSON = DOCS_DIR / "comparacion_circuitos_pba2.json"
REPORT_MD = DOCS_DIR / "comparacion_circuitos_pba2.md"

PARTY_ALIASES = {
    "A GONZALES CHAVES": "ADOLFO GONZALES CHAVES",
    "CAEUELAS": "CANUELAS",
    "CA UELAS": "CANUELAS",
    "CNEL DE MARINA L ROSALES": "CORONEL DE MARINA L ROSALES",
    "CORONEL ROSALES": "CORONEL DE MARINA L ROSALES",
    "9 DE JULIO": "NUEVE DE JULIO",
    "25 DE MAYO": "VEINTICINCO DE MAYO",
    "GENERAL LAMADRID": "GENERAL LA MADRID",
    "GENERAL MADARIAGA": "GENERAL JUAN MADARIAGA",
    "MORNN": "MORON",
}


def norm_text(value):
    return ("" if value is None else str(value)).strip()


def norm_name(value):
    text = norm_text(value).upper().replace("Ñ", "N")
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = re.sub(r"^PARTIDO\s+(DE|DEL)\s+", "", text)
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return PARTY_ALIASES.get(text, text)


def title_name(value):
    return " ".join(word.capitalize() for word in norm_text(value).lower().split())


def norm_circuit(value):
    text = norm_text(value).upper()
    if re.fullmatch(r"\d+", text):
        return str(int(text))
    match = re.fullmatch(r"0*(\d+)([A-Z]+)", text)
    if match:
        return f"{int(match.group(1))}{match.group(2)}"
    return text.lstrip("0") or text


def norm_code(value, width):
    text = norm_text(value)
    if re.fullmatch(r"\d+", text):
        return text.zfill(width)
    return text


def party_key_from_codes(province_id, department_id, valid_codes=None):
    department = norm_code(department_id, 3)
    candidate = f"{norm_code(province_id, 2)}{department}"
    fallback = f"06{department}"
    if valid_codes and candidate not in valid_codes and fallback in valid_codes:
        return fallback
    return candidate


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def geometry_hash(geometry):
    payload = json.dumps(geometry, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def feature_fields(geo):
    fields = set()
    for feature in geo.get("features", []):
        fields.update((feature.get("properties") or {}).keys())
    return sorted(fields)


def geometry_types(geo):
    return dict(Counter((feature.get("geometry") or {}).get("type", "None") for feature in geo.get("features", [])))


def collection_summary(path, geo):
    return {
        "path": str(path),
        "type": geo.get("type"),
        "crs": geo.get("crs"),
        "feature_count": len(geo.get("features", [])),
        "geometry_types": geometry_types(geo),
        "property_fields": feature_fields(geo),
        "sample_properties": [(feature.get("properties") or {}) for feature in geo.get("features", [])[:5]],
    }


def load_party_lookup():
    geo = load_json(PARTY_GEOJSON)
    codes = set()
    by_name = {}
    for feature in geo.get("features", []):
        props = feature.get("properties") or {}
        code = norm_text(props.get("cde"))
        if not code:
            continue
        codes.add(code)
        by_name.setdefault(norm_name(props.get("nam") or props.get("fna")), code)
    return codes, by_name


def resolve_party_key(props, valid_codes, codes_by_name):
    key = party_key_from_codes(props.get("indec_p"), props.get("indec_d"), valid_codes)
    if key in valid_codes:
        return key
    return codes_by_name.get(norm_name(props.get("departamen")), key)


def electoral_circuit_keys():
    data = load_json(APP_ELECTORAL_DATA)
    keys = set()
    for election in data.get("circuit", {}).get("elections", {}).values():
        keys.update(election.keys())
    return keys


def normalize_source_geojson(geo, metrics):
    valid_party_codes, party_codes_by_name = load_party_lookup()
    normalized = {
        key: value
        for key, value in geo.items()
        if key not in {"features"}
    }
    normalized["features"] = []
    for feature in geo.get("features", []):
        props = feature.get("properties") or {}
        key = norm_circuit(props.get("circuito"))
        party_key = resolve_party_key(props, valid_party_codes, party_codes_by_name)
        normalized["features"].append({
            "type": "Feature",
            "properties": {
                "key": key,
                "partido": title_name(props.get("departamen")),
                "partido_norm": party_key,
                "circuito": key,
                "indec_p": norm_code(props.get("indec_p"), 2),
                "indec_d": props.get("indec_d"),
                "cde": party_key,
                "has_data": key in metrics,
            },
            "geometry": feature.get("geometry"),
        })
    return normalized


def by_key(geo, key_field="key"):
    out = defaultdict(list)
    for index, feature in enumerate(geo.get("features", []), 1):
        props = feature.get("properties") or {}
        key = norm_circuit(props.get(key_field))
        out[key].append((index, feature))
    return out


def raw_by_circuit(geo):
    out = defaultdict(list)
    for index, feature in enumerate(geo.get("features", []), 1):
        props = feature.get("properties") or {}
        key = norm_circuit(props.get("circuito"))
        out[key].append((index, feature))
    return out


def compare_keyed(old_map, new_map):
    old_keys = set(old_map)
    new_keys = set(new_map)
    common = old_keys & new_keys
    changed_geometry = []
    changed_party = []
    changed_codes = []
    changed_circuit_value = []
    for key in sorted(common, key=lambda value: (len(value), value)):
        old_feature = old_map[key][0][1]
        new_feature = new_map[key][0][1]
        old_props = old_feature.get("properties") or {}
        new_props = new_feature.get("properties") or {}
        if geometry_hash(old_feature.get("geometry")) != geometry_hash(new_feature.get("geometry")):
            changed_geometry.append(key)
        if norm_name(old_props.get("departamen") or old_props.get("partido")) != norm_name(new_props.get("departamen") or new_props.get("partido")):
            changed_party.append({
                "key": key,
                "old": old_props.get("departamen") or old_props.get("partido"),
                "new": new_props.get("departamen") or new_props.get("partido"),
            })
        old_codes = (norm_text(old_props.get("indec_p")), norm_text(old_props.get("indec_d")), norm_text(old_props.get("cde")))
        new_codes = (norm_text(new_props.get("indec_p")), norm_text(new_props.get("indec_d")), norm_text(new_props.get("cde")))
        if old_codes != new_codes:
            changed_codes.append({"key": key, "old": old_codes, "new": new_codes})
        if norm_circuit(old_props.get("circuito")) != norm_circuit(new_props.get("circuito")):
            changed_circuit_value.append({"key": key, "old": old_props.get("circuito"), "new": new_props.get("circuito")})
    return {
        "added_keys": sorted(new_keys - old_keys, key=lambda value: (len(value), value)),
        "removed_keys": sorted(old_keys - new_keys, key=lambda value: (len(value), value)),
        "common_keys": len(common),
        "changed_geometry_keys": changed_geometry,
        "changed_party_names": changed_party,
        "changed_codes": changed_codes,
        "changed_circuit_values": changed_circuit_value,
        "old_duplicate_keys": {key: len(rows) for key, rows in old_map.items() if len(rows) > 1},
        "new_duplicate_keys": {key: len(rows) for key, rows in new_map.items() if len(rows) > 1},
    }


def compact_compare_for_markdown(compare):
    return {
        "agregados": len(compare["added_keys"]),
        "eliminados": len(compare["removed_keys"]),
        "comunes": compare["common_keys"],
        "geometrias_modificadas": len(compare["changed_geometry_keys"]),
        "nombres_partido_modificados": len(compare["changed_party_names"]),
        "codigos_modificados": len(compare["changed_codes"]),
        "circuitos_renombrados": len(compare["changed_circuit_values"]),
        "duplicados_anteriores": len(compare["old_duplicate_keys"]),
        "duplicados_nuevos": len(compare["new_duplicate_keys"]),
    }


def write_report(report):
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    old_new = compact_compare_for_markdown(report["source_old_vs_new"])
    app_new = compact_compare_for_markdown(report["app_current_vs_new_normalized"])
    fields_added = report["field_changes"]["new_source_added_fields"]
    fields_removed = report["field_changes"]["new_source_removed_fields"]
    lines = [
        "# Comparacion de circuitos electorales PBA2",
        "",
        "## Archivos",
        "",
        f"- GeoJSON actual de la app: `{APP_CIRCUITS}`",
        f"- GeoJSON fuente anterior: `{OLD_SOURCE}`",
        f"- GeoJSON fuente nuevo: `{NEW_SOURCE}`",
        "",
        "## Resumen fuente anterior vs fuente nueva",
        "",
        f"- Features anteriores: {report['summaries']['old_source']['feature_count']}",
        f"- Features nuevas: {report['summaries']['new_source']['feature_count']}",
        f"- Circuitos agregados: {old_new['agregados']}",
        f"- Circuitos eliminados: {old_new['eliminados']}",
        f"- Geometrias modificadas: {old_new['geometrias_modificadas']}",
        f"- Campos nuevos: {fields_added or 'ninguno'}",
        f"- Campos eliminados: {fields_removed or 'ninguno'}",
        f"- Tipos geometricos nuevos: {report['summaries']['new_source']['geometry_types']}",
        "",
        "## Resumen app actual vs nueva capa normalizada",
        "",
        f"- Features actuales app: {report['summaries']['app_current']['feature_count']}",
        f"- Features nuevas normalizadas: {report['summaries']['new_normalized']['feature_count']}",
        f"- Circuitos agregados: {app_new['agregados']}",
        f"- Circuitos eliminados: {app_new['eliminados']}",
        f"- Geometrias modificadas: {app_new['geometrias_modificadas']}",
        f"- Circuitos con datos electorales sin geometria nueva: {report['electoral_join']['data_keys_missing_in_new_geo_count']}",
        f"- Geometrias nuevas sin datos electorales: {report['electoral_join']['new_geo_keys_without_data_count']}",
        "",
        "## Clave de union",
        "",
        "La app usa `feature.properties.key` para vincular geometria de circuito con `data.electoral_data.circuit.elections`. En la capa normalizada esa clave se deriva de `properties.circuito` mediante normalizacion de ceros iniciales y sufijos alfabeticos.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    old_source = load_json(OLD_SOURCE)
    new_source = load_json(NEW_SOURCE)
    app_current = load_json(APP_CIRCUITS)
    metrics = electoral_circuit_keys()
    new_normalized = normalize_source_geojson(new_source, metrics)

    old_fields = set(feature_fields(old_source))
    new_fields = set(feature_fields(new_source))
    app_fields = set(feature_fields(app_current))
    normalized_fields = set(feature_fields(new_normalized))
    source_compare = compare_keyed(raw_by_circuit(old_source), raw_by_circuit(new_source))
    app_compare = compare_keyed(by_key(app_current), by_key(new_normalized))
    new_geo_keys = set(by_key(new_normalized))

    report = {
        "summaries": {
            "app_current": collection_summary(APP_CIRCUITS, app_current),
            "old_source": collection_summary(OLD_SOURCE, old_source),
            "new_source": collection_summary(NEW_SOURCE, new_source),
            "new_normalized": collection_summary(NEW_SOURCE, new_normalized),
        },
        "field_changes": {
            "new_source_added_fields": sorted(new_fields - old_fields),
            "new_source_removed_fields": sorted(old_fields - new_fields),
            "app_contract_added_fields_after_normalization": sorted(normalized_fields - app_fields),
            "app_contract_removed_fields_after_normalization": sorted(app_fields - normalized_fields),
        },
        "source_old_vs_new": source_compare,
        "app_current_vs_new_normalized": app_compare,
        "electoral_join": {
            "data_circuit_keys_count": len(metrics),
            "new_geo_keys_count": len(new_geo_keys),
            "data_keys_missing_in_new_geo_count": len(metrics - new_geo_keys),
            "data_keys_missing_in_new_geo_sample": sorted(metrics - new_geo_keys, key=lambda value: (len(value), value))[:50],
            "new_geo_keys_without_data_count": len(new_geo_keys - metrics),
            "new_geo_keys_without_data_sample": sorted(new_geo_keys - metrics, key=lambda value: (len(value), value))[:50],
        },
    }
    write_report(report)

    print(f"report_json={REPORT_JSON}")
    print(f"report_md={REPORT_MD}")
    print(f"old_source_features={report['summaries']['old_source']['feature_count']}")
    print(f"new_source_features={report['summaries']['new_source']['feature_count']}")
    print(f"source_added_circuits={len(source_compare['added_keys'])}")
    print(f"source_removed_circuits={len(source_compare['removed_keys'])}")
    print(f"source_changed_geometries={len(source_compare['changed_geometry_keys'])}")
    print(f"source_added_fields={report['field_changes']['new_source_added_fields']}")
    print(f"source_removed_fields={report['field_changes']['new_source_removed_fields']}")
    print(f"app_current_features={report['summaries']['app_current']['feature_count']}")
    print(f"new_normalized_features={report['summaries']['new_normalized']['feature_count']}")
    print(f"app_added_circuits={len(app_compare['added_keys'])}")
    print(f"app_removed_circuits={len(app_compare['removed_keys'])}")
    print(f"app_changed_geometries={len(app_compare['changed_geometry_keys'])}")
    print(f"app_contract_added_fields={report['field_changes']['app_contract_added_fields_after_normalization']}")
    print(f"app_contract_removed_fields={report['field_changes']['app_contract_removed_fields_after_normalization']}")
    print(f"data_keys_missing_in_new_geo={report['electoral_join']['data_keys_missing_in_new_geo_count']}")
    print(f"new_geo_keys_without_data={report['electoral_join']['new_geo_keys_without_data_count']}")


if __name__ == "__main__":
    main()
