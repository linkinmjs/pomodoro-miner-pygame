# Implementation Plan: POMI Corp. (Pomodoro Miner)

**Date**: 2026-02-12
**Spec**: [spec.md](spec.md)

## Summary

Juego hibrido idle/pomodoro donde el jugador trabaja en el mundo real mientras su nave
mina recursos automaticamente. Implementado en Python con Pygame, compatible con build
web via Pygbag. El desarrollo sigue un enfoque por user stories priorizadas, donde cada
story entrega valor independiente.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pygame 2.x, Pygbag (build web)
**Storage**: En memoria (persistencia en backlog)
**Testing**: Manual (verificacion visual y funcional por escena)
**Target Platform**: Desktop (Windows/Linux/Mac) + Web (Pygbag/itch.io)
**Project Type**: Single project (monolito en main.py)
**Performance Goals**: 60 FPS estables con fragmentos y particulas activos
**Constraints**: Compatible con SDL_ttf (fonts TrueType puras), async loop para Pygbag
**Scale/Scope**: Juego single-player casual, ~2500 LOC, 8 escenas

## Project Structure

### Documentation

```text
pomodoro-miner-python/
├── spec.md              # Especificacion (QUE construir)
├── plan.md              # Este archivo (COMO implementar)
├── sdd-guide.MD         # Guia de la metodologia SDD
├── plan-template.md     # Template de plan
└── spec-template.md     # Template de spec
```

### Source Code

```text
pomodoro-miner-python/
├── main.py              # Codigo fuente principal (monolito)
├── generate_audio.py    # Generador de archivos de audio placeholder
├── assets/
│   ├── fonts/           # Chakra Petch (.ttf) + Share Tech Mono (.ttf)
│   ├── audio/           # SFX (.wav) y ambiente (.wav/.ogg)
│   └── images/          # Story images (story_XX.png)
└── build/
    └── web/             # Build Pygbag para itch.io
```

**Structure Decision**: Proyecto monolito en `main.py`. Toda la logica (escenas, entidades,
audio, game loop) vive en un solo archivo. Los assets se organizan en subdirectorios por tipo.

---

## Phase 1: Setup (Shared Infrastructure) [COMPLETADO]

**Purpose**: Proyecto base con game loop, patron de escenas y configuracion Pygbag.

- [x] T001 Crear estructura del proyecto con main.py y directorio assets/
- [x] T002 Implementar game loop async compatible con Pygbag (60 FPS)
- [x] T003 Implementar patron de escenas (handle_event, update, draw)
- [x] T004 Implementar FadeTransition entre escenas
- [x] T005 Definir paleta de colores y constantes globales

---

## Phase 2: Foundational (Blocking Prerequisites) [COMPLETADO]

**Purpose**: Tipografia custom y sistema de audio - infraestructura compartida por todas las escenas.

- [x] T006 Seleccionar fonts TrueType compatibles con SDL_ttf (Chakra Petch + Share Tech Mono)
- [x] T007 Crear assets/fonts/ con archivos .ttf y escala tipografica (5 niveles)
- [x] T008 Reemplazar pygame.font.SysFont() por pygame.font.Font() con rutas .ttf
- [x] T009 Implementar AudioManager (carga automatica, play SFX, play/stop ambient)
- [x] T010 Generar audio placeholder con generate_audio.py (ui_click.wav, ambient_menu.wav)
- [x] T011 Integrar SFX ui_click en todos los botones de todas las escenas
- [x] T012 Ambient loop en menu/intro, detenido en mision

**Checkpoint**: Infraestructura de fonts y audio lista. Todas las escenas usan tipografia custom y audio.

---

## Phase 3: User Story 1 - Mision Pomodoro (Priority: P1) [COMPLETADO]

**Goal**: El jugador crea tareas, inicia misiones con timer pomodoro, la nave mina automaticamente
y los fragmentos se acumulan al completar.

**Independent Test**: Crear tarea -> Start -> nave orbita y mina -> timer llega a 0 -> fragmentos guardados.

### Implementation for User Story 1

