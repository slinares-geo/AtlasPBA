# Auditoria de datos electorales PBA

Generado: 2026-06-10T09:27:51

## Alcance vigente

- Esta auditoria corresponde a la app `05_MapaElectoral_Cockpit_CSV`.
- Capa de partidos fuente: `02_PartidosPBA2.geojson`.
- Capa de circuitos fuente: `01_CircuitosElectorales2025_PBA3.geojson`.
- La clave de union de partido es `CODIGO`.
- La clave de union de circuito es `circuito`, normalizada sin ceros iniciales y conservando sufijos alfabeticos.
- Los artefactos auditados son `electoral_data.json`, `partidos_pba.geojson` y `circuitos_pba.geojson` dentro de `data/`.

## Inventario CSV DINE

| eleccion | archivo | filas | circuitos | mesas | electores | votos | participacion_est |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2023 · General · Presidente/a | 02_Datos\01_DINE\01_2023\01_ResultadosGeneralesPresidencialesPBA2023.csv | 380.740 | 1047 | 38.074 | 13.124.435 | 10.199.399 | 77.71% |
| 2023 · Segunda vuelta · Presidente y vice | 02_Datos\01_DINE\01_2023\02_ResultadosSegundaPresidencialesPBA2023.csv | 226.998 | 1039 | 37.833 | 13.052.907 | 10.017.387 | 76.74% |
| 2023 · General · Gobernador/a | 02_Datos\01_DINE\01_2023\03_ResultadosGeneralesGobernadorPBA2023.csv | 361.809 | 1047 | 40.201 | 14.073.604 | 10.439.895 | 74.18% |
| 2025 · Generales · Diputado nacional | 02_Datos\01_DINE\02_2025\01_ResultadosDiputadosGeneralesPBA2025.csv | 775.200 | 1047 | 38.760 | 13.349.014 | 9.013.159 | 67.52% |

Nota: `participacion_est` se calcula como suma de votos registrados / electores unicos por mesa.

## Capas fuente

- Partidos fuente: 135 features, 135 CODIGO unicos.
- Circuitos fuente: 1153 features, 1153 circuitos unicos.
- CODIGO de partido presentes en circuitos fuente: 135.
- Features de circuito sin `CODIGO`: 0.
- Features de circuito sin `circuito`: 0.
- CODIGO duplicados en partidos fuente: ninguno.

Partidos criticos en la capa fuente:

| codigo | esperado | nombre_fuente |
| --- | --- | --- |
| 06218 | Chascomús | Chascomús |
| 06466 | Lezama | Lezama |
| 06371 | General San Martín | General San Martín |

## Cobertura circuito contra capa PBA3

| eleccion | circuitos_dine | match | cobertura_dine | dine_sin_geo | geo_sin_datos |
| --- | --- | --- | --- | --- | --- |
| 2023 · General · Presidente/a | 1047 | 1045 | 99.81% | 2 | 108 |
| 2023 · Segunda vuelta · Presidente y vice | 1039 | 1037 | 99.81% | 2 | 116 |
| 2023 · General · Gobernador/a | 1047 | 1045 | 99.81% | 2 | 108 |
| 2025 · Generales · Diputado nacional | 1047 | 1047 | 100.0% | 0 | 106 |

Muestras de circuitos DINE sin geometria:

- 2023 · General · Presidente/a: ['383', '388']
- 2023 · Segunda vuelta · Presidente y vice: ['383', '388']
- 2023 · General · Gobernador/a: ['383', '388']
- 2025 · Generales · Diputado nacional: ninguno

## Artefactos normalizados de la app

- `electoral_data.json` generado: 2026-06-10T09:14:28.
- Elecciones procesadas: 4.
- GeoJSON partidos app: 135 features, 135 claves unicas.
- GeoJSON circuitos app: 1153 features, 1153 claves unicas.

| eleccion | partidos | circuitos_datos | partidos_sin_geo | circuitos_sin_geo |
| --- | --- | --- | --- | --- |
| 2023 · General · Presidente/a | 135 | 1047 | 0 | 2 |
| 2023 · Segunda vuelta · Presidente y vice | 135 | 1039 | 0 | 2 |
| 2023 · General · Gobernador/a | 135 | 1047 | 0 | 2 |
| 2025 · Generales · Diputado nacional | 135 | 1047 | 0 | 0 |

## Validacion de partidos criticos en datos agregados

| eleccion | codigo | esperado | nombre | circuitos | electores | votantes |
| --- | --- | --- | --- | --- | --- | --- |
| 2023 · General · Presidente/a | 06218 | Chascomús | Chascomús | 6 | 35.319 | 27.578 |
| 2023 · General · Presidente/a | 06466 | Lezama | Lezama | 1 | 4.965 | 4.148 |
| 2023 · General · Presidente/a | 06371 | General San Martín | General San Martín | 11 | 351.839 | 265.803 |
| 2023 · Segunda vuelta · Presidente y vice | 06218 | Chascomús | Chascomús | 6 | 35.366 | 26.756 |
| 2023 · Segunda vuelta · Presidente y vice | 06466 | Lezama | Lezama | 1 | 4.968 | 3.862 |
| 2023 · Segunda vuelta · Presidente y vice | 06371 | General San Martín | General San Martín | 11 | 350.871 | 265.179 |
| 2023 · General · Gobernador/a | 06218 | Chascomús | Chascomús | 6 | 35.936 | 27.737 |
| 2023 · General · Gobernador/a | 06466 | Lezama | Lezama | 1 | 5.060 | 4.173 |
| 2023 · General · Gobernador/a | 06371 | General San Martín | General San Martín | 11 | 397.173 | 273.079 |
| 2025 · Generales · Diputado nacional | 06218 | Chascomús | Chascomús | 6 | 35.945 | 23.816 |
| 2025 · Generales · Diputado nacional | 06466 | Lezama | Lezama | 1 | 5.022 | 3.467 |
| 2025 · Generales · Diputado nacional | 06371 | General San Martín | General San Martín | 12 | 378.078 | 242.835 |

## Lectura operativa

- A nivel partido, todas las elecciones quedan con 135 partidos y sin partidos con datos fuera de la geometria.
- Chascomus y Lezama quedan separados por CODIGO: `06218` y `06466`.
- General San Martin queda agregado por CODIGO `06371`, incluyendo circuitos historicos 2023 aunque no existan como poligonos individuales en la capa 2025.
- En vista circuito, 2023 conserva una salvedad: los circuitos historicos `383` y `388` no tienen geometria propia en PBA3.
