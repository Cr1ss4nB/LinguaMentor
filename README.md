# Proyecto Final - Sistemas Distribuidos

### Integrantes
- 202010495: Cristian Andrés Basto Largo
- 201821701: Andrea Katherine Bello Sotelo

--- 

# LinguaMentor – Evaluador y Tutor Inteligente de Idiomas

## Idea Proyecto

Las herramientas actuales para el aprendizaje de idiomas suelen ofrecer ejercicios genéricos y poca personalización. LinguaMentor busca ofrecer una experiencia más adaptativa y precisa, actuando como un tutor virtual que entiende el nivel real del usuario y lo guía en su progreso.
A partir de un test inicial, la plataforma clasifica al estudiante según sus habilidades en escritura, lectura y habla, generando un plan de ejercicios ajustado a sus debilidades y fortalezas. El sistema entrega retroalimentación detallada con explicaciones y ejemplos, fomentando un aprendizaje autónomo y personalizado.
La evaluación del habla mediante IA representa un avance importante, ya que permite analizar la pronunciación y fluidez sin intervención humana, otorgando al estudiante una experiencia interactiva y realista. Este enfoque contribuye a mejorar la educación en idiomas desde una perspectiva tecnológica, ofreciendo un entorno inteligente, escalable y de fácil acceso para estudiantes de diferentes niveles.

--- 

## Arquitectura del Proyecto
La arquitectura de LinguaMentor se basa en un enfoque modular desplegado con contenedores Docker.
El frontend estará planeado para ser desarrollado en React, permitiendo una interacción directa con el usuario para el envío de textos o grabaciones de voz. Estas solicitudes se envían a través del proxy inverso Traefik, que gestiona las peticiones HTTP y las redirige al Backend, encargado de procesar los datos y coordinar las operaciones internas.
El Backend utiliza RabbitMQ como intermediario para manejar las tareas de análisis de texto y voz. Dichas tareas son procesadas por los servicios de inteligencia artificial: LangChain y otra IA que se enfoque en el análisis de voz (reconocimiento de voz). Finalmente, los resultados y puntuaciones se almacenan en la base de datos, y el sistema devuelve una retroalimentación personalizada al usuario, cerrando el ciclo de interacción.
Se comienza cuando el usuario ingresa a la plataforma y realiza el test inicial que evalúa las tres competencias: escritura, lectura y habla. El frontend recoge las respuestas y las envía al backend a través de Traefik. Desde allí, RabbitMQ distribuye las solicitudes hacia los servicios de inteligencia artificial: LangChain procesa los textos para evaluar gramática y coherencia, mientras que el servicio de voz analiza pronunciación y fluidez. Con base en los resultados, el sistema clasifica el nivel del usuario y genera actividades personalizadas que se almacenan en la base de datos. A medida que el usuario completa las tareas, el sistema vuelve a procesar las entregas y proporciona la retroalimentación.

(imagen del diagrama de eraser.io)
--- 

## 🧩 Arquitectura de Microservicios - LinguaMentor

LinguaMentor está diseñado bajo una arquitectura distribuida, basada en contenedores Docker y comunicación asíncrona con RabbitMQ.  
Cada microservicio cumple una función específica dentro del flujo de aprendizaje inteligente por voz.

| Microservicio | Descripción | Tecnologías principales |
|----------------|-------------|--------------------------|
| **Gateway API** | Punto de entrada de la aplicación. Gestiona las solicitudes del frontend y las enruta hacia otros microservicios. | FastAPI, Docker |
| **Gestión de Usuarios** | Administra registro, inicio de sesión, preferencias de idioma, nivel actual y progreso del usuario. | FastAPI, MongoDB |
| **Evaluación Inicial** | Realiza el test de nivel a través de la voz, determina si el usuario es novato, intermedio o avanzado. | FastAPI, LangChain, RabbitMQ |
| **Análisis de Voz** | Recibe archivos de audio, los transcribe y analiza pronunciación, gramática y fluidez. | FastAPI, Whisper, RabbitMQ |
| **Gestión de Cursos y Feedback** | Genera ejercicios personalizados y retroalimentación basada en errores detectados. | FastAPI, LangChain |
| **Base de Datos** | Almacena usuarios, resultados, niveles y progreso. | MongoDB |

## Estructura del proyecto LinguaMentor (Planteado)

--- 
LinguaMentor/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── models/
│   │   │   └── user_model.py
│   │   ├── routes/
│   │   │   ├── users.py
│   │   │   ├── evaluation.py
│   │   │   └── voice.py
│   │   ├── services/
│   │   │   ├── rabbitmq_utils.py
│   │   │   ├── voice_service.py
│   │   │   └── feedback_service.py
│   │   └── __init__.py
│   ├── requirements.txt
│   └── Dockerfile.backend
│
├── frontend/
│   ├── assets/
│   ├── index.html
    └── Dockerfile.frontend
