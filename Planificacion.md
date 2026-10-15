# Planificacion

## Maze-Generator

Viene dado por el ejercicio

## Parseo de entrada

## ConfiguracionInicial

### Atributos
- highscore_filename
- level array of multiple levels
- width , height for each level
- lives : 3
- pacgum : 42
- points_per_pacgum : 10
- points_per_super_pacgum : 50
- points_per_ghost : 200
- seed : 42
- level_max_time : 90

## Clase Jugador

### Atributos
- posicion x (int)
- posicion y (int)
- vidas (int)
- Posicion inicial (list[int, int])

### Funcionalidad

- Movimiento
- Cambios de estado
- reseteo
- Generar (establecer posicion y displayearse)

## Clase Fantasma

### Atributos
- posicion x (int)
- posicion y (int)
- Posicion inicial (list[int, int])
- vivos (bool)

### Funcionalidad

- Muerte
- Movimiento normal
- Movimiento con susto
- Generar (establecer posicion y displayearse)

## PacGums map

### Pacgums

#### Atributos
- tipo (ENUM)
- posicion x (int)
- posicion y (int)

### Atributos
- pacgums_number (int)
- PacGumsPosition (list[PacGums])

### Funcionalidad
- Aumentar score
- Desaparecer
- Generar

## Actual Map

### Atributos
- level (int)
- seconds_left (int)
- map (MazeGenerator Map)
- Super estado (bool)
- pausa (bool)
- finalizado (bool)
- puntuacion (int)

### Funcionalidad
- pasar de nivel (aumentar numero y regenerar mapa):
    - resetear tiempo
    - aumentar numero de nivel
    - regenerar mapa
    - Reposicionar todo
    - resetear Super estado
- establecer pausa
- finalizar partida:
    - Guardar score
    - Devolver al inicio


## Fases

### Parseo

### Funcionalidad de jugador

### Funcionalidad de fantasmas

### Funcionalidad de PacGums map

### Interfaz

### Habilitacion de mapa

### ScoreBoard