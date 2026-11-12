# Timeline del proyecto Pac-Man
 
## 1. Planificación de referencia
 
```mermaid
gantt
    title Pac-Man - Planificacion de referencia
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    todayMarker off
 
    section Analisis y diseno
    Analisis del subject y arquitectura  :p1, 2026-10-15, 2026-10-16
 
    section Base
    Player y clase de movimiento         :p2, 2026-10-16, 2026-10-20
    Ghost y metodos de persecucion       :p3, 2026-10-19, 2026-10-22
 
    section Interfaz y config
    MazeUi, factory y EntitiesAdapter    :p4, 2026-10-20, 2026-10-24
    Parser de config con Pydantic        :p5, 2026-10-22, 2026-10-25
    Colisiones, vidas y niveles          :p6, 2026-10-24, 2026-10-28
 
    section Pantallas y datos
    Menu, pausa y HUD                    :p7, 2026-10-27, 2026-10-30
    Game Over, Victory y highscores      :p8, 2026-10-29, 2026-11-01
 
    section Extras
    Cheats y animaciones                 :p9, 2026-11-01, 2026-11-04
    IA de fantasmas por personalidad     :p10, 2026-11-02, 2026-11-05
 
    section Calidad
    Lint, mypy y Makefile                :p11, 2026-11-04, 2026-11-06
    Adaptacion a MLXAdapter              :crit, p12, 2026-11-05, 2026-11-08
 
    section Entrega
    Plan de pruebas y documentacion      :p13, 2026-11-08, 2026-11-11
    Entrega                              :milestone, pm, 2026-11-12, 0d
```
 
## 2. Progreso real (según git log)
 
```mermaid
gantt
    title Pac-Man - Progreso real (segun git log)
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    todayMarker on
 
    section Base
    Estructura y planificacion inicial   :done, b1, 2026-10-15, 1d
    Player y clase de movimiento         :done, b2, 2026-10-15, 2026-10-19
    Ghost y metodos de persecucion       :done, b3, 2026-10-19, 2026-10-20
 
    section Interfaz y entidades
    MazeUi, factory y EntitiesAdapter    :done, u1, 2026-10-20, 2026-10-21
    Movimiento de jugador y fantasmas    :done, u2, 2026-10-21, 2026-10-26
    Parser de config con Pydantic        :done, u3, 2026-10-21, 2026-10-23
    Colisiones, vidas y niveles          :done, u4, 2026-10-23, 2026-10-26
 
    section Pantallas y datos
    Menu, pausa y HUD                    :done, p1, 2026-10-26, 2026-10-27
    Game Over, Victory y highscores      :done, p2, 2026-10-27, 2026-10-29
    Gestion de errores                   :done, p3, 2026-10-28, 2026-10-29
 
    section Jugabilidad
    Cheats y animaciones                 :done, j1, 2026-10-29, 2026-11-02
    Fantasmas asustados y correcciones   :done, j2, 2026-10-27, 2026-11-04
    IA de fantasmas por personalidad     :done, j3, 2026-11-04, 2026-11-06
    Bugs de pulido y balance             :done, j4, 2026-11-02, 2026-11-05
 
    section Calidad
    Makefile, gitignore, flake8 y mypy   :done, q1, 2026-11-03, 2026-11-06
    Empaquetado itch.io                  :done, q2, 2026-11-06, 1d
    Docstrings                           :done, q3, 2026-11-10, 1d
    Makefile con uv                      :done, q4, 2026-11-10, 1d
 
    section Refactor y MLX
    Primer refactor de arquitectura      :done, r1, 2026-10-29, 2026-11-03
    Segundo refactor (Game, Renderer)    :done, r2, 2026-11-09, 2026-11-10
    Adaptacion a MLXAdapter              :done, crit, r3, 2026-11-06, 2026-11-10
    Validacion de config (defaults)      :done, r4, 2026-11-11, 1d
```
 
## 3. Plan frente a real
 
| Bloque | Plan | Real | Desviación |
|---|---|---|---|
| Base (Player y Ghost) | 17/10 - 22/10 | 15/10 - 20/10 | Se adelantó unos 2 días |
| Interfaz y config | 20/10 - 28/10 | 20/10 - 26/10 | Ligeramente adelantado |
| Pantallas y datos | 27/10 - 01/11 | 26/10 - 29/10 | Adelantado |
| Extras (cheats, IA) | 01/11 - 05/11 | 29/10 - 06/11 | Más largo: muchos bugs de pulido |
| Calidad (lint, mypy) | 04/11 - 06/11 | 03/11 - 06/11 | Según lo previsto |
| Adaptación a MLX | 05/11 - 08/11 (3 días) | 06/11 - 10/11 (4 días) | Se infravaloró: la mayor parte del trabajo estuvo en reemplazar funciones de pygame sin equivalente |
| Refactores de arquitectura | No planificados | 29/10 - 03/11 y 09/11 - 10/11 | Trabajo añadido, no previsto |
| Documentación y pruebas | 08/11 - 11/11 | 10/11 - 11/11 | Retrasado, se concentró al final |

# DIvision de responsabilidades en el proyecto

## Alejandro

- Desarrollo de base para Player y Ghost junto con EntityFactory
- Desarrollo de primeros algoritmos de busqueda y huida de fantasmas
- Parseo de entrada
- Añadidas logicas para matar pacman y crear iconos
- Añadidas pantalla de finalizacion junto con tabla de scores
- Refactorizacion de MazeRenderer para abstrar la carga de nivel y el movimiento

## Iker

- Desarrollo de una primera version de la interfaz haciendo uso de las funciones nativas de pygame
- Desarrollo de logicas de velocidad
- Añadidas logicas de reposicionamiento y refactorizacion de MovementEntity para evitar enviar funciones innecesarias entre funciones
- Desarrollo de algoritmos de movimiento concretos de cada uno de los fantasmas
- Refactorizacion de MazeRenderer para dividir responsabilidades entre mazeGrid y GameState

# Conflictos

Lo cierto es que no hemos tenido conflictos demasiado importantes. habiamos planteado bastante bien el proyecto y ha habido pocas cosas que nos romperian la logica completa

- Excesivas responsabilidades sobre la clase MazeRenderer, la cual en un momento del proyecto se ocupaba de todo lo necesario para renderizar
- Adaptacion de funciones de pygame para que fueran validas. Esto los mayores conflictos que ha dado eran de optimizacion, ya que, abusabamos mucho de renderizar cada cada muro en cada vuelta, generandolo de nuevo desde 0, lo cual lo resolvimos haciendo una superficie que ibamos renderizando