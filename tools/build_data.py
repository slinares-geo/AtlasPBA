import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
DINE_DIR = ROOT / "02_Datos" / "01_DINE"
CIRCUIT_GEOJSON = ROOT / "02_Datos" / "03_circuitoselectoralespba" / "01_CircuitosElectorales2025_PBA3.geojson"
PARTY_GEOJSON = ROOT / "02_Datos" / "03_circuitoselectoralespba" / "02_PartidosPBA2.geojson"

BLOCK_ALIASES = {
    "LA LIBERTAD AVANZA": "LLA",
    "ALIANZA LA LIBERTAD AVANZA": "LLA",
    "UNION POR LA PATRIA": "PERONISMO_K",
    "UNIÓN POR LA PATRIA": "PERONISMO_K",
    "ALIANZA FUERZA PATRIA": "PERONISMO_K",
}

BLOCK_LABELS = {
    "LLA": "La Libertad Avanza",
    "PERONISMO_K": "Peronismo / kirchnerismo",
}

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
    return (value or "").strip()


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


def norm_group(value):
    text = norm_name(value)
    return text


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


def party_code(props):
    return norm_text(props.get("CODIGO") or props.get("cde"))


def party_name(props):
    return props.get("NOMBRE") or props.get("nam") or props.get("fna") or props.get("departamen")


def resolve_party_key(province_id, department_id, party_name, valid_codes, codes_by_name):
    key = party_key_from_codes(province_id, department_id, valid_codes)
    if key in valid_codes:
        return key
    return codes_by_name.get(norm_name(party_name), key)


def as_int(value):
    try:
        if value is None or value == "":
            return 0
        return int(float(str(value).replace(",", ".")))
    except ValueError:
        return 0


def pct(part, total):
    return part / total if total else None


def round_or_none(value, digits=6):
    return round(value, digits) if value is not None else None


def empty_bucket():
    return {
        "partido": "",
        "partido_norm": "",
        "seccion_id": "",
        "seccionprovincial_id": "",
        "seccionprovincial_nombre": "",
        "circuito": "",
        "electores_mesas": {},
        "votos_total": 0,
        "votos_tipo": Counter(),
        "fuerzas": Counter(),
        "bloques": Counter(),
    }


def discover_sources():
    sources = []
    for path in sorted(DINE_DIR.rglob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            first = next(reader)
        year = norm_text(first.get("año"))
        election_type = pretty_label(first.get("eleccion_tipo"))
        cargo = pretty_label(first.get("cargo_nombre"))
        cargo_id = norm_text(first.get("cargo_id"))
        election_id = norm_text(first.get("eleccion_id"))
        source_id = slug([year, first.get("eleccion_tipo"), cargo_id or cargo, path.stem])
        label = f"{year} · {election_type} · {cargo}"
        sources.append({
            "id": source_id,
            "year": year,
            "label": label,
            "election_type": election_type,
            "cargo": cargo,
            "cargo_id": cargo_id,
            "election_id": election_id,
            "path": path,
        })
    return sources


def slug(parts):
    text = "_".join(norm_name(part) for part in parts if part)
    text = re.sub(r"[^A-Z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_").lower()


def pretty_label(value):
    text = norm_text(value).lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1].upper() + text[1:]


