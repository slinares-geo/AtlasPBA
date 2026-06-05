# Auditoria de datos electorales PBA

Generado: 2026-06-01T09:28:45

## Resumen ejecutivo

- Los CSV DINE 2023 y 2025 tienen estructura compatible para una primera normalizacion electoral.
- Ambos archivos incluyen `seccion_id`, `seccion_nombre`, `circuito_id`, `circuito_nombre`, `mesa_id`, `mesa_electores`, `agrupacion_nombre`, `votos_tipo` y `votos_cantidad`.
- La unidad electoral de resultados puede reconstruirse a nivel mesa, circuito, partido/departamento y provincia.
- La cartografia departamental disponible en `04_DepartamentosElecciones.geojson` esta a nivel partido/departamento.
- La nueva cartografia `circuitos-electorales-pba.geojson` permite avanzar con el objetivo principal a nivel circuito, usando una clave normalizada partido + circuito.

## Inventario de resultados

| anio | archivo | filas | secciones | circuitos | mesas | electores | votos | participacion_est |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2023 | 02_Datos\01_DINE\01_2023\presentacionDeResultados_presidenciales_2023.csv | 226.998 | 135 | 1039 | 37.833 | 13.052.907 | 10.017.387 | 76.74% |
| 2025 | 02_Datos\01_DINE\02_2025\presentacionDeResultados_Diputados_2025.csv | 775.200 | 135 | 1047 | 38.760 | 13.349.014 | 9.013.159 | 67.52% |

Nota: `participacion_est` se calcula como suma de votos registrados / electores unicos por mesa. Debe validarse contra totales oficiales antes de publicar.

## Compatibilidad territorial 2023-2025

- Circuitos 2023: 1039
- Circuitos 2025: 1047
- Circuitos en ambos anios: 1033
- Circuitos solo en 2023: 6
- Circuitos solo en 2025: 14

La comparacion por circuito es viable en datos tabulares y la nueva capa permite mapearla con cobertura casi completa.

## Fuerzas principales detectadas

### 2023

| fuerza | votos_positivos |
| --- | --- |
| UNION POR LA PATRIA | 4.919.211 |
| LA LIBERTAD AVANZA | 4.776.711 |

### 2025

| fuerza | votos_positivos |
| --- | --- |
| ALIANZA LA LIBERTAD AVANZA | 3.605.127 |
| ALIANZA FUERZA PATRIA | 3.558.527 |
| FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD | 438.747 |
| PROPUESTA FEDERAL PARA EL CAMBIO | 243.326 |
| ALIANZA PROVINCIAS UNIDAS | 212.959 |
| PARTIDO NUEVO BUENOS AIRES | 116.670 |
| FRENTE PATRIOTA FEDERAL | 104.965 |
| ALIANZA UNIÓN FEDERAL | 78.125 |
| COALICIÓN CÍVICA - A.R.I. | 69.358 |
| ALIANZA POTENCIA | 61.209 |
| MOVIMIENTO POLÍTICO SOCIAL Y CULTURAL PROYECTO SUR | 52.563 |
| MOVIMIENTO AVANZADA SOCIALISTA | 49.482 |

## Tipos de voto

### 2023

| tipo | votos |
| --- | --- |
| POSITIVO | 9.695.922 |
| EN BLANCO | 178.640 |
| NULO | 136.904 |
| RECURRIDO | 3.427 |
| IMPUGNADO | 2.494 |

### 2025

| tipo | votos |
| --- | --- |
| POSITIVO | 8.696.636 |
| NULO | 206.177 |
| EN BLANCO | 103.947 |
| RECURRIDO | 4.277 |
| IMPUGNADO | 2.122 |
| COMANDO | 0 |

## Cartografia disponible

### Departamentos

- Archivo: `02_Datos\02_Poblaciones 2023\04_DepartamentosElecciones.geojson`
- Features: 135
- Tamanio: 6.34 MB
- Tipos geometricos: {'MultiPolygon': 135}
- Campos con apariencia de circuito: ninguno

Campos principales observados:

B_LISTA134, B_LISTA135, B_PARTIDO_, B_TOTAL_VO, B_VOTOS_PA, CODDPTO, CODPROV, COD_DPTO, DEPARTAMEN, DEPARTAM_1, DEPARTAM_2, DEPARTAM_3, DEPARTAM_4, DPTO, G_LISTA132, G_LISTA133, G_LISTA134, G_LISTA135, G_LISTA136, G_PARTIDO_, G_VOTOS_PA, O_FEDERAL, O_IZQUIERD, O_KIRCHNER, O_LIBERTAR, O_REPUBLIC, PROV, V_POSITIVO

Conclusion: esta capa sirve para un MVP departamental, pero no para pintar circuitos.

### Circuitos electorales

- Archivo: `02_Datos\03_circuitoselectoralespba\circuitos-electorales-pba.geojson`
- Features: 1150
- Tamanio: 8.41 MB
- Tipos geometricos: {'MultiPolygon': 1150}
- Campos principales de union: `departamen`, `circuito`.
- Features sin clave de union aparente: 0

Compatibilidad contra resultados DINE usando `seccion_nombre/departamen` normalizado + `circuito_id/circuito` normalizado:

- Claves cartograficas de circuito: 1146
- Match con circuitos 2023: 1035 de 1039 DINE; cobertura DINE 99.62%; cobertura geometrica 90.31%.
- Match con circuitos 2025: 1045 de 1047 DINE; cobertura DINE 99.81%; cobertura geometrica 91.19%.
- Circuitos DINE 2023 sin geometria: 4.
- Circuitos DINE 2025 sin geometria: 2.
- Geometrias sin resultados 2023: 111.
- Geometrias sin resultados 2025: 101.

