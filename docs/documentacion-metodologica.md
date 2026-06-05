# Documentacion metodologica

## Objetivo de la aplicacion

Atlas Electoral PBA permite explorar territorialmente resultados electorales de la Provincia de Buenos Aires. Su objetivo es facilitar lecturas comparativas entre elecciones, detectar patrones de participacion, ausentismo, composicion del voto y desempeno relativo de fuerzas politicas en distintas escalas territoriales.

La herramienta esta orientada a la exploracion analitica. No reemplaza la validacion estadistica ni la revision documental de las fuentes originales.

## Alcance territorial

El alcance territorial es la Provincia de Buenos Aires. La aplicacion integra informacion electoral y cartografica para representar resultados en el territorio provincial.

## Unidades de analisis

### Partido

La vista Partido agrega o representa informacion a nivel municipal. Permite leer patrones generales, comparar desempenos entre partidos y ubicar territorios de mayor peso electoral.

### Circuito electoral

La vista Circuito trabaja con una unidad territorial electoral mas detallada. Permite identificar heterogeneidad interna dentro de los partidos y observar variaciones que pueden quedar ocultas en la agregacion municipal.

## Fuentes de datos

1. DINE / resultados electorales: <https://www.argentina.gob.ar/dine/resultados-electorales>
2. Cartografia de partidos de Provincia de Buenos Aires desde datos abiertos: <https://catalogo.datos.gba.gob.ar/sv/dataset/partidos>

La aplicacion integra datos electorales y cartograficos. Los resultados electorales se procesan para construir indicadores por unidad territorial y las capas cartograficas permiten representarlos espacialmente.

## Metricas principales

### Electores

Cantidad de personas habilitadas para votar en la unidad territorial correspondiente.

### Votantes

Cantidad de electores que emitieron voto.

### Participacion

Proporcion de votantes sobre electores habilitados.

### Ausentismo

Proporcion de electores habilitados que no emitieron voto. Se interpreta como complemento de la participacion.

### Voto positivo

Votos afirmativos emitidos a fuerzas o listas participantes, expresados sobre el universo correspondiente segun el indicador seleccionado.

### Voto blanco

Votos emitidos sin seleccion de una opcion afirmativa.

### Voto nulo

Votos invalidados de acuerdo con los criterios electorales aplicables.

### Voto recurrido

Votos cuya validez fue objetada y queda sujeta a revision segun el procedimiento electoral.

### Voto impugnado

Votos asociados a una impugnacion de identidad u otra situacion prevista por la normativa electoral.

### Distribucion de votos positivos por fuerza

Composicion de los votos afirmativos segun fuerza politica. La aplicacion permite observar el porcentaje de cada fuerza sobre votos positivos y, cuando corresponde, sobre el total emitido.

### Competitividad

Diferencia entre la primera y la segunda fuerza sobre votos positivos. Valores mas bajos indican mayor competencia electoral entre las dos fuerzas principales.

### Distancia a primera fuerza

Mide la distancia entre la fuerza seleccionada y la primera fuerza en cada territorio. Si la fuerza seleccionada ya es primera fuerza, ese territorio se excluye de esta lectura. En el mapa esos casos quedan como sin dato o neutros para evitar interpretar como brecha una situacion en la que la fuerza ya lidera.

### Variaciones entre elecciones

Cambios entre una eleccion base y una eleccion comparada. Las variaciones se expresan principalmente en puntos porcentuales.

## Criterios de comparacion temporal

La comparacion temporal toma una eleccion base y una eleccion objetivo. Para cada metrica comparable, la aplicacion calcula la diferencia entre ambos momentos en la misma unidad territorial.

La lectura debe considerar que:

- los cargos, alianzas o denominaciones de fuerzas pueden variar entre elecciones;
- los cambios territoriales se interpretan mejor junto con volumen de electores y participacion;
- una variacion porcentual pequena puede ser relevante en territorios de gran peso electoral;
- una variacion grande en territorios pequenos requiere cautela analitica.

## Criterio de ranking

El ranking ordena territorios segun la metrica activa y el modo de analisis. Puede ordenar de mayor a menor, de menor a mayor o por intensidad absoluta del cambio, segun la pregunta o indicador seleccionado.

El ranking es una herramienta de priorizacion exploratoria. No implica causalidad ni jerarquia politica por fuera de la metrica elegida.

## Vista Partido/Circuito

La vista Partido permite una lectura agregada y comparable entre municipios. La vista Circuito permite una lectura mas fina y localizada. Cambiar de vista modifica la unidad de calculo, el mapa, el ranking y la interpretacion territorial de los indicadores.

## Como leer el atlas

1. Seleccionar si se desea analizar una eleccion o comparar dos elecciones.
2. Elegir la eleccion objetivo y, si corresponde, la eleccion base.
3. Definir que indicador mostrar en el mapa.
4. Si se analiza voto por fuerza o tipo de voto, ajustar los controles dependientes.
5. Alternar entre Partido y Circuito segun el nivel de detalle requerido.
6. Usar el mapa para ubicar patrones territoriales y el ranking para priorizar casos.
7. Revisar KPIs, composicion del voto y lectura rapida para contextualizar.
8. Usar el asistente para activar preguntas analiticas frecuentes.
9. Interpretar los resultados como indicios exploratorios y contrastarlos con fuentes y conocimiento territorial.

## Limitaciones

- La aplicacion depende de la disponibilidad, consistencia y actualizacion de las fuentes utilizadas.
- Pueden existir diferencias entre unidades cartograficas y unidades electorales.
- La lectura a nivel de circuito requiere validacion de correspondencias entre datos electorales y geometria.
- Los indicadores tienen un uso exploratorio y no explican por si mismos las causas de los cambios observados.
- Las comparaciones entre elecciones deben considerar cambios de oferta electoral, alianzas, cargos y contexto politico.

## Recomendaciones de interpretacion

- Combinar porcentajes con volumen de electores.
- Revisar participacion y ausentismo antes de interpretar cambios de voto.
- Comparar patrones entre Partido y Circuito para distinguir tendencias agregadas de heterogeneidad interna.
- Usar la distancia a primera fuerza solo en territorios donde la fuerza seleccionada no lidera.
- Tratar los territorios sin dato como casos a revisar, no como evidencia sustantiva.
