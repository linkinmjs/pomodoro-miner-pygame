# Feature Specification: POMI Corp. (Pomodoro Miner)

**Created**: 2025-01-01
**Updated**: 2026-02-12

## User Scenarios & Testing *(mandatory)*

<!--
  User stories priorizadas como journeys independientes.
  Cada una puede desarrollarse, testearse y demostrarse de forma independiente.
-->

### User Story 1 - Mision Pomodoro (Priority: P1)

El jugador crea una tarea con nombre libre, inicia una mision y su nave mina
recursos automaticamente de un asteroide mientras el trabaja o estudia en el mundo
real. Al terminar el temporizador, los fragmentos se acumulan y el pomodoro se suma.

**Why this priority**: Es el core loop del juego. Sin esto no hay producto. Entrega
el valor fundamental: un timer pomodoro gamificado con mineria idle.

**Independent Test**: Crear tarea -> iniciar mision -> esperar timer -> verificar
que fragmentos y pomodoro se acumulan correctamente.

**Acceptance Scenarios**:

1. **Scenario**: Crear tarea y empezar mision
   - **Given** el jugador esta en el menu sin tareas
   - **When** escribe un nombre (max 40 chars) y presiona "Add", luego selecciona la tarea y presiona "Start"
   - **Then** se transiciona a MissionScene con la nave orbitando el asteroide y el timer en cuenta regresiva

2. **Scenario**: Completar mision exitosamente
   - **Given** la nave esta minando y el timer llega a 00:00
   - **When** pasan 1.5s de delay
   - **Then** los fragmentos se guardan al 100%, el pomodoro se suma a la tarea, y se vuelve al menu

3. **Scenario**: Abortar mision
   - **Given** la nave esta minando y el jugador presiona "Abort"
   - **When** se muestra AbortScene con resumen (tiempo, fragmentos)
   - **Then** solo se conserva el 30% de fragmentos minados, se vuelve al menu sin sumar pomodoro

4. **Scenario**: Gameplay automatico de la nave
   - **Given** la mision esta activa
   - **When** el timer corre
   - **Then** la nave orbita automaticamente, dispara rafagas a intervalos aleatorios, y los fragmentos salen despedidos a velocidades variables

5. **Scenario**: Secuencia de disparo suave
   - **Given** la nave esta orbitando y decide disparar
   - **When** comienza la secuencia de disparo
   - **Then** la nave gira suavemente hacia el asteroide (AIMING), desacelera por inercia, dispara bala por bala con cadencia pausada (SHOOTING), y luego gira suavemente de vuelta a su orientacion de orbita (RETURNING) recuperando velocidad gradualmente

6. **Scenario**: Recoleccion por rayo tractor
   - **Given** hay fragmentos flotando y la nave orbita
   - **When** un fragmento esta dentro del rango del rayo tractor
   - **Then** la nave dispara un rayo visible hacia el fragmento mas cercano en rango, lo atrae a velocidad determinada y lo recolecta al llegar a la nave. Solo atrae 1 fragmento a la vez por rayo (base).

7. **Scenario**: Fragmentos fuera de alcance del rayo
   - **Given** la nave dispara y genera fragmentos
   - **When** los fragmentos salen despedidos fuera del rango del rayo tractor
   - **Then** se pierden definitivamente, reduciendo la recoleccion total de la mision

---

### User Story 2 - Sistema de Talentos (Priority: P2)

El jugador gasta fragmentos acumulados para comprar mejoras permanentes que potencian
su nave (velocidad de disparo, cantidad de balas, rango y velocidad del rayo tractor, etc.).

**Why this priority**: Da proposito a los fragmentos y motivacion para completar mas
pomodoros. Es el progression loop que sostiene el engagement.

**Independent Test**: Acumular fragmentos en misiones -> ir a Talents -> comprar upgrade
-> verificar efecto en la siguiente mision.

**Acceptance Scenarios**:

1. **Scenario**: Comprar un talento
   - **Given** el jugador tiene suficientes fragmentos y un talento no esta al maximo
   - **When** presiona "Upgrade" en ese talento
   - **Then** se descuentan los fragmentos (costo = nivel * 5), el nivel sube, y el efecto se aplica en la proxima mision

2. **Scenario**: Talento al maximo nivel
   - **Given** un talento esta en su nivel maximo
   - **When** el jugador lo ve en la pantalla de talentos
   - **Then** se muestra como "MAX" y no se puede comprar mas

3. **Scenario**: Fragmentos insuficientes
   - **Given** el jugador no tiene suficientes fragmentos
   - **When** intenta comprar un upgrade
   - **Then** la compra no se realiza y se indica visualmente que no alcanza

---

### User Story 3 - Configuracion de Ajustes (Priority: P3)

El jugador configura volumenes de audio (SFX y ambiente) y duraciones de pomodoro
y descanso desde una pantalla de Settings accesible desde el menu.

**Why this priority**: Personalizar la experiencia es importante pero no bloquea el
core gameplay. Permite adaptar el juego a las preferencias individuales.

**Independent Test**: Ir a Settings -> mover sliders de volumen -> cambiar duracion
de pomodoro -> iniciar mision -> verificar que la duracion es la configurada.

**Acceptance Scenarios**:

1. **Scenario**: Cambiar duracion del pomodoro
   - **Given** el jugador esta en Settings con pomodoro en 25 min
   - **When** presiona ">" para avanzar a 30 min
   - **Then** la proxima mision dura 30 minutos

