# Generador EPG MovistarTV

Generador del EPG de la programación de MovistarTV. El script hace uso de las mismas llamadas AJAX para visualizar la programación en la web `http://comunicacion.movistarplus.es/programacion/`. Primero, obtiene la lista completa de canales y descarga la programación para esos canales. Posteriormente, procesa la información obtenida para generar un fichero en formato XMLTV. El script tiene 2 modos de funcionamiento: el sencillo y el complejo. El sencillo genera un archivo con la información básica de cada emisión. El complejo, para cada emisión, si está disponible, se descarga la ficha técnica. Este último hace uso de multiprocesado y cache para agilizar el funcionamiento.

El repositorio está configurado con Travis CI para ejecutarse de manera automática cada día en modo sencillo y publicando el resultado como una página web de Github. Se pueden ver la ultima versión en:

```
https://oscarbc96.github.io/epg_generator/epg.xml
```

## Instalación

Lenguaje: Python 3

```
pip install -r requirements.txt
```

## Ejecutar

```
python epg_generator.py
```

El script tiene 2 modos de funcionamiento.

1. *Sencillo*: rápido y simple. Genera un archivo con la información básica de cada emisión.
2. *Completo*: lento y completo. Genera el mismo archivo que el sencillo pero para cada emisión, si está disponible, se descarga la ficha técnica. Crea tantos procesos como cores tenga disponibles y una vez descargada la ficha se guarda en una cache. De esta manera, el siguiente dia si ya tenemos la información no la volvera a pedir y se reduce el tiempo de ejecución.

## Configuración

En la carpeta del proyecto existe un archivo `conf.py`. En este se puede modificar el modo de ejecución (`DOWNLOAD_EXTRA_INFO`) y el numero de días a descargar la información (`DAYS_TO_DOWNLOAD`).

Cuando se define el numero de días hay que tener en cuenta que el script va a sumar uno. Ya que descargara el día anterior para completar la información del primero por la noche.

Ejemplo de salida del script:
```
EPG Generator
N. cores: 8
Download extra info: True
Days to download: 3
Start: 2019-01-09 23:48:07.350472
Downloading movistar data...
Getting movistar channels...
Getting movistar programmes of 2019-01-08...
Getting movistar programmes of 2019-01-09...
Getting movistar programmes of 2019-01-10...
Getting movistar programmes of 2019-01-11...
Downloading extra info for 1459206
Downloading extra info for 1596824
...
Downloading extra info for 1519698
Downloading extra info for 864221
Generating epg data...
Dumping epg data to xml...
Stop: 2019-01-09 23:58:16.360176
Execution time: 0:10:09.009704
```