def read_results(source, circuit_party_lookup, party_codes_by_name):
    buckets = defaultdict(empty_bucket)
    totals = {"rows": 0, "votes": 0, "electors": 0, "circuits": 0, "groups": Counter()}

    with source["path"].open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            totals["rows"] += 1
            key = norm_circuit(row.get("circuito_id"))
            party_lookup = circuit_party_lookup.get(key, {})
            bucket = buckets[key]
            bucket["partido"] = party_lookup.get("name") or title_name(row.get("seccion_nombre"))
            bucket["partido_norm"] = party_lookup.get("key") or party_codes_by_name.get(norm_name(row.get("seccion_nombre"))) or norm_name(row.get("seccion_nombre"))
            bucket["seccion_id"] = norm_text(row.get("seccion_id"))
            bucket["seccionprovincial_id"] = norm_text(row.get("seccionprovincial_id"))
            bucket["seccionprovincial_nombre"] = norm_text(row.get("seccionprovincial_nombre"))
            bucket["circuito"] = norm_circuit(row.get("circuito_id"))

            mesa_key = (
                norm_text(row.get("distrito_id")),
                norm_text(row.get("seccion_id")),
                norm_circuit(row.get("circuito_id")),
                norm_text(row.get("mesa_id")),
                norm_text(row.get("mesa_tipo")),
            )
            electors = as_int(row.get("mesa_electores"))
            if electors:
                bucket["electores_mesas"][mesa_key] = electors

            votes = as_int(row.get("votos_cantidad"))
            vote_type = norm_text(row.get("votos_tipo")).upper() or "SIN_TIPO"
            group_raw = norm_text(row.get("agrupacion_nombre"))
            group = norm_group(group_raw)
            bucket["votos_total"] += votes
            bucket["votos_tipo"][vote_type] += votes
            totals["votes"] += votes

            if vote_type == "POSITIVO" and group:
                bucket["fuerzas"][group_raw] += votes
                totals["groups"][group_raw] += votes
                block = BLOCK_ALIASES.get(group)
                if block:
                    bucket["bloques"][block] += votes

    output = {}
    for key, bucket in buckets.items():
        positive = bucket["votos_tipo"].get("POSITIVO", 0)
        electors = sum(bucket["electores_mesas"].values())
        top_forces = bucket["fuerzas"].most_common()
        winner = top_forces[0] if top_forces else ("", 0)
        runner_up = top_forces[1] if len(top_forces) > 1 else ("", 0)

        output[key] = {
            "key": key,
            "partido": bucket["partido"],
            "partido_norm": bucket["partido_norm"],
            "seccion_id": bucket["seccion_id"],
            "seccionprovincial_id": bucket["seccionprovincial_id"],
            "seccionprovincial_nombre": bucket["seccionprovincial_nombre"],
            "circuito": bucket["circuito"],
            "electores": electors,
            "votantes": bucket["votos_total"],
            "participacion": round_or_none(pct(bucket["votos_total"], electors)),
            "ausentismo": round_or_none(1 - pct(bucket["votos_total"], electors) if electors else None),
            "positivos": positive,
            "blanco": bucket["votos_tipo"].get("EN BLANCO", 0),
            "nulo": bucket["votos_tipo"].get("NULO", 0),
            "impugnado": bucket["votos_tipo"].get("IMPUGNADO", 0),
            "recurrido": bucket["votos_tipo"].get("RECURRIDO", 0),
            "pct_blanco": round_or_none(pct(bucket["votos_tipo"].get("EN BLANCO", 0), bucket["votos_total"])),
            "pct_nulo": round_or_none(pct(bucket["votos_tipo"].get("NULO", 0), bucket["votos_total"])),
            "pct_impugnado": round_or_none(pct(bucket["votos_tipo"].get("IMPUGNADO", 0), bucket["votos_total"])),
            "pct_recurrido": round_or_none(pct(bucket["votos_tipo"].get("RECURRIDO", 0), bucket["votos_total"])),
            "fuerzas": dict(bucket["fuerzas"].most_common()),
            "fuerzas_pct": {name: round_or_none(pct(votes, positive)) for name, votes in bucket["fuerzas"].items()},
            "bloques": dict(bucket["bloques"].most_common()),
            "bloques_pct": {block: round_or_none(pct(votes, positive)) for block, votes in bucket["bloques"].items()},
            "ganador": winner[0],
            "ganador_votos": winner[1],
            "segundo": runner_up[0],
            "segundo_votos": runner_up[1],
            "margen": round_or_none(pct(winner[1] - runner_up[1], positive)),
        }

    totals["electors"] = sum(item["electores"] for item in output.values())
    totals["circuits"] = len(output)
    return output, totals


