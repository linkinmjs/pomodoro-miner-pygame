# Pomodoro Miner - Specification (Blueprint)

> Documento vivo que describe la vision, sistemas y reglas del juego.
> Actualizar cada vez que se agregue o modifique una funcionalidad.

---

## 1. Vision del juego

**Pomodoro Miner** es un juego hibrido idle/pomodoro. El jugador trabaja o estudia
en el mundo real mientras su nave mina recursos automaticamente de un asteroide.

### Principio de diseño central

> El juego debe ser **relajante y no demandar atencion**. El jugador lo deja
> corriendo de fondo mientras se concentra en su tarea real. La informacion visual
> y sonora debe ser **minimalista, suave y ambiental** - nunca intrusiva.

- Sin alertas agresivas ni sonidos estridentes.
- La informacion importante se presenta de forma sutil y gradual.
- Los movimientos son organicos y fluidos, nunca bruscos.
- El jugador solo necesita interactuar al inicio (crear tarea, iniciar mision)
  y al final (ver resultados, asignar talentos).

---

## 2. Dimensiones y configuracion

| Parametro          | Valor          | Notas                                |
| ------------------ | -------------- | ------------------------------------ |
| Resolucion         | 900 x 600      |                                      |
| FPS                | 60              |                                      |
| Duracion pomodoro  | configurable    | Default 25 min, testing 60s          |
| Orbita radio       | 150 px          |                                      |
| Orbita velocidad   | 0.4 rad/s       | Base, modificable por talentos       |

---

## 3. Arquitectura de escenas

El juego usa un patron de escenas. Cada escena implementa `handle_event()`,
`update(dt)` y `draw(surf)`.

```
IntroScene         - Pantalla de bienvenida con titulo y texto typewriter
MenuScene          - Lista de tareas, input de texto, navegacion
SettingsScene      - Ajustes: volumen, duracion de pomodoro
TalentScene        - Arbol de mejoras permanentes
StoryScene         - Imagen narrativa pre-mision (si hay assets)
MissionScene       - Gameplay principal (nave orbitando + mineria)
BreakScene         - Descanso entre misiones con contador
AbortScene         - Resumen al abortar una mision
FadeTransition     - Transicion fade-to-black entre escenas
```

### Flujo de escenas

```
Intro -> Menu                                         (primera vez)
Menu -> [Story] -> Mission -> Break -> Menu           (completada)
Menu -> [Story] -> Mission -> Abort -> Menu           (abortada)
Menu -> Talents -> Menu
Menu -> Settings -> Menu
```

---

## 4. Sistema de tareas

- El jugador crea tareas con nombre libre (max 40 caracteres).
- Cada tarea registra cuantos pomodoros se completaron.
- Las tareas se listan con scroll vertical.
- Acciones: **Add**, **Start**, **Delete**.

---

## 5. Sistema de mision (gameplay)

### Nave (Ship)
- Orbita automaticamente alrededor del asteroide central.
- Dos estados: `ORBITING` (velocidad normal) y `SHOOTING` (velocidad reducida).
- Dispara rafagas automaticas a intervalos aleatorios.
- **[PENDIENTE]** Movimiento organico: micro-oscilaciones aleatorias sobre la orbita
  para dar sensacion de vuelo real (ver seccion 13.3).

### Asteroide
- Poligono irregular generado proceduralmente (14 vertices con ruido).
- Radio base ~40 px.
- **[PENDIENTE]** Screenshake sutil al recibir impacto (ver seccion 13.3).

### Proyectiles
- Velocidad: 200 px/s.
- Spread angular configurable por rafaga.
- Se destruyen al alcanzar radio 35 del centro del asteroide.

### Fragmentos
- Spawn en la superficie del asteroide al impacto.
- Se dispersan radialmente con deceleracion gradual.
- Se asientan cerca de la orbita (ORBIT_SETTLE_STRENGTH).
- Son atraidos por la nave si estan dentro del radio magnetico.
- Se recolectan al estar a <15 px de la nave.
- Colores aleatorios: naranja, amarillo, verde, cyan.

### Temporizador
- Cuenta regresiva en formato MM:SS.
- Al llegar a 0: mision completa, fragmentos guardados, pomodoro sumado.
- Delay de 1.5s antes de volver al menu.

