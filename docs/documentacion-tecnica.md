# Documentacion tecnica

## Descripcion general

Atlas Electoral PBA es una aplicacion web estatica para explorar resultados electorales de la Provincia de Buenos Aires con lectura territorial por partido y por circuito electoral. El visor combina datos electorales procesados, geometria territorial y componentes interactivos para analizar participacion, ausentismo, composicion del voto, desempeno de fuerzas politicas, competitividad y variaciones entre elecciones.

La aplicacion esta pensada como un tablero exploratorio: permite recorrer el mapa, aplicar filtros, consultar rankings, abrir un asistente de preguntas analiticas, cruzar metricas en un grafico de dispersion y exportar informacion o informes.

## Arquitectura general

La arquitectura es de despliegue estatico. No requiere backend en tiempo de ejecucion: el navegador carga HTML, CSS, JavaScript y archivos locales de datos.

Componentes principales:

- `index.html`: estructura de la interfaz, referencias a Leaflet, estilos y modulo JavaScript principal.
- `css/styles.css`: sistema visual, layout, paneles, mapa, rankings, asistente, modo informe y componentes superpuestos.
- `js/app.js`: estado de la aplicacion, carga de datos, transformaciones, renderizado del mapa y controles.
- `data/electoral_data.json`: datos electorales procesados para partidos y circuitos.
- `data/partidos_pba.geojson`: geometria de partidos de la Provincia de Buenos Aires.
- `data/circuitos_pba.geojson`: geometria de circuitos electorales.
- `docs/`: documentacion tecnica, metodologica y auditorias de datos.
- `tools/`: scripts de construccion y auditoria de datos.

## Estructura de carpetas

```text
05_MapaElectoral_Cockpit_CSV/
├── index.html
├── css/
│   └── styles.css
├── js/
│   └── app.js
├── data/
│   ├── electoral_data.json
│   ├── partidos_pba.geojson
│   └── circuitos_pba.geojson
├── docs/
│   ├── documentacion-tecnica.md
│   ├── documentacion-metodologica.md
│   ├── auditoria_datos.md
│   └── auditoria_datos.json
├── tools/
│   ├── build_data.py
│   ├── audit_data.py
│   └── audit_circuit_matches.py
└── README.md
```

## Tecnologias utilizadas

- HTML5 para la estructura de la aplicacion.
- CSS3 sin framework para layout, componentes y responsividad.
- JavaScript en modulo ES para la logica de interaccion.
- Leaflet 1.9.4 para visualizacion cartografica.
- GeoJSON para geometria territorial.
- JSON y CSV como formatos de datos electorales y de procesamiento.
- Python para scripts de construccion y auditoria de datos.

## Diseno de interfaz

### Layout general

La interfaz principal se organiza en tres zonas: panel lateral de filtros, mapa central y paneles de detalle/ranking/KPIs. El layout usa CSS Grid y se adapta a pantallas pequenas mediante reglas responsivas.

### Panel de filtros

El panel lateral contiene:

- selector de modo de vista: por eleccion o comparacion temporal;
- selectores de elecciones base y comparada;
- selector de indicador del mapa;
- controles dependientes para tipo de voto, fuerza politica y forma de medicion;
- accesos al asistente, cruce de metricas, exportacion CSV y modo informe.

### Mapa

El mapa usa Leaflet con capas GeoJSON para partidos y circuitos. Permite alternar nivel territorial, buscar partidos, seleccionar territorios y abrir un detalle municipal de circuitos.

### KPIs

La tira de KPIs resume indicadores sinteticos del universo territorial filtrado o seleccionado, como electores, participacion, ausentismo y otros valores relevantes segun la vista activa.

### Graficos

La aplicacion incluye barras apiladas para composicion del voto total y distribucion de votos positivos, y un grafico de dispersion SVG para cruces exploratorios entre metricas.

### Ranking

El ranking ordena partidos o circuitos segun la metrica activa y el criterio definido por el modo de lectura. Permite seleccionar territorios desde la lista.

### Asistente

El asistente contiene preguntas analiticas predefinidas. Cada pregunta ajusta filtros, unidad territorial, ordenamiento y, en algunos casos, abre el cruce de metricas.