2. **Scenario**: Ajustar volumen SFX
   - **Given** el jugador esta en Settings
   - **When** arrastra el slider de SFX al 40%
   - **Then** los sonidos de click y acciones se reproducen al 40% de volumen

3. **Scenario**: Ajustar volumen ambiente
   - **Given** el jugador esta en Settings con ambient sonando
   - **When** arrastra el slider de ambiente
   - **Then** el volumen del loop ambiental cambia en tiempo real

---

### User Story 4 - Sistema de Descanso (Priority: P4)

Al completar una mision, se activa un banner de descanso con cuenta regresiva
en la parte inferior del menu. Al terminar el countdown, indica que el jugador
esta listo para otra mision.

**Why this priority**: Complementa la tecnica Pomodoro pero no es critico para el MVP.
El juego funciona sin breaks.

**Independent Test**: Completar mision -> verificar banner con countdown -> esperar
que termine -> verificar mensaje "Ready for mission" con pulse.

**Acceptance Scenarios**:

1. **Scenario**: Break se activa tras mision completada
   - **Given** el jugador completa una mision exitosamente
   - **When** vuelve al menu
   - **Then** aparece un banner en la parte inferior con "Break MM:SS" y la info de la mision

2. **Scenario**: Break countdown termina
   - **Given** el break esta activo y el countdown llega a 0
   - **When** el timer se agota
   - **Then** el banner muestra "Ready for mission" en verde con pulso sinusoidal suave

3. **Scenario**: Break se desactiva al iniciar nueva mision
   - **Given** el break esta activo (countdown o ready)
   - **When** el jugador inicia una nueva mision
   - **Then** el break se desactiva automaticamente

4. **Scenario**: Break no se activa al abortar
   - **Given** el jugador aborta una mision
   - **When** vuelve al menu via AbortScene
   - **Then** no se activa ningun break

---

### User Story 5 - Game Juice: Movimiento Organico y Efectos (Priority: P5)

La nave tiene micro-oscilaciones organicas, screenshake sutil al impactar,
particulas de impacto, y la UI tiene hover en botones y barra de progreso.

**Why this priority**: Es polish visual. El juego es completamente funcional sin
esto, pero mejora significativamente la sensacion y la calidad percibida.

**Independent Test**: Iniciar mision -> observar wobble de la nave -> observar
screenshake al impacto -> verificar particulas -> verificar hover en botones del menu.

**Acceptance Scenarios**:

1. **Scenario**: Wobble orbital de la nave
   - **Given** la nave esta orbitando el asteroide
   - **When** pasa el tiempo
   - **Then** la nave tiene micro-desplazamientos perpendiculares a la orbita (3-5 px, multiples frecuencias) sin patron repetitivo

2. **Scenario**: Screenshake al impacto
   - **Given** un proyectil impacta el asteroide
   - **When** se detecta la colision
   - **Then** la camara se desplaza aleatoriamente 2-4 px con decaimiento exponencial (~0.15s)

3. **Scenario**: Hover en botones
   - **Given** el jugador esta en el menu
   - **When** pasa el mouse sobre un boton
   - **Then** el boton cambia de color/brillo como feedback visual

4. **Scenario**: Parallax de fondo en mision
   - **Given** la mision esta activa y la nave orbita
   - **When** el jugador observa el fondo
   - **Then** se ven 3 capas de parallax con profundidad: planetas/estrellas/via lactea lejanos (capa trasera), asteroides cercanos (capa media), y ocasionalmente un asteroide grande que pasa por encima de todo (capa frontal)

---

### Edge Cases

- Que pasa si el jugador intenta crear una tarea con nombre vacio?
- Que pasa si el jugador cierra el juego durante una mision activa?
- Que pasa si se intenta iniciar una mision sin tarea seleccionada?
- Que pasa si el jugador tiene 0 fragmentos e intenta comprar un talento de nivel 1 (costo 5)?
- Como se comporta el break banner si el jugador inicia mision inmediatamente sin esperar?
- Que pasa con el audio si Pygame no puede inicializar el mixer?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST permitir crear tareas con nombre libre (max 40 caracteres)
- **FR-002**: System MUST mostrar una lista scrollable de tareas con acciones Add, Start, Delete
- **FR-003**: System MUST ejecutar misiones con nave orbitando automaticamente, girando suavemente hacia el asteroide para disparar (AIMING), disparando con cadencia pausada (SHOOTING), y volviendo a orientacion de orbita (RETURNING), todo con transiciones interpoladas y velocidad orbital por inercia
- **FR-004**: System MUST implementar timer countdown configurable (default 25 min) en formato MM:SS
- **FR-005**: System MUST generar fragmentos al impactar el asteroide con velocidades variables de dispersion; los fragmentos flotan libremente y pueden perderse si escapan fuera del rango del rayo tractor
- **FR-005b**: System MUST recolectar fragmentos mediante rayo tractor visible: la nave emite un rayo hacia el fragmento mas cercano dentro del rango, lo atrae a velocidad fija y lo recolecta al contacto. Base: 1 rayo simultaneo, mejorable por talentos (rango, velocidad de atraccion, rayos adicionales)
- **FR-006**: System MUST conservar 100% de fragmentos al completar y 30% al abortar
- **FR-007**: System MUST implementar 16 talentos en 4 ramas (Armamento, Recoleccion, Navegacion, Economia) con niveles, costo progresivo (N * 5, modificable por talent_discount) y efectos acumulativos
- **FR-008**: System MUST proveer Settings con sliders de volumen (SFX/Ambiente) y selectores de duracion
- **FR-009**: System MUST activar break banner tras mision completada con countdown y fase "ready"
- **FR-010**: System MUST reproducir audio SFX y ambiente via AudioManager con control de volumen independiente
- **FR-011**: System MUST mostrar pantalla de introduccion con efecto typewriter solo al abrir el juego
- **FR-012**: System MUST soportar transiciones fade-to-black entre escenas (0.5s)
- **FR-013**: System MUST mostrar imagenes narrativas (story) antes de misiones segun pomodoros completados
- **FR-014**: System MUST renderizar fondo parallax de 3 capas procedurales en MissionScene: fondo lejano (estrellas, planetas, via lactea), asteroides decorativos cercanos, y asteroide frontal ocasional semi-transparente