- [x] T013 [US1] Implementar MenuScene: input de texto, lista de tareas, botones Add/Start/Delete
- [x] T014 [US1] Implementar MissionScene: nave orbitando asteroide con timer countdown
- [x] T015 [US1] Implementar Ship: orbita automatica, estados ORBITING/SHOOTING, disparo de rafagas
- [x] T016 [US1] Implementar Asteroid: poligono procedural (14 vertices con ruido)
- [x] T017 [US1] Implementar Projectiles: velocidad 200 px/s, spread angular, colision con asteroide
- [x] T018 [US1] Implementar Fragments: spawn en superficie, dispersion radial, recoleccion (sistema magnetico legacy, pendiente refactor a rayo tractor)
- [x] T019 [US1] Implementar timer countdown configurable (MM:SS) con delay 1.5s al completar
- [x] T020 [US1] Implementar AbortScene: penalidad 30%, resumen de mision
- [x] T021 [US1] Implementar IntroScene: fade-in titulo, typewriter, skip, auto-avance
- [x] T022 [US1] Implementar StoryScene: mostrar imagenes narrativas segun pomodoros completados

**Checkpoint**: Core gameplay loop funcional. Se puede crear tarea, minar y acumular fragmentos.

---

## Phase 4: User Story 2 - Sistema de Talentos (Priority: P2) [COMPLETADO]

**Goal**: El jugador gasta fragmentos en mejoras permanentes para la nave.

**Independent Test**: Acumular fragmentos -> Talents -> Upgrade -> verificar efecto en mision.

### Implementation for User Story 2

- [x] T023 [US2] Implementar TalentScene: lista de talentos con niveles y boton Upgrade (implementacion inicial con 6 talentos)
- [x] T024 [US2] Implementar sistema de costo progresivo (nivel * 5 fragmentos)
- [x] T025 [US2] Aplicar efectos de talentos basicos en Ship/MissionScene (fire_rate, bullet_count, orbit_speed, double_frag)
- [x] T026 [US2] Feedback visual: nivel actual, costo, MAX cuando corresponda

**Checkpoint**: Progression loop basico funcional. Pendiente: expansion a 16 talentos en 4 ramas (Phase 7).

---

## Phase 5: User Story 3 - Configuracion de Ajustes (Priority: P3) [COMPLETADO]

**Goal**: El jugador personaliza volumenes de audio y duraciones desde Settings.

**Independent Test**: Settings -> cambiar duracion pomodoro -> iniciar mision -> verificar duracion.

### Implementation for User Story 3

- [x] T027 [US3] Implementar SettingsScene con layout centrado
- [x] T028 [US3] Slider de volumen SFX (0-100%, arrastrable, default 70%)
- [x] T029 [US3] Slider de volumen Ambiente (0-100%, arrastrable, default 50%)
- [x] T030 [US3] Selector de duracion pomodoro (< > con valores predefinidos, default 25 min)
- [x] T031 [US3] Selector de duracion descanso (< > con valores predefinidos, default 5 min)
- [x] T032 [US3] Conectar sliders a AudioManager (volumen en tiempo real)
- [x] T033 [US3] MissionScene y AbortScene usan game.pomodoro_minutes

**Checkpoint**: Experiencia personalizable. Audio y duraciones configurables.

---

## Phase 6: User Story 4 - Sistema de Descanso (Priority: P4) [COMPLETADO]

**Goal**: Break banner con countdown tras mision completada, fase "ready" con pulse.

**Independent Test**: Completar mision -> banner countdown -> termina -> "Ready for mission" pulsando.

### Implementation for User Story 4

- [x] T034 [US4] Implementar estado de break en Game (break_active, break_remaining, break_ready)
- [x] T035 [US4] Implementar banner persistente (36px inferior) con linea separadora
- [x] T036 [US4] Fase countdown: "Break MM:SS" centrado + info mision a la izquierda
- [x] T037 [US4] Fase ready: "Ready for mission" en GREEN con pulse sinusoidal (0.8 Hz)
- [x] T038 [US4] Activacion automatica al completar mision (_start_break)
- [x] T039 [US4] Desactivacion al iniciar nueva mision (dismiss_break)
- [x] T040 [US4] Dibujar banner sobre MenuScene, TalentScene y SettingsScene

**Checkpoint**: Tecnica Pomodoro completa con breaks entre sesiones.

---

## Phase 7: Refactor Sistema de Recoleccion - Rayo Tractor

