# Comparacion de circuitos electorales PBA2

## Archivos

- GeoJSON actual de la app: `G:\Unidades compartidas\Análisis de datos\99_FCH\07_Elecciones\03_Tableros\05_MapaElectoral_Cockpit_CSV\data\circuitos_pba.geojson`
- GeoJSON fuente anterior: `G:\Unidades compartidas\Análisis de datos\99_FCH\07_Elecciones\02_Datos\03_circuitoselectoralespba\01_CircuitosElectorales2025_PBA.geojson`
- GeoJSON fuente nuevo: `G:\Unidades compartidas\Análisis de datos\99_FCH\07_Elecciones\02_Datos\03_circuitoselectoralespba\01_CircuitosElectorales2025_PBA2.geojson`

## Resumen fuente anterior vs fuente nueva

- Features anteriores: 1156
- Features nuevas: 1153
- Circuitos agregados: 1
- Circuitos eliminados: 0
- Geometrias modificadas: 15
- Campos nuevos: ninguno
- Campos eliminados: ['Circuito_1', 'OID_', 'Votos']
- Tipos geometricos nuevos: {'MultiPolygon': 1153}

## Resumen app actual vs nueva capa normalizada

- Features actuales app: 1156
- Features nuevas normalizadas: 1153
- Circuitos agregados: 1
- Circuitos eliminados: 0
- Geometrias modificadas: 15
- Circuitos con datos electorales sin geometria nueva: 2
- Geometrias nuevas sin datos electorales: 102

## Clave de union

La app usa `feature.properties.key` para vincular geometria de circuito con `data.electoral_data.circuit.elections`. En la capa normalizada esa clave se deriva de `properties.circuito` mediante normalizacion de ceros iniciales y sufijos alfabeticos.
