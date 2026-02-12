# Pomodoro Miner - Plan de trabajo

> Cada fase es un bloque de trabajo que se puede completar en una sesion.
> Marcar con [x] las tareas completadas. Agregar nuevas fases al final.

---

## Fase 1: Tipografia custom ✓

**Objetivo**: Reemplazar las fuentes del sistema por fonts embebidas que
funcionen en todas las plataformas (especialmente web/Pygbag).

**Referencia spec**: Seccion 11

- [x] Seleccionar y descargar fonts .ttf (Chakra Petch + Share Tech Mono)
- [x] Crear directorio `assets/fonts/`
- [x] Reemplazar `pygame.font.SysFont()` por `pygame.font.Font()` con rutas a .ttf
- [x] Definir escala tipografica: 5 niveles (title 38, heading 28, timer 42, body 18, small 14)
- [ ] Verificar build web (se hara en Fase 9)

**Notas**: Orbitron descartada por usar CFF outlines (incompatible con SDL_ttf).
Chakra Petch Bold/Regular elegida como reemplazo (geometrica, estilo tech).

---

## Fase 2: Pantalla de introduccion (IntroScene) ✓

**Objetivo**: Crear la escena de bienvenida con titulo y efecto typewriter.

**Referencia spec**: Seccion 8

- [x] Implementar IntroScene con 4 fases: title_fade, title_hold, typing, done
- [x] Efecto typewriter: renderizar texto letra por letra (~28 chars/s)
- [x] Skip: click o tecla en cualquier momento salta directo al menu con fade
- [x] Transicion fade al MenuScene al terminar o al skipear
- [x] Texto: "Bienvenido a POMI Corp." + instrucciones de tareas/recursos
- [x] IntroScene solo se muestra al iniciar el juego (no al volver de mision)

---

## Fase 3: Pantalla de ajustes (SettingsScene) ✓

**Objetivo**: Permitir al jugador configurar volumen y duraciones.

**Referencia spec**: Seccion 9

- [x] Agregar boton "Settings" al MenuScene (junto a "Talents")
- [x] Implementar SettingsScene con layout centrado
- [x] Slider de volumen SFX (0-100%, arrastrable, default 70%)
- [x] Slider de volumen Ambiente (0-100%, arrastrable, default 50%)
- [x] Selector de duracion de pomodoro (< > con valores: 1,5,15,25,30,45,60 min)
- [x] Selector de duracion de descanso (< > con valores: 1,3,5,10 min)
- [x] Boton "Back" para volver al menu
- [x] Configuracion almacenada en Game (sfx_volume, ambient_volume, pomodoro_minutes, break_minutes)
- [x] MissionScene y AbortScene usan `game.pomodoro_minutes` en vez de constante

**Notas**: Los sliders aun no estan conectados al AudioManager (se hara en Fase 5).
POMODORO_SECONDS se mantiene como constante legacy pero ya no se usa en el gameplay.

---

## Fase 4: Sistema de descanso (Break banner) ✓

**Objetivo**: Implementar la pausa entre misiones de la tecnica Pomodoro.

**Referencia spec**: Seccion 10

- [x] Banner persistente en parte inferior (36px), visible en Menu/Talents/Settings
- [x] Fase countdown: "Break MM:SS" centrado + info de mision a la izquierda
- [x] Fase ready: "Ready for mission" en GREEN con pulse sinusoidal (0.8 Hz, 40%-100%)
- [x] Estado del break vive en Game (break_active, break_remaining, break_ready)
- [x] update_break(dt) en game loop principal, draw_break_banner(surf) sobre escenas de menu
- [x] Se activa al completar mision (_start_break), se desactiva al iniciar nueva (dismiss_break)
- [x] Duracion usa game.break_minutes (configurable en Settings)

**Notas**: Cambio de diseno: se paso de escena independiente (BreakScene) a banner
persistente. El jugador puede interactuar con menu/talents/settings mientras el break corre.

---

## Fase 5: Sistema de audio

**Objetivo**: Agregar SFX a las interacciones principales del juego.

**Referencia spec**: Seccion 12