### Key Entities

- **Task**: Nombre libre (str, max 40 chars), contador de pomodoros completados (int)
- **Ship**: Posicion orbital (angulo), estado (ORBITING/AIMING/SHOOTING/RETURNING), angulo de facing (interpolado), velocidad orbital actual, talentos aplicados, rayos tractor activos (lista de TractorBeam)
- **Asteroid**: Poligono procedural (14 vertices con ruido), radio base ~40 px
- **Fragment**: Posicion, velocidad variable (pueden escapar de la orbita), color aleatorio (naranja/amarillo/verde/cyan), estado (FREE/LOCKED: siendo atraido por un rayo)
- **TractorBeam**: Rayo visible entre nave y fragmento objetivo; atrae 1 fragmento a la vez a velocidad fija. Selecciona automaticamente el fragmento mas cercano dentro del rango. Se libera al recolectar el fragmento y busca el siguiente.
- **Talent**: ID, nombre, nivel actual (int), nivel maximo (int), efecto por nivel
- **AudioManager**: Diccionario de sonidos cargados, volumen SFX (float), volumen ambiente (float)

### Tabla de Talentos

**Rama Armamento (Weapons)**:

| ID              | Nombre          | Max | Efecto por nivel           |
| --------------- | --------------- | --- | -------------------------- |
| fire_rate       | Rapid Fire      | 5   | -10% intervalo entre rafagas |
| bullet_count    | Multi Shot      | 5   | +1 bala por rafaga         |
| burst_speed     | Trigger Finger  | 3   | -15% intervalo entre balas dentro de una rafaga |
| piercing        | Deep Drill      | 3   | +1 fragmento extra por impacto (chance 20%/nivel) |
| crit_shot       | Overcharge      | 4   | 5% chance/nivel de disparo critico (x2 fragmentos en ese impacto) |

**Rama Recoleccion (Tractor Beam)**:

| ID              | Nombre          | Max | Efecto por nivel           |
| --------------- | --------------- | --- | -------------------------- |
| beam_range      | Long Range Beam | 5   | +20% rango del rayo tractor |
| beam_speed      | Beam Accelerator| 5   | +15% velocidad de atraccion del rayo |
| beam_count      | Multi Beam      | 2   | +1 rayo tractor simultaneo (base 1, max 3) |
| double_frag     | Double Fragment | 5   | +8% chance fragmento doble |
| auto_collect    | Drone Sweep     | 3   | Cada 10s/8s/5s recolecta el fragmento mas lejano fuera del rango del rayo |

**Rama Navegacion (Ship)**:

| ID              | Nombre          | Max | Efecto por nivel           |
| --------------- | --------------- | --- | -------------------------- |
| orbit_speed     | Thruster Boost  | 5   | +10% velocidad orbital     |
| aim_speed       | Quick Draw      | 3   | +20% velocidad de giro en AIMING/RETURNING |
| inertia_control | Drift Stabilizer| 3   | +15% velocidad minima durante SHOOTING |

**Rama Economia (Resources)**:

| ID              | Nombre          | Max | Efecto por nivel           |
| --------------- | --------------- | --- | -------------------------- |
| abort_save      | Emergency Vault | 3   | +10% fragmentos conservados al abortar (base 30%) |
| end_bonus       | Completion Bonus| 3   | +5% fragmentos bonus al completar mision |
| talent_discount | Efficient Corp  | 2   | -1/-2 al costo de todos los talentos (minimo costo 1) |

### Parametros del Sistema

| Parametro          | Valor          | Notas                                |
| ------------------ | -------------- | ------------------------------------ |
| Resolucion         | 900 x 600      |                                      |
| FPS                | 60              |                                      |
| Duracion pomodoro  | configurable    | Default 25 min, opciones: 1,5,15,25,30,45,60 |
| Duracion descanso  | configurable    | Default 5 min, opciones: 1,3,5,10    |
| Orbita radio       | 150 px          |                                      |
| Orbita velocidad   | 0.4 rad/s       | Base, modificable por talentos       |
| Proyectil vel      | 200 px/s        |                                      |
| Rayo tractor rango | 120 px          | Base, mejorable por talento Long Range Beam |
| Rayo tractor vel   | 80 px/s         | Velocidad de atraccion base, mejorable por Beam Accelerator |
| Rayos simultaneos  | 1               | Base, mejorable por talento Multi Beam (max 3) |
| Recoleccion dist   | < 15 px         | Distancia nave-fragmento para pickup  |

### Comportamiento de la Nave (Ship)