### Abortar
- Penalidad: solo se conserva el 30% de los fragmentos minados.
- Muestra resumen: tiempo transcurrido/restante, fragmentos ganados.

---

## 6. Sistema de talentos

Mejoras permanentes compradas con fragmentos. Costo del nivel N = `N * 5`.

| ID              | Nombre          | Max | Efecto por nivel           |
| --------------- | --------------- | --- | -------------------------- |
| fire_rate       | Rapid Fire      | 5   | -10% intervalo de disparo  |
| bullet_count    | Multi Shot      | 5   | +1 bala por rafaga         |
| magnet_range    | Magnetic Pull   | 5   | +20% radio magnetico       |
| double_frag     | Double Fragment | 5   | +8% chance fragmento doble |
| orbit_speed     | Thruster Boost  | 5   | +10% velocidad orbital     |
| frag_magnet_str | Tractor Beam    | 3   | +30% fuerza magnetica      |

---

## 7. Sistema de historia (Story)

- Imagenes `assets/images/story_XX.png` se muestran antes de cada mision.
- Se selecciona la imagen segun total de pomodoros completados.
- Click o SPACE para continuar a la mision.

---

## 8. Pantalla de introduccion (IntroScene)

Escena que se muestra **una sola vez** al abrir el juego, antes del menu.

### Secuencia

1. Fondo negro. Aparece el titulo del juego **"POMODORO MINER"** con fade-in
   centrado en pantalla.
2. Tras una breve pausa (~1s), comienza a aparecer un texto de bienvenida
   con **efecto typewriter** (letra por letra, como si se estuviera escribiendo).
3. El texto es una presentacion breve y atmosferica del juego. Ejemplo:

   > *"En los confines del espacio, el tiempo es tu recurso mas valioso...*
   > *Cada minuto de trabajo alimenta tu nave. Cada pomodoro te acerca*
   > *a las estrellas."*

4. Al terminar el texto (o al hacer click/presionar cualquier tecla en
   cualquier momento), transicion fade al MenuScene.

### Parametros

| Parametro              | Valor sugerido | Notas                                     |
| ---------------------- | -------------- | ----------------------------------------- |
| Velocidad typewriter   | ~30 chars/s    | Ritmo de lectura comodo                   |
| Pausa entre lineas     | ~0.4s          | Separacion natural entre oraciones        |
| Delay antes del texto  | ~1.0s          | Tiempo para que el titulo se asiente      |
| Skip                   | click/tecla    | El jugador puede saltear en cualquier momento |

### Notas de diseno
- El tono debe ser **calmo y evocador**, coherente con la filosofia relajante.
- El texto no debe ser largo: 2-3 oraciones maximo.
- Se puede acompanar con un SFX ambiental suave al aparecer el titulo.

---

## 9. Pantalla de ajustes (SettingsScene)

Accesible desde el menu principal mediante un boton **"Settings"**.

### Opciones configurables

| Ajuste                | Control           | Rango / Opciones            | Default     |
| --------------------- | ----------------- | --------------------------- | ----------- |
| Volumen SFX           | Slider horizontal | 0% - 100%                   | 70%         |
| Duracion del pomodoro | Selector          | 1, 5, 15, 25, 30, 45, 60 min| 25 min      |
| Duracion del descanso | Selector          | 1, 3, 5, 10 min             | 5 min       |

### Comportamiento
- Los cambios se aplican inmediatamente (no requiere boton "guardar").
- Boton **"Back"** para volver al menu.
- Los valores se persisten si se implementa el sistema de guardado (ver backlog).
- El slider de volumen ajusta el volumen master de `pygame.mixer`.
- Los selectores de duracion pueden ser botones `<` `>` que ciclan entre
  los valores predefinidos.

### Layout sugerido
```
         SETTINGS

  SFX Volume     [=====>----]  70%

  Pomodoro       <  25 min  >

  Break          <   5 min  >

            [ Back ]
```

---

## 10. Sistema de descanso (BreakScene)

Implementa la pausa entre sesiones de la tecnica Pomodoro.

### Cuando se activa
- **Automaticamente** al completar una mision exitosamente.
- Flujo: Mission complete -> (delay 1.5s) -> BreakScene.
- **No se activa** al abortar una mision (se vuelve directo al menu).

