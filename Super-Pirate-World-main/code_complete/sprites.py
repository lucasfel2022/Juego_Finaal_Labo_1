import pygame
from settings import *
from math import sin, cos, radians
from random import randint

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf=pygame.Surface((TILE_SIZE, TILE_SIZE)), groups=None, z=Z_LAYERS['main']):
        """
        Clase base para todos los sprites del juego.
        
        :param pos: Posición inicial del sprite (x, y).
        :param surf: Superficie de imagen para el sprite (por defecto un cuadrado del tamaño TILE_SIZE).
        :param groups: Grupos a los que el sprite pertenece (por defecto None).
        :param z: Capa Z del sprite (por defecto Z_LAYERS['main']).
        """
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = z

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups, z=Z_LAYERS['main'], animation_speed=ANIMATION_SPEED):
        """
        Sprite animado basado en una secuencia de imágenes.

        :param pos: Posición inicial del sprite (x, y).
        :param frames: Lista de superficies de imagen para la animación.
        :param groups: Grupos a los que el sprite pertenece.
        :param z: Capa Z del sprite.
        :param animation_speed: Velocidad de la animación.
        """
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, dt):
        """
        Actualiza la imagen del sprite para la animación basada en el delta tiempo.
        
        :param dt: Delta tiempo (tiempo transcurrido desde la última actualización).
        """
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        """
        Actualiza el sprite animado.
        
        :param dt: Delta tiempo.
        """
        self.animate(dt)

class Item(AnimatedSprite):
    def __init__(self, item_type, pos, frames, groups, data):
        """
        Sprite para los ítems recolectables en el juego.

        :param item_type: Tipo de ítem (ej. 'gold', 'silver').
        :param pos: Posición inicial del sprite (x, y).
        :param frames: Lista de superficies de imagen para la animación.
        :param groups: Grupos a los que el sprite pertenece.
        :param data: Datos del juego (para modificar el estado del juego).
        """
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.item_type = item_type
        self.data = data

    def activate(self):
        """
        Activa el ítem, modificando el estado del juego basado en el tipo de ítem.
        """
        if self.item_type == 'gold':
            self.data.coins += 5
        if self.item_type == 'silver':
            self.data.coins += 1
        if self.item_type == 'diamond':
            self.data.coins += 20
        if self.item_type == 'skull':
            self.data.coins += 50
        if self.item_type == 'potion':
            self.data.health += 1