- [ ] Crear directorio `assets/audio/`
- [ ] Obtener/crear los archivos de audio (ver catalogo en spec)
- [ ] Implementar clase/modulo AudioManager:
  - Cargar todos los sonidos al inicio
  - Dos canales de volumen: SFX y Ambiente (controlados desde Settings)
  - Metodo `play(sound_name)` usa volumen SFX
  - Metodo `play_ambient(sound_name)` usa volumen Ambiente
  - Manejo graceful si un archivo no existe (sin crash)
- [ ] Integrar SFX en los eventos:
  - [ ] Click en botones del menu
  - [ ] Agregar/eliminar tarea
  - [ ] Inicio de mision
  - [ ] Disparo de la nave
  - [ ] Impacto en asteroide
  - [ ] Recoleccion de fragmento
  - [ ] Mision completada / abortada
  - [ ] Upgrade de talento
  - [ ] Titulo intro / typewriter
  - [ ] Fin de descanso (break ready chime)
- [ ] Conectar volumen SFX al slider de Settings (`game.sfx_volume`)
- [ ] Conectar volumen Ambiente al slider de Settings (`game.ambient_volume`)
- [ ] Probar compatibilidad con Pygbag (web)

---

## Fase 6: Game juice - Movimiento organico

**Objetivo**: Hacer que la nave y el mundo se sientan vivos y relajantes.

**Referencia spec**: Secciones 13.3, 13.4

- [ ] **Wobble orbital**: Agregar micro-oscilacion perpendicular a la orbita
  - Usar suma de senos con frecuencias distintas (evitar patron repetitivo)
  - Amplitud: ~3-5 px, frecuencias: 0.7, 1.3, 2.1 Hz aprox
- [ ] **Facing suave**: Interpolar el angulo de facing con lerp en lugar de
  cambio discreto entre ORBITING y SHOOTING
- [ ] **Screenshake al impacto**:
  - Offset aleatorio de camara (2-4 px) con decaimiento exponencial
  - Duracion: ~0.15s
  - Aplicar offset en el draw del Game, no en cada objeto
- [ ] **Trail de la nave** (opcional):
  - Buffer circular de posiciones recientes
  - Dibujar puntos con alpha decreciente

---

## Fase 7: UI polish

**Objetivo**: Mejorar la experiencia de los menus y la informacion en pantalla.

**Referencia spec**: Seccion 13.5

- [ ] Hover en botones: cambio de color/brillo al pasar el mouse
- [ ] Barra de progreso visual para el temporizador (complementa MM:SS)
- [ ] Animacion sutil en el contador de fragmentos al recolectar (+1 que sube y desaparece)
- [ ] Revisar espaciado, margenes y alineacion general de la UI
- [ ] Mejorar feedback visual de la escena de Abort (hacerla menos agresiva)

---

## Fase 8: Particulas y efectos visuales

**Objetivo**: Agregar efectos de particulas para reforzar las acciones del juego.

**Referencia spec**: Seccion 13.2

- [ ] Flash de impacto al golpear el asteroide (explosion breve de particulas)
- [ ] Glow/pulse en fragmentos cuando estan dentro del rango del magnet
- [ ] Efecto visual al recolectar un fragmento (destello que se desvanece)
- [ ] Efecto visual al completar mision (particulas de celebracion sutiles)

---

## Fase 9: Build y deploy

**Objetivo**: Generar build final y subir a itch.io.

- [ ] Verificar que todos los assets (fonts, audio, images) se empaquetan correctamente
- [ ] Generar build con `python -m pygbag --build main.py`
- [ ] Testear el build web localmente (`python -m pygbag main.py` sin --build)
- [ ] Crear ZIP y subir a itch.io
- [ ] Configurar pagina de itch.io (titulo, descripcion, screenshots, tags)

---

## Notas de trabajo

> Espacio para anotar decisiones, problemas encontrados y cambios de rumbo
> durante el desarrollo.

- El juego ya es compatible con Pygbag (async loop implementado).
- POMODORO_SECONDS se mantiene como constante legacy; el gameplay usa `game.pomodoro_minutes`.
- La IntroScene solo se muestra al arrancar, no entre misiones.
- El BreakScene se activa solo al completar mision, no al abortar.
- Settings tiene dos sliders (SFX y Ambiente) listos para conectar al AudioManager en Fase 5.
- Fonts CFF (Orbitron, Exo2) no son compatibles con SDL_ttf. Usar solo TrueType puras.