Muestras de no apareados:

- DINE 2023 sin geometria: [('FLORENTINO AMEGHINO', '361A'), ('GENERAL SAN MARTIN', '383'), ('GENERAL SAN MARTIN', '388'), ('PUAN', '779')]
- DINE 2025 sin geometria: [('FLORENTINO AMEGHINO', '361A'), ('PUAN', '779')]
- Geometrias sin DINE 2023: [('ADOLFO ALSINA', '2'), ('ADOLFO ALSINA', '4'), ('ALMIRANTE BROWN', '22C'), ('AYACUCHO', '48'), ('AYACUCHO', '49'), ('AYACUCHO', '51'), ('AYACUCHO', '53'), ('AYACUCHO', '54'), ('AZUL', '64'), ('AZUL', '68'), ('AZUL', '69'), ('BARADERO', '108'), ('BARADERO', '109'), ('BARADERO', '114'), ('BENITO JUAREZ', '438'), ('BENITO JUAREZ', '442'), ('BOLIVAR', '130'), ('CANUELAS', '160'), ('CANUELAS', '161'), ('CANUELAS', '162'), ('CARLOS TEJEDOR', '171A'), ('CASTELLI', '186'), ('CHACABUCO', '192'), ('CHACABUCO', '194'), ('CHACABUCO', '196'), ('CHASCOMUS', '206'), ('CHASCOMUS', '208'), ('CHASCOMUS', '209A'), ('CHIVILCOY', '213'), ('CHIVILCOY', '214')]
- Geometrias sin DINE 2025: [('ADOLFO ALSINA', '2'), ('ADOLFO ALSINA', '4'), ('AYACUCHO', '48'), ('AYACUCHO', '49'), ('AYACUCHO', '51'), ('AYACUCHO', '53'), ('AYACUCHO', '56'), ('AZUL', '64'), ('AZUL', '68'), ('AZUL', '69'), ('BARADERO', '108'), ('BARADERO', '109'), ('BARADERO', '114'), ('BENITO JUAREZ', '438'), ('BENITO JUAREZ', '442'), ('BOLIVAR', '130'), ('CANUELAS', '161'), ('CARLOS TEJEDOR', '171A'), ('CASTELLI', '186'), ('CHACABUCO', '192'), ('CHACABUCO', '194'), ('CHACABUCO', '196'), ('CHASCOMUS', '206'), ('CHASCOMUS', '208'), ('CHASCOMUS', '209A'), ('CHIVILCOY', '213'), ('CHIVILCOY', '214'), ('CHIVILCOY', '217'), ('CHIVILCOY', '223'), ('CHIVILCOY', '225')]

## Observaciones para homologacion politica

- La comparacion solicitada entre La Libertad Avanza y peronismo/kirchnerismo requiere una tabla de homologacion de fuerzas.
- Homologacion inicial sugerida:
  - `LA LIBERTAD AVANZA` (2023) -> bloque `LLA`.
  - `ALIANZA LA LIBERTAD AVANZA` (2025) -> bloque `LLA`.
  - `UNION POR LA PATRIA` (2023) -> bloque `PERONISMO_K`.
  - `ALIANZA FUERZA PATRIA` (2025) -> bloque `PERONISMO_K`.
- El resto de fuerzas deberia conservarse como agrupacion propia y, en paralelo, clasificarse en bloques amplios si el analisis politico lo requiere.

## Circuitos no apareados

Muestra de claves con formato `(distrito_id, seccion_id, circuito_id)`:

- Solo 2023: [('2', '47', '342'), ('2', '5', '56'), ('2', '52', '383'), ('2', '52', '388'), ('2', '60', '448'), ('2', '84', '0719A')]
- Solo 2025: [('2', '105', '882'), ('2', '109', '927'), ('2', '111', '0933M'), ('2', '17', '160'), ('2', '17', '162'), ('2', '3', '0022C'), ('2', '39', '309'), ('2', '48', '346'), ('2', '5', '54'), ('2', '52', '0388A'), ('2', '52', '0388B'), ('2', '52', '0388C'), ('2', '63', '493'), ('2', '81', '678')]

## Archivos auxiliares

- `Libro3_normalizado_mapas.xls`: firma `D0 CF 11 E0 A1 B1 1A E1`. Es un Excel binario historico `.xls`; requiere conversion o lector `xlrd` para auditar hojas.
- Diccionario `.xlsx`: firma `50 4B 03 04 14 00 06 00`. Es un `.xlsx` valido y puede inspeccionarse luego si necesitamos documentar campos de la capa departamental.

## Recomendacion para el proximo paso

1. Construir un ETL que produzca agregados por circuito para 2023 y 2025, mas una tabla de comparacion.
2. Preparar una capa GeoJSON liviana de circuitos con clave normalizada `partido_norm + circuito_norm`.
3. Desarrollar el MVP estatico con Leaflet/Argenmap usando datos preprocesados.
4. Revisar manualmente los pocos circuitos no apareados antes de publicar indicadores finales.

## Indicadores calculables con los insumos actuales

- Electores por mesa/circuito/partido/provincia.
- Votantes como suma de votos por mesa/circuito/partido/provincia.
- Participacion y ausentismo.
- Voto positivo por fuerza.
- Blanco, nulo y otros tipos disponibles en `votos_tipo`.
- Ranking de variaciones 2023-2025 por circuito si se usa la tabla electoral.
- Mapa de variaciones por circuito con la nueva cartografia, sujeto a resolver no apareados.