class ParticleEffectSprite(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        """
        Sprite para efectos de partículas (animaciones cortas que se eliminan al finalizar).

        :param pos: Posición inicial del sprite (x, y).
        :param frames: Lista de superficies de imagen para la animación.
        :param groups: Grupos a los que el sprite pertenece.
        """
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.z = Z_LAYERS['fg']

    def animate(self, dt):
        """
        Actualiza la imagen del sprite para la animación y elimina el sprite al finalizar.
        
        :param dt: Delta tiempo.
        """
        self.frame_index += self.animation_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class MovingSprite(AnimatedSprite):
    def __init__(self, frames, groups, start_pos, end_pos, move_dir, speed, flip=False):
        """
        Sprite que se mueve en una trayectoria definida.

        :param frames: Lista de superficies de imagen para la animación.
        :param groups: Grupos a los que el sprite pertenece.
        :param start_pos: Posición inicial del sprite (x, y).
        :param end_pos: Posición final del sprite (x, y).
        :param move_dir: Dirección del movimiento ('x' o 'y').
        :param speed: Velocidad de movimiento.
        :param flip: Si el sprite debe voltear su imagen.
        """
        super().__init__(start_pos, frames, groups)
        if move_dir == 'x':
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos

        self.start_pos = start_pos
        self.end_pos = end_pos

        # Movimiento
        self.moving = True
        self.speed = speed
        self.direction = pygame.math.Vector2(1, 0) if move_dir == 'x' else pygame.math.Vector2(0, 1)
        self.move_dir = move_dir

        self.flip = flip
        self.reverse = {'x': False, 'y': False}

    def check_border(self):
        """
        Verifica y ajusta la posición del sprite al alcanzar los bordes del trayecto.
        """
        if self.move_dir == 'x':
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            self.reverse['x'] = True if self.direction.x < 0 else False
        else:
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            self.reverse['y'] = True if self.direction.y > 0 else False

    def update(self, dt):
        """
        Actualiza la posición del sprite y realiza la animación.
        
        :param dt: Delta tiempo.
        """
        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * dt
        self.check_border()

        self.animate(dt)
        if self.flip:
            self.image = pygame.transform.flip(self.image, self.reverse['x'], self.reverse['y'])

class Spike(Sprite):
    def __init__(self, pos, surf, groups, radius, speed, start_angle, end_angle, z=Z_LAYERS['main']):
        """
        Sprite para los obstáculos tipo espiga que se mueven en un círculo.

        :param pos: Posición central del sprite (x, y).
        :param surf: Superficie de imagen para el sprite.
        :param groups: Grupos a los que el sprite pertenece.
        :param radius: Radio del movimiento circular.
        :param speed: Velocidad de rotación.
        :param start_angle: Ángulo inicial de rotación.
        :param end_angle: Ángulo final de rotación.
        :param z: Capa Z del sprite.
        """
        self.center = pos
        self.radius = radius
        self.speed = speed
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.angle = self.start_angle
        self.direction = 1
        self.full_circle = True if self.end_angle == -1 else False

        # Trigonometría para la posición inicial
        y = self.center[1] + sin(radians(self.angle)) * self.radius
        x = self.center[0] + cos(radians(self.angle)) * self.radius

        super().__init__((x, y), surf, groups, z)

    def update(self, dt):
        """
        Actualiza la posición del sprite en el movimiento circular.
        
        :param dt: Delta tiempo.
        """
        self.angle += self.direction * self.speed * dt

        if not self.full_circle:
            if self.angle >= self.end_angle:
                self.direction = -1
            if self.angle < self.start_angle:
                self.direction = 1

        y = self.center[1] + sin(radians(self.angle)) * self.radius
        x = self.center[0] + cos(radians(self.angle)) * self.radius
        self.rect.center = (x, y)

class Cloud(Sprite):
    def __init__(self, pos, surf, groups, z=Z_LAYERS['clouds']):
        """
        Sprite para las nubes en movimiento.

        :param pos: Posición inicial del sprite (x, y).
        :param surf: Superficie de imagen para el sprite.
        :param groups: Grupos a los que el sprite pertenece.
        :param z: Capa Z del sprite.
        """
        super().__init__(pos, surf, groups, z)
        self.speed = randint(50, 120)
        self.direction = -1
        self.rect.midbottom = pos

    def update(self, dt):
        """
        Actualiza la posición de la nube y elimina el sprite si sale de la pantalla.
        
        :param dt: Delta tiempo.
        """
        self.rect.x += self.direction * self.speed * dt

        if self.rect.right <= 0:
            self.kill()

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, level, data, paths):
        """
        Nodo en la ruta del juego para la navegación.

        :param pos: Posición del nodo (x, y).
        :param surf: Superficie de imagen para el nodo.
        :param groups: Grupos a los que el nodo pertenece.
        :param level: Nivel al que pertenece el nodo.
        :param data: Datos del juego.
        :param paths: Diccionario de rutas accesibles desde el nodo.
        """
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center=(pos[0] + TILE_SIZE / 2, pos[1] + TILE_SIZE / 2))
        self.z = Z_LAYERS['path']
        self.level = level
        self.data = data
        self.paths = paths
        self.grid_pos = (int(pos[0] / TILE_SIZE), int(pos[1] / TILE_SIZE))

    def can_move(self, direction):
        """
        Verifica si se puede mover en la dirección dada.

        :param direction: Dirección en la que se desea mover.
        :return: True si el movimiento es posible, False en caso contrario.
        """
        if direction in list(self.paths.keys()) and int(self.paths[direction][0][0]) <= self.data.unlocked_level:
            return True

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos, groups, frames):
        """
        Sprite para un icono en movimiento a lo largo de un camino.

        :param pos: Posición inicial del sprite (x, y).
        :param groups: Grupos a los que el sprite pertenece.
        :param frames: Diccionario de listas de imágenes para diferentes estados.
        """
        super().__init__(groups)
        self.icon = True
        self.path = None
        self.direction = pygame.math.Vector2()
        self.speed = 400

        # Imagen y rectángulo inicial
        self.frames, self.frame_index = frames, 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.z = Z_LAYERS['main']

        self.rect = self.image.get_rect(center=pos)

    def start_move(self, path):
        """
        Inicia el movimiento del icono a lo largo del camino especificado.

        :param path: Lista de puntos que forman el camino.
        """
        self.rect.center = path[0]
        self.path = path[1:]
        self.find_path()

    def find_path(self):
        """
        Determina la dirección del movimiento del icono basado en el camino.
        """
        if self.path:
            if self.rect.centerx == self.path[0][0]:  # Movimiento vertical
                self.direction = pygame.math.Vector2(0, 1 if self.path[0][1] > self.rect.centery else -1)
            else:  # Movimiento horizontal
                self.direction = pygame.math.Vector2(1 if self.path[0][0] > self.rect.centerx else -1, 0)
        else:
            self.direction = pygame.math.Vector2()

    def point_collision(self):
        """
        Maneja la colisión con puntos en el camino y actualiza la dirección.
        """
        if self.direction.y == 1 and self.rect.centery >= self.path[0][1] or \
           self.direction.y == -1 and self.rect.centery <= self.path[0][1]:
            self.rect.centery = self.path[0][1]
            del self.path[0]
            self.find_path()

        if self.direction.x == 1 and self.rect.centerx >= self.path[0][0] or \
           self.direction.x == -1 and self.rect.centerx <= self.path[0][0]:
            self.rect.centerx = self.path[0][0]
            del self.path[0]
            self.find_path()

    def animate(self, dt):
        """
        Actualiza la imagen del sprite para la animación basada en el delta tiempo.
        
        :param dt: Delta tiempo.
        """
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]

    def get_state(self):
        """
        Determina el estado del icono basado en su dirección.
        """
        self.state = 'idle'
        if self.direction == pygame.math.Vector2(1, 0):
            self.state = 'right'
        if self.direction == pygame.math.Vector2(-1, 0):
            self.state = 'left'
        if self.direction == pygame.math.Vector2(0, 1):
            self.state = 'down'
        if self.direction == pygame.math.Vector2(0, -1):
            self.state = 'up'

    def update(self, dt):
        """
        Actualiza el estado y posición del icono.
        
        :param dt: Delta tiempo.
        """
        if self.path:
            self.point_collision()
            self.rect.center += self.direction * self.speed * dt
        self.get_state()
        self.animate(dt)

class PathSprite(Sprite):
    def __init__(self, pos, surf, groups, level):
        """
        Sprite para representar caminos en el juego.

        :param pos: Posición inicial del sprite (x, y).
        :param surf: Superficie de imagen para el sprite.
        :param groups: Grupos a los que el sprite pertenece.
        :param level: Nivel al que pertenece el camino.
        """
        super().__init__(pos, surf, groups, Z_LAYERS['path'])
        self.level = level
