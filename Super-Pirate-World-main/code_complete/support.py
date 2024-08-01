import os
import pygame
from os import walk
from os.path import join, abspath, dirname, normpath

# Define el directorio base a partir de la ubicación del archivo actual
BASE_PATH = dirname(dirname(abspath(__file__)))  # Dos niveles arriba para alcanzar 'Super-Pirate-World-main'

def import_image(*path, alpha=True, format='png'):
    full_path = normpath(join(BASE_PATH, *path)) + f'.{format}'
    try:
        return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
    except FileNotFoundError:
        print(f"Error: El archivo '{full_path}' no se encontró.")
        return None
    except pygame.error as e:
        print(f"Error al cargar la imagen '{full_path}': {e}")
        return None

def import_folder(*path):
    frames = []
    for folder_path, subfolders, image_names in walk(normpath(join(BASE_PATH, *path))):
        for image_name in sorted(image_names, key=lambda name: int(name.split('.')[0])):
            full_path = normpath(join(folder_path, image_name))
            frames.append(pygame.image.load(full_path).convert_alpha())
    return frames

def import_folder_dict(*path):
    frame_dict = {}
    for folder_path, _, image_names in walk(normpath(join(BASE_PATH, *path))):
        for image_name in image_names:
            full_path = normpath(join(folder_path, image_name))
            surface = pygame.image.load(full_path).convert_alpha()
            frame_dict[image_name.split('.')[0]] = surface
    return frame_dict

def import_sub_folders(*path):
    frame_dict = {}
    for _, sub_folders, __ in walk(normpath(join(BASE_PATH, *path))): 
        if sub_folders:
            for sub_folder in sub_folders:
                full_path = normpath(join(BASE_PATH, *path, sub_folder))
                frame_dict[sub_folder] = import_folder(full_path)
    return frame_dict

# Asegúrate de que 'join(BASE_PATH, ...)' esté en todas las llamadas a pygame.font.Font y pygame.mixer.Sound en tu archivo main.py

# En tu archivo main.py
class Game:
    def __init__(self):
        self.import_assets()
        # Otras inicializaciones

    def import_assets(self):
        self.images = {
            'saw_chain': import_image('graphics', 'enemies', 'saw', 'saw_chain'),
            'spike_ball': import_image('graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
            'spiked_chain': import_image('graphics', 'enemies', 'spike_ball', 'spiked_chain'),
            'pearl': import_image('graphics', 'enemies', 'bullets', 'pearl'),
            'water_body': import_image('graphics', 'level', 'water', 'body'),
            'large_cloud': import_image('graphics', 'level', 'clouds', 'large_cloud'),
            'coin': import_image('graphics', 'ui', 'coin')
        }

        self.sounds = {
            'coin': pygame.mixer.Sound(normpath(join(BASE_PATH, 'audio', 'coin.wav')))
        }

        self.font = pygame.font.Font(normpath(join(BASE_PATH, 'graphics', 'ui', 'runescape_uf.ttf')), 40)