**Goal**: Reemplazar el sistema de atraccion magnetica invisible por rayos tractores visibles
que atrapan fragmentos individualmente.

**Independent Test**: Iniciar mision -> disparar al asteroide -> verificar que la nave emite un rayo
visible al fragmento mas cercano -> el fragmento es atraido -> se recolecta -> el rayo busca el siguiente.

### Implementation

- [ ] T041 Implementar estados de fragmento (FREE/LOCKED) y logica de seleccion de objetivo (mas cercano en rango)
- [ ] T042 Implementar TractorBeam: rayo visible (linea CYAN con alpha) entre nave y fragmento LOCKED
- [ ] T043 Implementar atraccion: fragmento LOCKED se mueve hacia la nave a velocidad fija (base 80 px/s)
- [ ] T044 Implementar ciclo de rayo: recolectar fragmento -> liberar rayo -> buscar siguiente automaticamente
- [ ] T045 Remover sistema de atraccion magnetica legacy (campo invisible, ORBIT_SETTLE_STRENGTH)
- [ ] T046 Implementar talento beam_range (Long Range Beam): +20%/nivel al rango del rayo
- [ ] T047 Implementar talento beam_speed (Beam Accelerator): +15%/nivel a velocidad de atraccion
- [ ] T048 Implementar talento beam_count (Multi Beam): +1 rayo simultaneo/nivel (max 3), cada rayo busca fragmento distinto
- [ ] T049 Implementar talento auto_collect (Drone Sweep): recolecta fragmento mas lejano fuera del rango cada 10s/8s/5s
- [ ] T050 Remover talentos legacy (magnet_range, frag_magnet_str) y reemplazar por los nuevos en TalentScene
- [ ] T051 Implementar talentos de armamento nuevos: burst_speed, piercing, crit_shot (aplicar en MissionScene)
- [ ] T052 Implementar talentos de navegacion nuevos: aim_speed, inertia_control (aplicar en Ship states)
- [ ] T053 Implementar talentos de economia: abort_save (AbortScene), end_bonus (mision completa), talent_discount (costo global)
- [ ] T054 Refactorizar TalentScene: layout en 4 ramas (Armamento, Recoleccion, Navegacion, Economia), 16 talentos total
- [ ] T055 Visual del rayo: pulso sutil de opacidad/grosor, coherente con estetica relajante
- [ ] T056 Visual de crit_shot: flash especial al impactar (color/tamaño distinto)

**Checkpoint**: Sistema de recoleccion por rayo tractor funcional + 16 talentos en 4 ramas implementados.

---

## Phase 8: User Story 5 - Parallax de Fondo (Priority: P5)

**Goal**: Fondo de MissionScene con 3 capas de parallax procedural que den profundidad y sensacion de campo de asteroides.

**Independent Test**: Iniciar mision -> verificar capa de fondo (estrellas, planetas, via lactea) -> verificar asteroides decorativos detras de la nave -> esperar asteroide frontal semi-transparente pasando por encima.

### Implementation

- [ ] T057 [US5] Capa 1 - Estrellas: generar 80-120 puntos aleatorios (1-3 px) con brillo variable y parpadeo sinusoidal sutil
- [ ] T058 [US5] Capa 1 - Planetas: generar 2-3 circulos (20-50 px radio) con colores desaturados (azul oscuro, violeta, terracota) y sombreado simple
- [ ] T059 [US5] Capa 1 - Via Lactea: banda diagonal difusa con alpha muy bajo (~15-25), tonos violeta/azul, generada con ruido o circulos superpuestos
- [ ] T060 [US5] Capa 2 - Asteroides decorativos: 5-8 poligonos irregulares (6-10 vertices, radio 8-25 px), grises oscuros, rotacion lenta aleatoria
- [ ] T061 [US5] Capa 3 - Spawner de asteroide frontal: 1 cada 15-30s, poligono grande (60-120 px radio), alpha 40-60%, cruza pantalla linealmente
- [ ] T062 [US5] Sistema de parallax: desplazamiento por capa (factor 0.05-0.1 / 0.2-0.3 / 1.5-2.0) vinculado al movimiento orbital o scroll continuo
- [ ] T063 [US5] Integrar orden de renderizado en MissionScene: Capa1 -> Capa2 -> Nave/Asteroide/Fragmentos -> Capa3 -> UI

