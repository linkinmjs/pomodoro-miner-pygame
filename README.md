# Pomodoro Miner

Un juego hibrido idle/pomodoro construido con Pygame. Combina la tecnica de productividad Pomodoro con una mecanica de mineria espacial: mientras trabajas en tus tareas del mundo real, tu nave orbita un asteroide, lo dispara y recolecta fragmentos que luego usas para mejorar tu nave.

## Concepto

El jugador crea tareas (estudio, trabajo, etc.) y lanza misiones de 25 minutos (configurable). Durante la mision:

- Una nave orbita automaticamente un asteroide central.
- La nave dispara proyectiles al asteroide a intervalos aleatorios.
- Los impactos generan fragmentos de recursos que se dispersan hacia la orbita.
- La nave los recolecta al pasar cerca gracias a un efecto magnético.
- Al completar la mision (no abortarla), los fragmentos se suman al inventario global.
- Los fragmentos se gastan en el arbol de talentos para mejorar la nave.

La idea central: **cuanto mas trabajas, mas fuerte se vuelve tu nave**.

## Requisitos

- **Python** 3.10 o superior
- **Pygame** 2.x

## Instalacion y ejecucion

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd pomodoro-miner-python

# Instalar dependencias
pip install pygame

# Ejecutar el juego
python main.py
```

## Features

### Sistema de tareas
- Crear y eliminar tareas desde el menu principal.
- Cada tarea registra cuantos pomodoros se completaron.
- Scroll para manejar listas largas.

### Mision (Pomodoro)
- Temporizador configurable (por defecto 60s para testing, cambiar `POMODORO_SECONDS` a `25 * 60` para uso real).
- Nave orbitando automaticamente el asteroide.
- Disparo automatico con intervalo aleatorio (15-30s base).
- Fragmentos se dispersan radialmente y se asientan sobre la orbita, facilitando la recoleccion.
- Sistema de magnet: la nave atrae fragmentos cercanos.
- **Completar** la mision = fragmentos guardados + pomodoro sumado.
- **Abortar** la mision = fragmentos perdidos (incentivo para terminar).

### Sistema de Talentos
Arbol de mejoras permanentes compradas con fragmentos:

| Talento | Niveles | Efecto por nivel |
|---|---|---|
| Rapid Fire | 5 | -10% intervalo de disparo |
| Magnetic Pull | 5 | +20% radio del magnet |
| Double Fragment | 5 | +8% chance de fragmento doble |
| Thruster Boost | 5 | +10% velocidad orbital |
| Tractor Beam | 3 | +30% fuerza del magnet |

**Costo**: nivel N cuesta `N * 5` fragmentos (nivel 1 = 5, nivel 2 = 10, ..., nivel 5 = 25).

## Controles

- **Mouse**: toda la interaccion es con clicks.
- Menu: escribir nombre de tarea, click en Add, Start o Delete.
- Mision: solo el boton "Abort Mission" es interactivo; el resto es automatico.
- Talentos: click en los botones de upgrade.

## Estructura del proyecto

```
pomodoro-miner-python/
  main.py       # Codigo fuente completo (single-file)
  README.md     # Este documento
  .gitignore    # Archivos ignorados por git
```

## Constantes configurables (en main.py)

| Constante | Default | Descripcion |
|---|---|---|
| `POMODORO_SECONDS` | 60 | Duracion de la mision en segundos |
| `ORBIT_RADIUS` | 150 | Radio de la orbita en pixeles |
| `ORBIT_SPEED` | 0.4 | Velocidad angular (rad/s) |
| `SHOOT_INTERVAL_RANGE` | (15, 30) | Rango del intervalo de disparo (s) |
| `MAGNET_RADIUS` | 60 | Radio de atraccion de fragmentos |
| `MAGNET_STRENGTH` | 300 | Fuerza de atraccion |
| `ORBIT_SETTLE_STRENGTH` | 40 | Fuerza con la que los fragmentos migran a la orbita |

## Licencia

Proyecto personal / educativo.