def compare_elections(base_data, target_data):
    comparison = {}
    for key in sorted(set(base_data) | set(target_data)):
        base = base_data.get(key)
        target = target_data.get(key)
        row = target or base

        def diff(field):
            if not base or not target:
                return None
            a = base.get(field)
            b = target.get(field)
            return round_or_none(b - a) if a is not None and b is not None else None

        def block_diff(block):
            if not base or not target:
                return None
            return round_or_none((target["bloques_pct"].get(block) or 0) - (base["bloques_pct"].get(block) or 0))

        comparison[key] = {
            "key": key,
            "partido": row["partido"],
            "partido_norm": row["partido_norm"],
            "circuito": row["circuito"],
            "has_base": bool(base),
            "has_target": bool(target),
            "participacion_delta": diff("participacion"),
            "ausentismo_delta": diff("ausentismo"),
            "blanco_delta": diff("pct_blanco"),
            "nulo_delta": diff("pct_nulo"),
            "margen_delta": diff("margen"),
            "lla_delta": block_diff("LLA"),
            "peronismo_k_delta": block_diff("PERONISMO_K"),
            "winner_changed": base.get("ganador") != target.get("ganador") if base and target else None,
        }
    return comparison


def aggregate_party(circuits):
    parties = defaultdict(lambda: {
        "key": "",
        "partido": "",
        "partido_norm": "",
        "electores": 0,
        "votantes": 0,
        "positivos": 0,
        "blanco": 0,
        "nulo": 0,
        "bloques": Counter(),
        "fuerzas": Counter(),
        "circuit_count": 0,
    })
    for row in circuits.values():
        party = parties[row["partido_norm"]]
        party["key"] = row["partido_norm"]
        party["partido"] = row["partido"]
        party["partido_norm"] = row["partido_norm"]
        party["electores"] += row["electores"] or 0
        party["votantes"] += row["votantes"] or 0
        party["positivos"] += row["positivos"] or 0
        party["blanco"] += row["blanco"] or 0
        party["nulo"] += row["nulo"] or 0
        party["impugnado"] = party.get("impugnado", 0) + (row.get("impugnado") or 0)
        party["recurrido"] = party.get("recurrido", 0) + (row.get("recurrido") or 0)
        party["bloques"].update(row["bloques"])
        party["fuerzas"].update(row["fuerzas"])
        party["circuit_count"] += 1

    output = {}
    for key, row in parties.items():
        row["bloques"] = dict(row["bloques"].most_common())
        row["fuerzas"] = dict(row["fuerzas"].most_common())
        row["participacion"] = round_or_none(pct(row["votantes"], row["electores"]))
        row["ausentismo"] = round_or_none(1 - pct(row["votantes"], row["electores"]) if row["electores"] else None)
        row["pct_blanco"] = round_or_none(pct(row["blanco"], row["votantes"]))
        row["pct_nulo"] = round_or_none(pct(row["nulo"], row["votantes"]))
        row["pct_impugnado"] = round_or_none(pct(row.get("impugnado", 0), row["votantes"]))
        row["pct_recurrido"] = round_or_none(pct(row.get("recurrido", 0), row["votantes"]))
        row["bloques_pct"] = {block: round_or_none(pct(votes, row["positivos"])) for block, votes in row["bloques"].items()}
        top_forces = sorted(row["fuerzas"].items(), key=lambda item: item[1], reverse=True)
        winner = top_forces[0] if top_forces else ("", 0)
        runner_up = top_forces[1] if len(top_forces) > 1 else ("", 0)
        row["ganador"] = winner[0]
        row["ganador_votos"] = winner[1]
        row["segundo"] = runner_up[0]
        row["segundo_votos"] = runner_up[1]
        row["margen"] = round_or_none(pct(winner[1] - runner_up[1], row["positivos"]))
        output[key] = row
    return output


def slim_circuit_geojson(metrics):
    valid_party_codes, party_codes_by_name = load_party_lookup()
    with CIRCUIT_GEOJSON.open("r", encoding="utf-8") as handle:
        geo = json.load(handle)
    for feature in geo.get("features", []):
        props = feature.get("properties", {}) or {}
        key = norm_circuit(props.get("circuito"))
        party_key = party_code(props) or resolve_party_key(props.get("indec_p"), props.get("indec_d"), props.get("departamen"), valid_party_codes, party_codes_by_name)
        feature["properties"] = {
            "key": key,
            "partido": title_name(props.get("departamen")),
            "partido_norm": party_key,
            "circuito": norm_circuit(props.get("circuito")),
            "indec_p": norm_code(props.get("indec_p"), 2),
            "indec_d": props.get("indec_d"),
            "cde": party_key,
            "has_data": key in metrics,
        }
    return geo