### Fase 1: Cuenta regresiva

- Muestra un contador descendente con la duracion del descanso (configurable
  en Settings, default 5 min).
- Formato: `MM:SS`.
- Texto acompanante: *"Take a break"* o similar, en tono suave.
- Fondo relajante (puede ser el fondo negro con estrellas sutiles o similar).
- El jugador **puede** volver al menu antes de que termine el descanso
  mediante un boton discreto (no prominente, para no incentivar saltear).

### Fase 2: Ready (post-descanso)

- Al llegar el contador a 0, el texto cambia a un mensaje como:
  **"Ready for next mission"**.
- El mensaje aparece con un **parpadeo suave** (pulse de opacidad, no
  on/off brusco):
  - Opacidad oscila entre ~40% y 100% usando una funcion sinusoidal.
  - Frecuencia: ~0.8 Hz (un ciclo completo cada ~1.2 segundos).
  - El efecto debe ser **estimulante pero no agresivo**, como un faro lejano.
- El jugador hace click o presiona cualquier tecla para volver al menu.
- **No hay auto-retorno**: el jugador decide cuando esta listo.

### Informacion en pantalla durante el descanso

| Elemento                | Visible en fase 1 | Visible en fase 2 |
| ----------------------- | ------------------ | ------------------ |
| Contador MM:SS          | Si                 | No                 |
| "Take a break"          | Si                 | No                 |
| "Ready for next mission"| No                 | Si (pulsando)      |
| Tarea completada        | Si (sutil)         | Si (sutil)         |
| Fragmentos ganados      | Si (sutil)         | Si (sutil)         |
| Boton "Skip" / "Menu"   | Si (discreto)      | No                 |
| "Click to continue"     | No                 | Si                 |

### Notas de diseno
- Esta pantalla debe ser la mas relajante de todo el juego.
- Considerar un SFX suave al terminar el descanso (como un chime ambiental).
- El descanso no es obligatorio: el boton de skip existe, pero no se destaca.

---

## 11. Tipografia

Fonts embebidas en `assets/fonts/` (Google Fonts, licencia OFL).

| Uso              | Font                     | Tamano | Variable en Game     |
| ---------------- | ------------------------ | ------ | -------------------- |
| Titulos          | Chakra Petch Bold        | 38     | `font_title`         |
| Subtitulos       | Chakra Petch Regular     | 28     | `font_heading`       |
| Timer de mision  | Share Tech Mono          | 42     | `font_timer`         |
| Texto UI/cuerpo  | Share Tech Mono          | 18     | `font`               |
| Hints/captions   | Share Tech Mono          | 14     | `font_small`         |

**Chakra Petch**: Geometrica, estilo tech/sci-fi. Usada para titulos y headings.
**Share Tech Mono**: Monospace sci-fi. Usada para todo el texto funcional (timer, UI, botones).

**Nota**: Las fonts deben ser TrueType puras (.ttf con outlines TT, no CFF).
Pygame 2.x con SDL_ttf no soporta fonts CFF-based (como Orbitron static).

---

## 12. Sistema de audio

### Filosofia
El audio debe ser **ambiental y no intrusivo**. Sonidos suaves y cortos.
Sin musica de fondo agresiva. Los efectos refuerzan acciones sin distraer.

### Catalogo de efectos (SFX)

| Evento                    | Archivo esperado         | Descripcion del sonido             |
| ------------------------- | ------------------------ | ---------------------------------- |
| Click en boton (menu)     | `ui_click.wav`           | Click suave, tonal                 |
| Hover en boton            | `ui_hover.wav`           | Tick sutil (opcional)              |
| Agregar tarea             | `ui_confirm.wav`         | Confirmacion suave                 |
| Eliminar tarea            | `ui_delete.wav`          | Sonido bajo, descriptivo           |
| Iniciar mision            | `mission_start.wav`      | Transicion ambiental               |
| Disparo de nave           | `ship_shoot.wav`         | Laser suave, corto                 |
| Impacto en asteroide      | `asteroid_hit.wav`       | Impacto solido pero sutil          |
| Fragmento recolectado     | `fragment_collect.wav`   | Tintineo cristalino                |
| Mision completada         | `mission_complete.wav`   | Acorde satisfactorio               |
| Mision abortada           | `mission_abort.wav`      | Tono descendente suave             |
| Upgrade de talento        | `talent_upgrade.wav`     | Sonido de mejora/nivel up          |
| Titulo intro              | `intro_title.wav`        | Tono ambiental al aparecer titulo  |
| Typewriter (letra)        | `typewriter_tick.wav`    | Tick muy sutil por caracter        |
| Fin de descanso           | `break_ready.wav`        | Chime ambiental suave              |