**Checkpoint**: MissionScene con fondo espacial inmersivo y profundidad visual.

---

## Phase 9: User Story 5 - Game Juice: Movimiento Organico (Priority: P5)

**Goal**: Nave con movimiento organico, screenshake, facing suave. El juego se siente vivo.

**Independent Test**: Iniciar mision -> observar wobble -> observar screenshake al impacto -> facing interpolado.

### Implementation for User Story 5

- [ ] T064 [US5] Refactorizar estados de la nave: ORBITING -> AIMING -> SHOOTING -> RETURNING -> ORBITING
- [ ] T065 [US5] AIMING: giro suave (lerp) hacia asteroide + desaceleracion gradual de velocidad orbital
- [ ] T066 [US5] SHOOTING: cadencia pausada entre balas, velocidad orbital reducida (~30-40%) por inercia
- [ ] T067 [US5] RETURNING: giro suave (lerp) de vuelta a tangente + aceleracion gradual hasta velocidad base
- [ ] T068 [US5] Wobble orbital: micro-oscilacion perpendicular con suma de senos (3 frecuencias, 3-5 px)
- [ ] T069 [US5] Screenshake al impacto: offset camara 2-4 px, decaimiento exponencial ~0.15s
- [ ] T070 [US5] Trail de la nave (opcional): buffer circular de posiciones con alpha decreciente

**Checkpoint**: La nave se siente viva y organica.

---

## Phase 10: User Story 5 - Game Juice: UI Polish (Priority: P5)

**Goal**: Mejorar feedback visual de menus y HUD de mision.

**Independent Test**: Hover sobre botones -> cambio visual. Recolectar fragmento -> animacion +1.

### Implementation

- [ ] T071 [US5] Hover en botones: cambio de color/brillo al pasar el mouse
- [ ] T072 [US5] Barra de progreso visual para el temporizador (complementa MM:SS)
- [ ] T073 [US5] Animacion sutil en contador de fragmentos al recolectar (+1 que sube y desaparece)
- [ ] T074 [US5] Revisar espaciado, margenes y alineacion general de la UI
- [ ] T075 [US5] Mejorar feedback visual de AbortScene (menos agresiva)

**Checkpoint**: UI pulida con feedback visual consistente.

---

## Phase 11: User Story 5 - Game Juice: Particulas y Efectos (Priority: P5)

**Goal**: Efectos de particulas para reforzar acciones del juego.

**Independent Test**: Disparar al asteroide -> flash de impacto. Recolectar fragmento -> destello.

### Implementation

- [ ] T076 [US5] Flash de impacto al golpear asteroide (explosion breve de particulas)
- [ ] T077 [US5] Glow/pulse en fragmentos dentro del rango del rayo tractor
- [ ] T078 [US5] Efecto visual al recolectar fragmento (destello que se desvanece)
- [ ] T079 [US5] Efecto visual al completar mision (particulas de celebracion sutiles)

**Checkpoint**: Efectos visuales completos. El juego se siente pulido.

---

## Phase 12: User Story 5 - Game Juice: SFX Adicionales (Priority: P5)

**Goal**: Agregar los SFX pendientes del catalogo de audio.

**Independent Test**: Disparar -> sonido laser. Impactar -> sonido impacto. Recolectar -> tintineo.

### Implementation

- [ ] T080 [US5] Implementar gen_ship_shoot() en generate_audio.py: sine sweep descendente, ~0.1s
- [ ] T081 [US5] Implementar gen_asteroid_hit() en generate_audio.py: noise burst percusivo, ~0.08s
- [ ] T082 [US5] Implementar gen_fragment_collect() en generate_audio.py: sine alta freq con decay, ~0.12s
- [ ] T083 [US5] Implementar gen_mission_complete() en generate_audio.py: acorde mayor, ~0.5s
- [ ] T084 [US5] Implementar gen_mission_abort(), gen_talent_upgrade(), gen_break_ready() en generate_audio.py
- [ ] T085 [US5] Ejecutar generate_audio.py y verificar que todos los .wav se crean en assets/audio/
- [ ] T086 [US5] Integrar SFX en MissionScene (disparo, impacto, recoleccion, mision completa)
- [ ] T087 [US5] Integrar SFX en AbortScene (mision abortada)
- [ ] T088 [US5] Integrar SFX en TalentScene (upgrade)
- [ ] T089 [US5] Integrar SFX break_ready al terminar countdown

