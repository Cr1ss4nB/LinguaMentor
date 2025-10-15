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

## Implementación