def slim_party_geojson(party_keys):
    with PARTY_GEOJSON.open("r", encoding="utf-8") as handle:
        geo = json.load(handle)
    for feature in geo.get("features", []):
        props = feature.get("properties", {}) or {}
        key = party_code(props)
        feature["properties"] = {
            "key": key,
            "partido": party_name(props) or title_name(key),
            "partido_norm": key,
            "cde": key,
            "has_data": key in party_keys,
        }
    geo["features"] = [feature for feature in geo.get("features", []) if feature["properties"]["has_data"]]
    return geo


def load_party_lookup():
    with PARTY_GEOJSON.open("r", encoding="utf-8") as handle:
        geo = json.load(handle)
    codes = set()
    by_name = {}
    for feature in geo.get("features", []):
        props = feature.get("properties", {}) or {}
        code = party_code(props)
        if not code:
            continue
        codes.add(code)
        by_name.setdefault(norm_name(party_name(props)), code)
    return codes, by_name


def build_circuit_party_lookup():
    valid_party_codes, party_codes_by_name = load_party_lookup()
    with CIRCUIT_GEOJSON.open("r", encoding="utf-8") as handle:
        geo = json.load(handle)
    lookup = {}
    for feature in geo.get("features", []):
        props = feature.get("properties", {}) or {}
        circuit = norm_circuit(props.get("circuito"))
        party_key = party_code(props) or resolve_party_key(props.get("indec_p"), props.get("indec_d"), props.get("departamen"), valid_party_codes, party_codes_by_name)
        lookup[circuit] = {"key": party_key, "name": title_name(props.get("departamen"))}
    return lookup


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sources = discover_sources()
    _, party_codes_by_name = load_party_lookup()
    circuit_party_lookup = build_circuit_party_lookup()
    circuit_elections = {}
    party_elections = {}
    source_meta = []

    for source in sources:
      data, totals = read_results(source, circuit_party_lookup, party_codes_by_name)
      circuit_elections[source["id"]] = data
      party_elections[source["id"]] = aggregate_party(data)
      source_meta.append({
          "id": source["id"],
          "year": source["year"],
          "label": source["label"],
          "election_type": source["election_type"],
          "cargo": source["cargo"],
          "path": str(source["path"].relative_to(ROOT)),
          "rows": totals["rows"],
          "votes": totals["votes"],
          "electors": totals["electors"],
          "circuits": totals["circuits"],
          "top_groups": dict(totals["groups"].most_common(20)),
      })

    default_base = next((source["id"] for source in source_meta if source["year"] == "2023" and "Presidente" in source["cargo"] and "Segunda" not in source["election_type"]), source_meta[0]["id"])
    default_target = next((source["id"] for source in source_meta if source["year"] == "2025"), source_meta[-1]["id"])

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "csv",
        "blocks": BLOCK_LABELS,
        "sources": source_meta,
        "defaults": {"base": default_base, "target": default_target},
        "circuit": {"elections": circuit_elections},
        "party": {"elections": party_elections},
    }

    all_circuit_keys = set().union(*(set(data) for data in circuit_elections.values()))
    all_party_keys = set().union(*(set(data) for data in party_elections.values()))

    (DATA_DIR / "electoral_data.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (DATA_DIR / "circuitos_pba.geojson").write_text(json.dumps(slim_circuit_geojson(all_circuit_keys), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (DATA_DIR / "partidos_pba.geojson").write_text(json.dumps(slim_party_geojson(all_party_keys), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(DATA_DIR / "electoral_data.json")
    print(f"{len(source_meta)} elecciones CSV procesadas")


if __name__ == "__main__":
    main()