**Ubicacion**: `assets/audio/`
**Formato**: `.wav` u `.ogg` (compatibles con Pygame y Pygbag).

---

## 13. Game Juice (polish visual)

### 13.1 Transiciones
- **Ya implementado**: Fade-to-black entre escenas (0.5s).

### 13.2 Particulas y efectos
- **Ya implementado**: Fragmentos con colores aleatorios y movimiento fisico.
- **[PENDIENTE]** Particulas de impacto al golpear el asteroide (flash breve).
- **[PENDIENTE]** Trail sutil detras de la nave (puntos que se desvanecen).
- **[PENDIENTE]** Glow/pulse en fragmentos cercanos al magnet.

### 13.3 Movimiento organico de la nave
La nave debe sentirse viva aun en orbita pasiva:
- **Wobble orbital**: Micro-desplazamiento perpendicular a la orbita usando
  ruido sinusoidal (2-3 frecuencias superpuestas, amplitud ~3-5 px).
- **Inclinacion suave**: El facing de la nave se interpola suavemente (lerp)
  en lugar de cambiar abruptamente entre estados.

### 13.4 Screenshake
- Al impactar el asteroide: desplazamiento aleatorio de la camara (2-4 px)
  con decaimiento rapido (~0.15s).
- Intensidad sutil, coherente con la filosofia relajante.

### 13.5 UI polish
- Botones con transicion de color al hover.
- Numeros que animan al cambiar (count-up sutil para fragmentos).
- Barra de progreso visual para el temporizador (ademas del texto MM:SS).

---

## 14. Paleta de colores

| Nombre        | RGB             | Uso                          |
| ------------- | --------------- | ---------------------------- |
| BG_COLOR      | (0, 0, 0)      | Fondo general                |
| WHITE         | (255, 255, 255) | Texto principal              |
| GRAY          | (160, 160, 160) | Texto secundario             |
| DARK_GRAY     | (60, 60, 60)    | Separadores, elementos inactivos |
| CYAN          | (0, 220, 255)   | Nave, acentos primarios      |
| YELLOW        | (255, 220, 50)  | Fragmentos, contadores       |
| RED           | (220, 60, 60)   | Alertas, boton abort/delete  |
| GREEN         | (60, 220, 60)   | Confirmacion, boton start    |
| ORANGE        | (255, 160, 40)  | Talentos, acentos secundarios|
| ASTEROID_COLOR| (130, 130, 130) | Asteroide                    |

---

## 15. Estructura del proyecto

```
pomodoro-miner-python/
  main.py                    # Codigo fuente principal
  spec.md                    # Este documento (blueprint)
  plan.md                    # Plan de trabajo por fases
  README.md                  # Documentacion publica
  assets/
    fonts/                   # [PENDIENTE] Archivos .ttf
    audio/                   # [PENDIENTE] Archivos .wav/.ogg
    images/
      story_01.png           # Imagen narrativa
  build/
    web/                     # Build Pygbag para itch.io
```

---

## 16. Backlog de ideas

> Espacio para registrar ideas futuras. Evaluar antes de incorporar al plan.

- [ ] Persistencia de datos (guardar progreso en JSON/localStorage para web)
- [ ] Musica ambiental de fondo (loop suave, volumen bajo)
- [ ] Tipos de asteroide con diferentes resistencias/recompensas
- [ ] Estadisticas acumuladas (total de fragmentos minados, tiempo total, etc.)
- [ ] Notificacion sonora sutil cuando el pomodoro esta por terminar (ultimos 30s)
- [ ] Animacion de la nave al completar mision (celebracion sutil)
- [ ] Temas visuales desbloqueables (paletas de color alternativas)