### Exportacion de informe

La aplicacion permite exportar CSV y activar un modo informe con secciones de lectura ejecutiva, mapa, KPIs y graficos principales.

## Flujo de datos

### Carga de datos

Al inicializar, `app.js` carga en paralelo:

- `data/electoral_data.json`;
- `data/partidos_pba.geojson`;
- `data/circuitos_pba.geojson`.

### Transformacion

Los datos electorales ya llegan procesados desde los scripts de `tools/`. En el navegador se realizan transformaciones ligeras para calcular valores derivados, preparar rankings, generar puntos de dispersion y construir textos de lectura.

### Calculo de metricas

Las metricas principales se calculan desde estructuras de datos por eleccion y unidad territorial. La aplicacion evalua participacion, ausentismo, competitividad, tipos de voto, porcentajes por fuerza y variaciones entre elecciones.

### Renderizado

El renderizado se actualiza desde una funcion de refresco general que sincroniza mapa, leyenda, KPIs, detalle territorial, barras, ranking, asistente y grafico de dispersion.

## Componentes principales de JavaScript

- `state`: objeto central con mapa, datos, seleccion territorial, filtros activos y caches.
- `METRICS`, `SCATTER_METRICS` y `QUESTIONS`: configuraciones declarativas de metricas, cruces y preguntas.
- Funciones de formato: porcentajes, puntos porcentuales y numeros.
- Funciones de acceso a datos: recuperan filas por unidad y eleccion.
- Funciones de metrica: calculan valores actuales, variaciones y valores de ranking.
- Funciones de mapa: crean capas, estilos, tooltips, seleccion y busqueda.
- Funciones de UI: actualizan filtros, leyendas, paneles, KPIs, ranking y textos.
- Funciones de exportacion: generan CSV y modo informe.
- Inicializacion: carga datos, construye controles y registra eventos.

## Manejo de estado

El estado se mantiene en memoria dentro del objeto `state`. Los controles modifican valores de ese objeto y luego llaman a la actualizacion de la interfaz. No se usa almacenamiento persistente ni gestion de estado externa.

Campos relevantes:

- eleccion base y eleccion objetivo;
- modo de vista;
- indicador, tipo de voto, fuerza y medida positiva;
- partido o circuito seleccionado;
- nivel de mapa;
- seleccion del grafico de dispersion;
- referencias a capas Leaflet y caches de centroides.

## Infraestructura

### Despliegue estatico

La aplicacion puede servirse desde cualquier hosting estatico. Solo requiere que las rutas relativas a `css/`, `js/`, `data/` y `docs/` se conserven.

### GitHub Pages

Es compatible con GitHub Pages si la carpeta publicada mantiene la misma estructura interna. Los recursos se cargan con rutas relativas.

### Dependencias externas

La dependencia externa de ejecucion es Leaflet, cargada desde `https://unpkg.com`. No se agregan frameworks ni dependencias pesadas.

### Servicios de mapas base

El mapa base usa servicios de teselas del Instituto Geografico Nacional mediante ArgenMap.

### Archivos de datos locales

Los datos electorales y cartograficos se almacenan localmente en `data/`. Esto evita depender de una API externa durante el uso de la aplicacion.

## Consideraciones de mantenimiento

- Mantener sincronizados los datos electorales y las geometria territorial.
- Revisar auditorias de datos antes de publicar una nueva version.
- Actualizar cache-busters de `index.html` cuando cambien `css/styles.css` o `js/app.js`.
- Evitar cambios de estructura en `data/` sin actualizar las funciones de lectura.
- Validar que la aplicacion funcione desde rutas relativas para GitHub Pages.

## Posibles mejoras futuras

- Incorporar mas elecciones y cargos.
- Agregar validacion mas fina de correspondencias entre circuitos electorales y geometria.
- Permitir descarga de informes en formatos adicionales.
- Incorporar capas socioeconomicas o censales.
- Agregar busqueda avanzada y filtros territoriales combinados.
- Publicar una guia de actualizacion de datos paso a paso.