**Checkpoint**: Audio completo. Cada accion tiene feedback sonoro sutil.

---

## Phase 13: Build & Deploy

**Purpose**: Generar build web y publicar en itch.io.

- [ ] T090 Verificar que el game loop es async con await asyncio.sleep(0) en cada frame
- [ ] T091 Verificar que no se usan threads ni file I/O bloqueante
- [ ] T092 Verificar que todos los assets (fonts, audio, images) se empaquetan correctamente
- [ ] T093 Verificar que solo se usan imports de stdlib + pygame (sin dependencias externas en runtime)
- [ ] T094 Generar build con `python -m pygbag --build main.py`
- [ ] T095 Testear build web localmente (`python -m pygbag main.py`)
- [ ] T096 Verificar compatibilidad de fonts TrueType con Pygbag
- [ ] T097 Verificar compatibilidad de audio WAV/OGG con Pygbag (no MP3)
- [ ] T098 Verificar que el audio inicia tras primera interaccion del usuario (autoplay bloqueado)
- [ ] T099 Crear ZIP y subir a itch.io
- [ ] T100 Configurar pagina de itch.io (titulo, descripcion, screenshots, tags)

**Checkpoint**: Juego publicado y accesible en web.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - COMPLETADO
- **Foundational (Phase 2)**: Depende de Phase 1 - COMPLETADO
- **US1 Mision Pomodoro (Phase 3)**: Depende de Phase 2 - COMPLETADO
- **US2 Talentos (Phase 4)**: Depende de Phase 3 (necesita fragmentos) - COMPLETADO
- **US3 Settings (Phase 5)**: Depende de Phase 2 - COMPLETADO
- **US4 Break (Phase 6)**: Depende de Phase 3 (se activa post-mision) - COMPLETADO
- **Rayo Tractor + Talentos (Phase 7)**: Depende de Phase 3 y 4 (refactoriza recoleccion y talentos existentes)
- **US5 Parallax (Phase 8)**: Depende de Phase 3 (MissionScene existente). Puede hacerse en paralelo con Phase 7.
- **US5 Game Juice (Phases 9-12)**: Depende de Phase 7 (polish sobre funcionalidad refactorizada)
- **Build & Deploy (Phase 13)**: Depende de que el juego este en estado publicable

### User Story Dependencies

- **US1 (P1)**: Core loop - COMPLETADO. No depende de otras stories.
- **US2 (P2)**: Depende de US1 (necesita fragmentos para comprar) - COMPLETADO
- **US3 (P3)**: Independiente de US1/US2 (solo configuracion) - COMPLETADO
- **US4 (P4)**: Depende de US1 (se activa post-mision) - COMPLETADO
- **US5 (P5)**: Polish sobre todo lo anterior. Puede hacerse en paralelo por sub-fase.

### Within Each Phase

- Logica de entidades antes de integracion con escenas
- Core functionality antes de polish/efectos
- Verificar tests manuales al completar cada phase
- Commit despues de cada tarea o grupo logico

## Notes

- [USx] label mapea tarea a user story para trazabilidad
- El proyecto es monolito en main.py; no hay separacion en modulos
- POMODORO_SECONDS se mantiene como constante legacy; el gameplay usa game.pomodoro_minutes
- La IntroScene solo se muestra al arrancar, no entre misiones
- El break se activa solo al completar mision, no al abortar
- AudioManager carga todo assets/audio/ automaticamente
- Fonts CFF (Orbitron, Exo2) no son compatibles con SDL_ttf. Usar solo TrueType puras (.ttf con outlines TT)
- Ambient loop corre en menu/intro, se detiene en misiones
- generate_audio.py es un script de setup (no runtime): genera placeholders WAV mono 16-bit 44100Hz con puro Python (math, wave, struct). Se ejecuta una vez durante el setup
- StoryScene se salta automaticamente si no hay imagenes en assets/images/
- **Pygbag**: Game loop DEBE ser async. No usar threads, file I/O bloqueante, MP3, ni imports externos. Audio inicia tras primera interaccion del usuario en web