La nave orbita el asteroide de forma continua y realiza secuencias de disparo automaticas.
El movimiento debe sentirse **fluido y organico**, sin cambios bruscos de estado.

**Estados de la nave**:

```
ORBITING → AIMING → SHOOTING → RETURNING → ORBITING
```

| Estado      | Descripcion                                                          | Velocidad orbital       | Facing                              |
| ----------- | -------------------------------------------------------------------- | ----------------------- | ----------------------------------- |
| ORBITING    | Navegacion normal por la orbita                                      | 100% (base + talentos)  | Tangente a la orbita (direccion de avance) |
| AIMING      | Giro suave hacia el asteroide antes de disparar                      | Desacelera gradualmente (~40-50% de base) | Interpola (lerp) desde tangente hacia el centro del asteroide |
| SHOOTING    | Dispara rafaga de proyectiles con cadencia pausada entre balas       | Reducida (~30-40% de base), simula inercia | Apuntando al centro del asteroide   |
| RETURNING   | Giro suave de vuelta a la orientacion de orbita                      | Acelera gradualmente hasta 100% | Interpola (lerp) desde asteroide hacia tangente de orbita |

**Secuencia de disparo**:

1. La nave decide disparar (intervalo aleatorio entre rafagas).
2. **AIMING**: La nave gira suavemente (lerp) hacia el asteroide mientras desacelera. No frena en seco: la velocidad orbital baja gradualmente.
3. **SHOOTING**: Una vez alineada, dispara la rafaga bala por bala con una cadencia pausada (intervalo entre balas mayor que el actual, para que se perciba la secuencia). Durante el disparo, la nave sigue avanzando lentamente por la orbita (efecto de inercia).
4. **RETURNING**: Al terminar la rafaga, la nave gira suavemente de vuelta a la orientacion tangencial y recupera su velocidad orbital de forma gradual.
5. **ORBITING**: Navegacion normal hasta la proxima secuencia de disparo.

**Principios de movimiento**:

- **Sin cambios bruscos**: Todas las transiciones de angulo y velocidad son interpoladas (lerp/ease).
- **Inercia**: La nave nunca se detiene completamente; siempre conserva movimiento orbital residual.
- **Coherencia relajante**: El ritmo de disparo y los giros suaves refuerzan la sensacion de calma automatica.
- **Orbita invisible**: La trayectoria orbital es puramente logica. **No se dibuja** ningun circulo, linea ni guia visual de la orbita. La nave simplemente "flota" alrededor del asteroide de forma natural.

### Sistema de Rayo Tractor (Recoleccion de Fragmentos)

La recoleccion de fragmentos se realiza mediante **rayos tractores visibles** que la nave
emite hacia los fragmentos cercanos. Reemplaza el sistema de atraccion magnetica invisible.

**Comportamiento base** (sin talentos):

1. La nave emite **1 rayo tractor** a la vez.
2. El rayo busca automaticamente el **fragmento mas cercano** dentro de su rango.
3. Al encontrarlo, se dibuja una **linea visible** (rayo) entre la nave y el fragmento.
4. El fragmento es atraido hacia la nave a una **velocidad fija** (base 80 px/s).
5. Al llegar a distancia de recoleccion (< 15 px), el fragmento se recolecta.
6. El rayo se libera e inmediatamente busca el **siguiente fragmento mas cercano**.
7. Los fragmentos fuera de rango siguen su trayectoria libre y pueden perderse.

**Estados de un fragmento**:

- **FREE**: Flotando libremente tras ser despedido del asteroide. No esta siendo atraido.
- **LOCKED**: Un rayo tractor lo tiene como objetivo. Se mueve hacia la nave.

Un fragmento LOCKED no puede ser objetivo de otro rayo (cada rayo atrae un fragmento distinto).

**Visual del rayo**:

- Linea sutil desde la nave hasta el fragmento, con color tenue (CYAN con alpha bajo).
- Puede tener un leve pulso de opacidad o grosor para sentirse vivo.
- Coherente con la estetica relajante: no debe ser un efecto agresivo.

**Talentos relacionados**:

| Talento | Efecto sobre el rayo |
|---------|---------------------|
| Long Range Beam | Aumenta el radio de busqueda del rayo (+20%/nivel) |
| Beam Accelerator | Aumenta la velocidad a la que el rayo atrae fragmentos (+15%/nivel) |
| Multi Beam | Agrega rayos simultaneos (+1/nivel, base 1, max 3). Cada rayo busca un fragmento distinto. |

### Sistema de Parallax (Fondo de Mision)

El fondo de la MissionScene usa **3 capas de parallax** que dan profundidad y la sensacion
de que la nave se encuentra dentro de un campo de asteroides. Todo es **generado proceduralmente**.

**Orden de renderizado** (de atras hacia adelante):

```
Capa 1 (fondo lejano)  →  Capa 2 (asteroides cercanos)  →  Nave/Asteroide/Fragmentos  →  Capa 3 (primer plano)
```

#### Capa 1: Fondo Lejano (detras de todo)

Representa el espacio profundo. Se mueve **muy lentamente** (parallax factor ~0.05-0.1).

