# Levantar la estructura base del Nodo de Borde

Esta es la propuesta paso a paso para crear la estructura base del repositorio `alpr-edge-node`. Como me pediste, te explicaré cada concepto para que entiendas qué hace cada cosa y por qué lo usamos.

## Conceptos Básicos (Breve Explicación)

*   **Docker:** Es una herramienta que nos permite "empaquetar" una aplicación con todo lo que necesita para funcionar (librerías, configuraciones) dentro de algo llamado **Contenedor**. Esto asegura que si funciona en tu computador, funcionará exactamente igual en el servidor o en una Jetson Nano.
*   **Docker Compose:** Es una herramienta para definir y ejecutar aplicaciones Docker que tienen múltiples contenedores (servicios). En nuestro caso, tenemos 2 servicios: el `pipeline` (backend en Python) y el `dashboard` (frontend en React). En lugar de levantar uno por uno, usamos un archivo `docker-compose.yml` para levantar ambos al mismo tiempo.
*   **Volumen Docker:** Los contenedores se borran y se recrean constantemente. Si guardamos la base de datos (SQLite) dentro del contenedor, se perdería. Un volumen nos permite persistir los datos vinculando una carpeta de tu computador real con una carpeta dentro del contenedor.

## Proposed Changes

Vamos a crear la siguiente estructura dentro de la carpeta `alpr-edge-node`:

### 1. Backend IA (Python)
Aquí correrá tu modelo YOLO y OpenCV.

#### [NEW] [pipeline/main.py](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/pipeline/main.py)
#### [NEW] [pipeline/detector.py](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/pipeline/detector.py)
#### [NEW] [pipeline/ocr.py](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/pipeline/ocr.py)
#### [NEW] [pipeline/validator.py](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/pipeline/validator.py)
#### [NEW] [pipeline/requirements.txt](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/pipeline/requirements.txt)
#### [NEW] [pipeline/Dockerfile](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/pipeline/Dockerfile)
Este archivo le enseñará a Docker cómo preparar el entorno de Python (instalar paquetes, copiar tu código y configuraciones) para que el pipeline funcione. También configuraremos el acceso a la cámara.

### 2. Frontend Local (React)
Una interfaz ligera para visualizar lo que detecta la IA en tiempo real.

#### [NEW] [dashboard/Dockerfile](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/dashboard/Dockerfile)
*Nota:* Crearemos el proyecto base de React usando `Vite` (una herramienta muy rápida para proyectos frontend modernos) y luego añadiremos su Dockerfile correspondiente.

### 3. Orquestación y Datos
Para unir ambos mundos.

#### [NEW] [data/.keep](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/data/.keep)
Una carpeta vacía inicial para guardar la base de datos `local.db` con persistencia.
#### [NEW] [docker-compose.yml](file:///c:/Users/Benjamin/Desktop/alpr-access-system/alpr-edge-node/docker-compose.yml)
Este será el "director de orquesta". Le dirá a Docker: "levanta el contenedor del pipeline, luego el del dashboard, y conecta esta carpeta de datos para SQLite".

## Open Questions

> [!TIP]
> **Preguntas para ti:**
> 1. Para el Dashboard (React), ¿te gustaría que use **TypeScript** o **JavaScript** puro? (Recomiendo TypeScript ya que veo que en el panel de administración usan TypeScript).
> 2. ¿Deseas que añada librerías específicas a `requirements.txt` de Python desde ya (ej. `opencv-python`, `ultralytics` para YOLO, `fastapi`) o prefieres mantenerlo mínimo y añadir después?

## User Review Required

Si estás de acuerdo con este plan, dale al botón **Proceed** y yo me encargaré de ejecutar todos los comandos e inicializar los proyectos por ti de manera automática. Luego te explicaré cómo levantarlo para probarlo.