│   └── app.js
│
├── infrastructure/
│   ├── docker-compose.yml
│   ├── .env
│   └── traefik/
│       ├── traefik.yml
│       └── dynamic_conf.yml
│
└── README.md
└── .gitignore

--- 

## Implementación

### Semana 1 

Durante la primera fase del desarrollo del proyecto LinguaMentor, se configuró el entorno base distribuido mediante Docker y RabbitMQ, y se desarrolló el servicio Gateway API con FastAPI, encargado de recibir las peticiones del usuario y enviarlas a una cola de mensajería donde serán procesadas por el servicio de análisis de voz.

#### Backend principal (main.py)

- Implementado con FastAPI.

- Expone dos endpoints:

    1. /health: prueba de conexión.

    2. /analyze_voice: recibe archivos de audio y los envía a RabbitMQ para análisis.

Fragmento clave del código:

```
@app.post("/analyze_voice")
async def analyze_voice(file: UploadFile = File(...)):
    audio_data = await file.read()
    message = {"filename": file.filename, "size": len(audio_data)}
    await send_message("voice_analysis", message)
    return {"status": "processing", "detail": f"Archivo {file.filename} recibido y en proceso."}

```

Este endpoint no almacena archivos (todavía), solo los procesa en memoria y los envía como mensajes.

#### Comunicación con RabbitMQ (rabbitmq_utils.py)

- Implementa la conexión con RabbitMQ usando la librería aio-pika.
- Envía mensajes serializados en formato JSON a una cola llamada voice_analysis.

Ejemplo:

```
await channel.default_exchange.publish(
    aio_pika.Message(body=json.dumps(message).encode()),
    routing_key=queue_name,
)

```

Esto permite comunicación asíncrona entre servicios: el backend envía la tarea y no espera la respuesta inmediata.

#### Servicio de voz (voice_service.py)

- Simula el análisis de voz (por ahora sin IA real).

- Se ejecuta dentro del mismo contenedor del backend.

- Escucha la cola voice_analysis, recibe mensajes y “procesa” el archivo (simulado con un sleep).

Ejemplo:

```
async def process_voice(message: dict):
    filename = message.get("filename")
    print(f"Analizando archivo {filename}...")
    await asyncio.sleep(2)
    print("Resultado: pronunciación buena, gramática aceptable.")

```

Este servicio demuestra la comunicación entre microservicios dentro del entorno distribuido.

#### Infraestructura con Docker Compose

El archivo docker-compose.yml define los contenedores:

* RabbitMQ: sistema de mensajería (cola de tareas).

* Backend: servicio FastAPI.

```
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
  backend:
    build: ../backend
    ports:
      - "8000:8000"
```

Con docker compose up --build se levantan ambos servicios conectados en una red interna (lingua_net).

#### Requisitos

## Dependencias del Proyecto

Cada paquete tiene una función específica dentro del sistema:

| Paquete | Función |
|----------|----------|
| **fastapi** | Framework web principal para crear APIs REST rápidas y modernas. |
| **uvicorn[standard]** | Servidor ASGI que ejecuta la aplicación FastAPI. |
| **aio-pika** | Librería asíncrona para la comunicación con RabbitMQ. |
| **pydantic** | Permite validar, estructurar y manejar los datos de entrada y salida. |
| **python-multipart** | Habilita el manejo de formularios y archivos `multipart/form-data` (por ejemplo, audios). |

#### Prueba

1. Levantar los servicios:

```
docker compose --env-file .env up --build

```

2. Acceder al backend: 

http://localhost:8000/health

<img width="656" height="156" alt="image" src="https://github.com/user-attachments/assets/c94d3576-6842-4770-a569-e6c3a6ed3421" />

3. Abrir el panel de RabbitMQ:
http://localhost:15672

Usuario: admin
Contraseña: lingua123

Una vez iniciado sesión con las credenciales correctas se accede al Home Page de RabbitMQ:

<img width="1918" height="914" alt="image" src="https://github.com/user-attachments/assets/2b6c9b5c-a1a3-4171-9f83-4fd7280d02dc" />

4. Ejecutar el servicio de voz dentro del contenedor:

```
docker exec -it lingua_backend bash
cd services
python voice_service.py

```

5. Enviar un audio: 

```
curl -X POST "http://localhost:8000/analyze_voice" -F "file=@test.wav"

```

Se verifica también en RabbitMQ:

<img width="946" height="398" alt="image" src="https://github.com/user-attachments/assets/bc9be466-1f74-4c54-be67-53797df170d4" />

#### Resultados

Resultado final de la semana

- ✅ Entorno funcional con Docker y RabbitMQ
- ✅ Comunicación asíncrona entre microservicios simulada
- ✅ Backend operativo en FastAPI
- ✅ Infraestructura base lista para expansión con IA y MongoDB

--- 

### Semana 2