| Elemento       | Cantidad | Generacion procedural | Visual |
|---------------|----------|----------------------|--------|
| Estrellas      | 80-120   | Posiciones aleatorias, tamano 1-3 px | Puntos blancos/celestes con brillo variable (alpha aleatorio, leve parpadeo sinusoidal) |
| Planetas       | 2-3      | Circulos grandes (20-50 px radio), posiciones aleatorias | Colores suaves y apagados (azul oscuro, violeta, terracota). Gradiente o sombreado simple. Sin detalle excesivo. |
| Via Lactea     | 1        | Banda diagonal difusa generada con ruido o multiples circulos con alpha muy bajo | Tonos violeta/azul muy tenues (alpha ~15-25). Efecto de nube/nebulosa. Sutil, casi imperceptible. |

**Principios**: Colores desaturados y con alpha bajo. Nada debe competir visualmente con la accion en primer plano. La capa debe sentirse como un telón de fondo atmosferico.

#### Capa 2: Asteroides Cercanos (detras de la nave)

Asteroides flotando que dan contexto de "campo de asteroides". Se mueven **un poco mas rapido**
que la capa de fondo pero todavia lentos (parallax factor ~0.2-0.3).

| Elemento        | Cantidad | Generacion procedural | Visual |
|----------------|----------|----------------------|--------|
| Asteroides med  | 5-8      | Poligonos irregulares (6-10 vertices con ruido), radio 8-25 px | Grises oscuros variados (70-110 RGB), siluetas. Rotacion lenta aleatoria. |

**Principios**: Estos asteroides son decorativos, no interactivos. Deben verse como parte del entorno,
no confundirse con el asteroide que se esta minando. Mantener tonos mas oscuros y tamaños menores que el asteroide central.

#### Capa 3: Primer Plano (por encima de la nave)

Asteroides grandes que pasan **ocasionalmente** por delante de todo, reforzando la sensacion de
profundidad y de estar inmerso en el campo. Se mueven **mas rapido** (parallax factor ~1.5-2.0).

| Elemento        | Frecuencia | Generacion procedural | Visual |
|----------------|------------|----------------------|--------|
| Asteroide grande | 1 cada 15-30s | Poligono irregular (10-14 vertices), radio 60-120 px | Gris oscuro con alpha medio (~40-60%). Semi-transparente para no tapar la accion. Cruza la pantalla de un lado a otro. |

**Principios**: Poco frecuente para no distraer. Semi-transparente para que el jugador siempre
vea la accion debajo. El movimiento debe ser lento y predecible (lineal, sin giros bruscos).
Efecto cinematografico sutil.

#### Movimiento del Parallax

El desplazamiento de cada capa se vincula al **movimiento orbital de la nave** (o a un scroll
virtual continuo si la camara es estatica). Las capas mas lejanas se mueven menos, las cercanas mas.

| Capa | Parallax Factor | Velocidad relativa | Referencia de movimiento |
|------|----------------|-------------------|------------------------|
| 1 (fondo) | 0.05-0.1 | Casi estatica, drift muy sutil | Scroll continuo lento |
| 2 (media) | 0.2-0.3 | Movimiento perceptible pero suave | Vinculado al angulo orbital de la nave |
| 3 (frente) | 1.5-2.0 | Cruza la pantalla en ~8-15s | Trayectoria lineal independiente |

#### Consideraciones Tecnicas

- **Generacion al inicio de la mision**: Las capas 1 y 2 se generan una vez al crear MissionScene. Se reciclan/wrappean al salir de pantalla.
- **Capa 3 spawner**: Un timer genera asteroides frontales a intervalos aleatorios (15-30s). Entran por un borde y salen por el opuesto.
- **Performance**: Mantener el conteo de objetos bajo. Las estrellas son puntos simples, los planetas circulos con pocos draws, los asteroides poligonos de pocos vertices.
- **Coherencia relajante**: El parallax debe agregar inmersion sin distraer. Todo movimiento es lento, fluido y predecible.

### Arquitectura del Game Loop y Clase Game

El juego se estructura alrededor de una clase **Game** que actua como estado central y
orquestador del game loop. El loop es **async** para compatibilidad con Pygbag (web).

**Clase Game (estado central)**:

| Atributo | Tipo | Descripcion |
|----------|------|-------------|
| `screen` | Surface | Surface principal de Pygame (900x600) |
| `clock` | Clock | Control de framerate (60 FPS) |
| `scene` | Scene | Escena activa (se swapea en transiciones) |
| `tasks` | list[dict] | Lista de tareas del jugador ({name, pomodoros}) |
| `fragments` | int | Total de fragmentos acumulados |
| `talents` | dict | Niveles de cada talento {id: nivel} |
| `sfx_volume` | float | Volumen SFX (0.0-1.0, default 0.7) |
| `ambient_volume` | float | Volumen ambiente (0.0-1.0, default 0.5) |
| `pomodoro_minutes` | int | Duracion del pomodoro (default 25) |
| `break_minutes` | int | Duracion del descanso (default 5) |
| `break_active` | bool | Si el break esta activo |
| `break_remaining` | float | Segundos restantes del break |
| `break_ready` | bool | Si el countdown del break termino |
| `audio` | AudioManager | Instancia del gestor de audio |
| `font`, `font_title`, `font_heading`, `font_timer`, `font_small` | Font | Fuentes cargadas |

**Game loop** (pseudocodigo):

```python
async def main():
    pygame.init()
    game = Game()
    game.scene = IntroScene(game)  # Solo al arrancar

    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            game.scene.handle_event(event)
        game.scene.update(dt)
        game.update_break(dt)  # Si break activo
        game.scene.draw(screen)
        game.draw_break_banner(screen)  # Si en menu/talents/settings
        pygame.display.flip()
        await asyncio.sleep(0)  # Yield para Pygbag
```

