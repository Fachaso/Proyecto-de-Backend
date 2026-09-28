<div align="right">
    <img width="32px" src="img/logo_intro.desarrollo.software.png">
</div>

# Proyecto Backend
## Información de los estudiantes:

* Ramiro Tomas Martinez - 115961 - rtmartinez@fi.uba.ar - https://github.com/Fachaso
* Alan Fabrizio Messina Bossio - 116403 - amessina@fi.uba.ar
* Yohan Rodrigo Cornejo Campana -116364 - ycornejo@fi.uba.ar
* Lucas Nahuel Uran -116478 - luran@fi.uba.ar
* Pablo Martin Cantoni Noblia -115568 -pcantoni@fi.uba.ar
* Tiziana Gonzalez -116294 - tigonzalez@fi.uba.ar
* Julieta Nágera - 114474 - jnagera@fi.uba.ar
* Guadalupe Fernandez - 115583 - bgfernandez@fi.uba.ar
* Sarai Slavkis -114351 -sslavkis@fi.uba.ar
* Villegas Mateo -115821 -mvillegas@fi.uba.ar
---

## Versiones utilizadas 
* Python 3.10 o superior
* Flask (para levantar la API)
* MySQL (para la base de datos)
* Swagger / OpenAPI 3.0 (para el contrato)

## Pasos de instalación 
1. Entrar a la carpeta del código: `cd club-deportivo-api`
2. Armar el entorno virtual para no romper nada: `python -m venv venv`
3. Activarlo en Windows con `venv\Scripts\activate` (o en Mac/Linux con `source venv/bin/activate`)
4. Instalar las librerías del proyecto: `pip install -r requirements.txt`

## Ejecución 
Para arrancar el servidor local, corremos el archivo principal con Python:
```bash
python run.py
```
La API se levanta por defecto en: `http://localhost:5000/`


## Configuración
1. Configurar la base de datos MySQL corriendo los scripts que están dentro de la carpeta `scripts/`.
2. Crear un archivo llamado `.env` en la raíz de la carpeta `club-deportivo-api/` usando como plantilla el archivo `.env.example` para poner las credenciales locales de la base de datos.


## Ejemplos de solicitudes y supuestos adoptados
### Supuestos del Club
* El club abre de 08:00 a 23:00. Los turnos son de horas completas (de 1 a 3 horas) y arrancan clavados en punto.
* Todos los precios se manejan en centavos para evitar problemas con los decimales en la base de datos (ej: $10.000 se guarda como 1000000).
* Si una cancha cambia de precio, las reservas viejas mantienen su tarifa congelada al momento en que se hicieron.
* El sistema valida que no se superpongan turnos en una misma cancha ni que un socio reserve dos cosas a la misma hora.



### Ejemplos de solicitudes de prueba

1. **Ver canchas disponibles (GET):**
`http://localhost:5000/canchas/disponibles?fecha=2026-10-15&hora_inicio=18:00:00&hora_fin=20:00:00`

2. **Crear una reserva (POST a /reservas):**
```json
{
  "id_socio": 1,
  "id_cancha": 2,
  "fecha_hora_inicio": "2026-10-15T18:00:00.000000-03:00",
  "fecha_hora_fin": "2026-10-15T20:00:00.000000-03:00"
}
```



## Índice
* [0. Enunciado](#0-Enunciado)
* [1. Instrucciones](#1-Instrucciones)
* [2. Funcionamiento](#2-Funcionamiento)
* [3. Estructura](#3-Estructura)
* [4. Decisiones de diseño y/o complejidades de implementación](#4-Decisiones-de-diseño-yo-complejidades-de-implementación)


## 0. Enunciado



## 1. Instrucciones
### 1.1. Compilación
Al ser un proyecto desarrollado en Python, no requiere ningún proceso de compilación previa. El servidor se interpreta y ejecuta directamente.

### 1.2. Para ejecutar
Para levantar el entorno, parate en la carpeta principal y corre:
```bash
python run.py
```




## 2. Funcionamiento
La API interactúa mediante peticiones HTTP en formato JSON. Cuando llega una solicitud (por ejemplo, para crear una reserva), el sistema primero valida el horario contra las reglas del club, chequea en la base de datos que no haya superposiciones de turnos y, si está todo en orden, calcula el precio final y persiste el registro en MySQL.



## 3. Estructura
* `run.py`: Archivo principal para encender el servidor Flask.
* `app/`: Carpeta contenedora de todo el código de la aplicación.
* `app/routes/`: Definición de los endpoints y manejo de las peticiones HTTP.
* `app/services/`: Capa lógica donde se validan las reglas de negocio y horarios.
* `app/repositories/`: Consultas SQL directas hacia la base de datos.
* `scripts/`: Scripts SQL para la creación inicial de las tablas del club.



## 4. Decisiones de diseño y/o complejidades de implementación