**Patron de escenas (contrato)**:

Cada escena es una clase que implementa 3 metodos:

- `handle_event(event)`: Procesa eventos de Pygame (clicks, teclas, mouse)
- `update(dt)`: Actualiza logica con delta time en segundos
- `draw(surf)`: Dibuja la escena en la surface

Las transiciones entre escenas se hacen via `FadeTransition(game, next_scene, duration=0.5)`.

### Escenas del Juego

```
IntroScene         - Pantalla de bienvenida con titulo y texto typewriter
MenuScene          - Lista de tareas, input de texto, navegacion
SettingsScene      - Ajustes: volumen, duracion de pomodoro
TalentScene        - Arbol de mejoras permanentes (16 talentos en 4 ramas)
StoryScene         - Imagen narrativa pre-mision (si hay assets)
MissionScene       - Gameplay principal (nave orbitando + mineria)
AbortScene         - Resumen al abortar una mision
FadeTransition     - Transicion fade-to-black entre escenas (0.5s)
```

**Break banner**: Banner persistente en parte inferior de Menu/Talents/Settings.
Estado vive en el objeto Game, no es escena independiente.

### Flujo de Escenas

```
Intro -> Menu                                         (primera vez)
Menu -> [Story] -> Mission -> Menu (con break banner) (completada)
Menu -> [Story] -> Mission -> Abort -> Menu           (abortada)
Menu -> Talents -> Menu
Menu -> Settings -> Menu
```

### Layout del MenuScene

El menu principal muestra el titulo del juego, la lista de tareas y los botones de navegacion.
Los elementos deben estar distribuidos sin solapamientos.

```
+------------------------------------------+
|                                          |
|             POMI Corp.                   |   <- font_title, CYAN, centrado horizontal, Y ~40
|                                          |
|  [ input de texto .............. ] [Add] |   <- zona de input, Y ~100
|                                          |
|  > Tarea 1  (2 pom)           [Del]      |   <- lista scrollable, Y ~140 a ~420
|    Tarea 2  (0 pom)           [Del]      |
|    ...                                   |
|                                          |
|           [ Start Mission ]              |   <- boton principal, Y ~440
|                                          |
|     [ Talents ]     [ Settings ]         |   <- botones secundarios, Y ~500
|                                          |
|  ======= Break banner (36px) =========  |   <- solo si break activo
+------------------------------------------+
```

**Reglas de layout**:

- El titulo **"POMI Corp."** se renderiza con `font_title` en CYAN, centrado horizontalmente, en la zona superior (~Y 40).
- Los botones **Talents** y **Settings** se ubican en la zona inferior, por debajo de "Start Mission", con suficiente margen respecto al titulo y a la lista de tareas.
- Si el break banner esta activo (36px inferiores), los botones deben quedar por encima del banner.
- La lista de tareas ocupa la zona central con scroll si hay muchas tareas.

### Layout del IntroScene

```
+------------------------------------------+
|                                          |
|                                          |
|            POMI Corp.                    |   <- font_title, CYAN, fade-in 1.0s
|                                          |
|   "Bienvenido a POMI Corp."             |   <- font, WHITE, typewriter ~28 chars/s
|   "Cargue sus tareas para comenzar..."   |   <- pausa 0.4s entre lineas
|   "Aproveche los recursos para..."       |
|                                          |
|                                          |
|        [click/tecla para skip]           |   <- font_small, GRAY, sutil
+------------------------------------------+
```

- Fade-in del titulo: 1.0s. Pausa post-titulo: 0.6s.
- Typewriter: ~28 chars/s (CHAR_DELAY = 0.035s). Pausa entre lineas: 0.4s.
- Auto-avance al menu con fade tras 1.5s de pausa final.
- Skip en cualquier momento (click o tecla) salta directo al menu con fade.
- Solo se muestra al abrir el juego, no entre misiones.

### Layout del SettingsScene

```
+------------------------------------------+
|                                          |
|              SETTINGS                    |   <- font_heading, WHITE, centrado
|                                          |
|   SFX Volume    [=====>----]  70%        |   <- slider arrastrable
|                                          |
|   Ambience      [====>-----]  50%        |   <- slider arrastrable, actualiza en vivo
|                                          |
|   Pomodoro      <  25 min  >             |   <- selector con < > ciclando valores
|                                          |
|   Break         <   5 min  >             |   <- selector con < > ciclando valores
|                                          |
|              [ Back ]                    |   <- vuelve al menu
|                                          |
|  ======= Break banner (36px) =========  |
+------------------------------------------+
```

- Cambios se aplican inmediatamente (sin boton guardar).
- Valores de pomodoro: 1, 5, 15, 25, 30, 45, 60 min.
- Valores de break: 1, 3, 5, 10 min.

### Layout del TalentScene

```
+------------------------------------------+
|                                          |
|    TALENTS           Fragments: 42       |   <- font_heading + contador
|                                          |
|  --- Weapons ---                         |   <- separador de rama
|  Rapid Fire      Lv 2/5  [Upgrade: 10]  |
|  Multi Shot      Lv 0/5  [Upgrade: 5]   |
|  Trigger Finger  Lv 0/3  [Upgrade: 5]   |
|  Deep Drill      Lv 0/3  [Upgrade: 5]   |
|  Overcharge      Lv 0/4  [Upgrade: 5]   |
|  --- Tractor Beam ---                    |
|  Long Range Beam Lv 1/5  [Upgrade: 10]  |
|  ...                                     |   <- scroll si no caben
|  --- Ship ---                            |
|  ...                                     |
|  --- Resources ---                       |
|  ...                                     |
|                                          |
|              [ Back ]                    |
|  ======= Break banner (36px) =========  |
+------------------------------------------+
```

- 16 talentos en 4 ramas con separadores visuales.
- Cada talento muestra: nombre, nivel actual/max, boton Upgrade con costo.
- Si nivel == max: muestra "MAX" en vez de boton.
- Si fragmentos insuficientes: boton visualmente deshabilitado.
- Scroll vertical si los 16 talentos no caben en pantalla.

### Layout del MissionScene HUD

```
+------------------------------------------+
|  Tarea: "Estudiar fisica"     MM:SS      |   <- font_small + font_timer, zona superior
|                                          |
|          [Parallax Capa 1]               |
|      [Parallax Capa 2]                   |
|                                          |
|            ~~~  asteroide  ~~~           |   <- centro de pantalla
|         nave -->  *   <-- fragmentos     |
|              [rayos tractor]             |
|                                          |
|          [Parallax Capa 3]               |
|                                          |
|  Fragments: 12          [ Abort ]        |   <- font_small, zona inferior
+------------------------------------------+
```

- Nombre de tarea y timer en la zona superior.
- Contador de fragmentos y boton Abort en la zona inferior.
- La accion (nave, asteroide, fragmentos, rayos) ocupa el centro.
- El parallax se renderiza en su orden de capas.
- No se dibuja la orbita (trayectoria invisible).

### Layout del AbortScene

```
+------------------------------------------+
|                                          |
|          MISSION ABORTED                 |   <- font_heading, RED
|                                          |
|   Task: "Estudiar fisica"               |
|   Time elapsed: 12:34                    |
|   Time remaining: 12:26                  |
|                                          |
|   Fragments mined: 24                    |
|   Fragments kept (30%): 7               |   <- penalidad visible
|                                          |
|            [ Continue ]                  |   <- vuelve al menu
|                                          |
+------------------------------------------+
```

- Resumen de la mision abortada con penalidad visible.
- Boton "Continue" para volver al menu.
- No se activa break al abortar.

### Layout del StoryScene

```
+------------------------------------------+
|                                          |
|                                          |
|         [story_XX.png centrada]          |   <- imagen escalada a pantalla
|                                          |
|                                          |
|                                          |
|    [click o SPACE para continuar]        |   <- font_small, GRAY, sutil
+------------------------------------------+
```

**Seleccion de imagen**:

Las imagenes se almacenan en `assets/images/` con el patron `story_XX.png` (ej: `story_01.png`, `story_02.png`).
La imagen mostrada depende del **total de pomodoros completados** por el jugador:

| Pomodoros completados | Imagen mostrada |
|----------------------|-----------------|
| 0-2                  | story_01.png    |
| 3-5                  | story_02.png    |
| 6+                   | story_03.png (o la mas alta disponible) |

**Comportamiento**:

- Si no hay imagenes en `assets/images/`, la StoryScene se salta y se va directo a MissionScene.
- Si la imagen correspondiente no existe, se muestra la ultima disponible.
- Click o SPACE para continuar a MissionScene con fade.
- La imagen se escala/centra manteniendo aspect ratio dentro de la resolucion (900x600).

### Paleta de Colores

| Nombre        | RGB             | Uso                          |
| ------------- | --------------- | ---------------------------- |
| BG_COLOR      | (0, 0, 0)      | Fondo general                |
| WHITE         | (255, 255, 255) | Texto principal              |
| GRAY          | (160, 160, 160) | Texto secundario             |
| DARK_GRAY     | (60, 60, 60)    | Separadores, inactivos       |
| CYAN          | (0, 220, 255)   | Nave, acentos primarios      |
| YELLOW        | (255, 220, 50)  | Fragmentos, contadores       |
| RED           | (220, 60, 60)   | Alertas, abort/delete        |
| GREEN         | (60, 220, 60)   | Confirmacion, start          |
| ORANGE        | (255, 160, 40)  | Talentos, acentos secundarios|
| ASTEROID_COLOR| (130, 130, 130) | Asteroide                    |

### Tipografia

Fonts embebidas en `assets/fonts/` (Google Fonts, licencia OFL). TrueType puras (.ttf).

| Uso              | Font                     | Tamano | Variable en Game     |
| ---------------- | ------------------------ | ------ | -------------------- |
| Titulos          | Chakra Petch Bold        | 38     | `font_title`         |
| Subtitulos       | Chakra Petch Regular     | 28     | `font_heading`       |
| Timer de mision  | Share Tech Mono          | 42     | `font_timer`         |
| Texto UI/cuerpo  | Share Tech Mono          | 18     | `font`               |
| Hints/captions   | Share Tech Mono          | 14     | `font_small`         |

### Audio

Filosofia: ambiental y no intrusivo. Sin musica. Dos canales: SFX y Ambiente.

| Archivo              | Tipo     | Descripcion                          | Estado      |
| -------------------- | -------- | ------------------------------------ | ----------- |
| `ui_click.wav`       | SFX      | Click suave tonal (800Hz, 0.08s)     | Implementado|
| `ambient_menu.wav`   | Ambiente  | Drone espacial, loop 10s             | Implementado|
| `ship_shoot.wav`     | SFX      | Laser suave, corto                   | Pendiente   |
| `asteroid_hit.wav`   | SFX      | Impacto solido pero sutil            | Pendiente   |
| `fragment_collect.wav`| SFX     | Tintineo cristalino                  | Pendiente   |
| `mission_complete.wav`| SFX     | Acorde satisfactorio                 | Pendiente   |
| `mission_abort.wav`  | SFX      | Tono descendente suave               | Pendiente   |
| `talent_upgrade.wav` | SFX      | Sonido de mejora/nivel up            | Pendiente   |
| `break_ready.wav`    | SFX      | Chime ambiental suave                | Pendiente   |

### Generacion Procedural de Audio (generate_audio.py)

Los archivos de audio se generan con un script Python puro (`generate_audio.py`) sin
dependencias externas. Esto permite reproducir los assets de audio desde cero en cualquier
entorno. Los archivos generados son **placeholders** reemplazables por audio profesional.

**Formato de salida**: WAV mono 16-bit, 44100 Hz.

**Tecnicas de generacion**:

| Tipo de sonido | Tecnica | Parametros clave |
|---------------|---------|-----------------|
| Click UI | Sine burst con decay exponencial | 800 Hz, 0.08s, decay exp(-t*60), vol 0.4 |
| Ambient drone | Capas de senos con modulacion lenta + ruido filtrado | Acorde A1-E2-A2-E3 (55-165 Hz), mod 0.05 Hz, ruido 0.015, fade in/out 0.5s, loop 10s |
| Laser (disparo) | Sine sweep descendente con decay | Freq alta->baja, ~0.1s |
| Impacto | Noise burst con envelope percusivo | ~0.08s, decay rapido |
| Tintineo (recoleccion) | Sine de alta frecuencia con decay | ~1200 Hz, 0.12s |
| Acorde (mision completa) | Capas de senos en acorde mayor | ~0.5s, fade out |
| Tono descendente (abort) | Sine sweep descendente lento | ~0.3s |
| Upgrade | Sine sweep ascendente | Freq baja->alta, ~0.2s |
| Chime (break ready) | Sine puro con decay suave | ~800 Hz, 0.3s |

**Ejecucion**: `python generate_audio.py` genera todos los archivos en `assets/audio/`.
Se ejecuta una vez durante el setup del proyecto. No es necesario en runtime.

### Restricciones de Plataforma (Pygbag / Web)

El juego debe funcionar como **build web via Pygbag** ademas de desktop nativo.
Estas restricciones deben considerarse durante toda la implementacion.

**Game loop async** (obligatorio):

```python
import asyncio

async def main():
    # ... game loop ...
    while running:
        # ... update, draw ...
        await asyncio.sleep(0)  # Cede control al browser

asyncio.run(main())
```

**Restricciones tecnicas**:

| Area | Restriccion | Solucion |
|------|------------|---------|
| Game loop | Debe ser `async` con `await asyncio.sleep(0)` en cada frame | Usar patron async desde el inicio |
| Fonts | SDL_ttf no soporta CFF outlines | Usar solo TrueType puras (.ttf con outlines TT) |
| Audio | Formatos soportados: WAV, OGG | No usar MP3. Generar en WAV. |
| Audio | Autoplay bloqueado por browsers | El audio comienza tras primera interaccion del usuario |
| File I/O | No hay filesystem persistente en web | Persistencia via localStorage (backlog) |
| Imports | Solo stdlib + pygame disponibles | No usar dependencias externas en runtime |
| Assets | Deben estar en el directorio del proyecto | Pygbag empaqueta todo el directorio en el build |
| Threads | No disponibles en WASM | No usar threading; todo en el loop async |

**Comando de build**: `python -m pygbag --build main.py`
**Test local**: `python -m pygbag main.py` (sirve en localhost)
**Output**: Directorio `build/web/` con archivos HTML/JS/WASM listos para itch.io.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El jugador puede completar un ciclo completo (crear tarea -> mision -> recolectar -> upgrade) sin errores
- **SC-002**: El timer es preciso: desviacion menor a 1 segundo en una mision de 25 minutos
- **SC-003**: El juego mantiene 60 FPS estables durante toda la mision con fragmentos activos
- **SC-004**: El audio no presenta glitches, cortes ni latencia perceptible al reproducir SFX
- **SC-005**: El build web (Pygbag) funciona correctamente en navegadores modernos (Chrome, Firefox)
- **SC-006**: La experiencia es relajante: ningun sonido ni animacion resulta agresivo o intrusivo
- **SC-007**: Todos los talentos aplican sus efectos correctamente y se acumulan por nivel

### Principio de Diseno Central

> El juego debe ser **relajante y no demandar atencion**. El jugador lo deja
> corriendo de fondo mientras se concentra en su tarea real. La informacion visual
> y sonora debe ser **minimalista, suave y ambiental** - nunca intrusiva.

## Backlog de Ideas

> Ideas futuras. Evaluar antes de incorporar al plan.

- [ ] Persistencia de datos (guardar progreso en JSON/localStorage para web)
- [ ] Tipos de asteroide con diferentes resistencias/recompensas
- [ ] Estadisticas acumuladas (total de fragmentos minados, tiempo total, etc.)
- [ ] Notificacion sonora sutil cuando el pomodoro esta por terminar (ultimos 30s)
- [ ] Animacion de la nave al completar mision (celebracion sutil)
- [ ] Temas visuales desbloqueables (paletas de color alternativas)
