from settings import * 
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join, dirname, normpath
from support import * 
from data import Data
from debug import debug
from ui import UI
from overworld import Overworld
import os
import sys

print("Directorio de trabajo actual:", os.getcwd())

# Define el directorio base a partir de la ubicación del archivo actual
BASE_PATH = normpath(join(dirname(__file__), '..'))

class Game:
    def __init__(self):
        # Inicializa Pygame y configura la pantalla del juego
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Aventuras de Un Pirata')
        self.clock = pygame.time.Clock()
        self.import_assets()

        # Inicializa la interfaz de usuario y los datos del juego
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        
        # Carga los mapas de niveles
        self.tmx_maps = {
            0: load_pygame(join(BASE_PATH, 'data', 'levels', 'omni.tmx')),
            1: load_pygame(join(BASE_PATH, 'data', 'levels', '1.tmx')),
            2: load_pygame(join(BASE_PATH, 'data', 'levels', '2.tmx')),
            3: load_pygame(join(BASE_PATH, 'data', 'levels', '3.tmx')),
            4: load_pygame(join(BASE_PATH, 'data', 'levels', '4.tmx')),
            5: load_pygame(join(BASE_PATH, 'data', 'levels', '5.tmx')),
        }
        # Carga el mapa del overworld
        self.tmx_overworld = load_pygame(join(BASE_PATH, 'data', 'overworld', 'overworld.tmx'))
        # Establece el estado actual del juego como Overworld
        self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)
        self.bg_music.play(-1)  # Reproduce la música de fondo en bucle

        self.paused = False  # Estado de pausa del juego
        self.selected_option = 0  # Opción seleccionada en el menú de pausa

    def switch_stage(self, target, unlock=0):
        # Cambia la etapa actual del juego
        print(f"Switching stage to: {target}")  # Para depuración
        if target == 'level':
            # Cambia a un nivel específico
            self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files, self.data, self.switch_stage)
        elif target == 'overworld':
            # Cambia al overworld y maneja el desbloqueo de niveles
            if unlock > 0:
                self.data.unlocked_level = 6
            else:
                self.data.health -= 1
            self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)

    def import_assets(self):
        # Carga todos los activos necesarios para el juego (imágenes, sonidos, etc.)
        self.level_frames = {
            'flag': import_folder(BASE_PATH, 'graphics', 'level', 'flag'),
            'saw': import_folder(BASE_PATH, 'graphics', 'enemies', 'saw', 'animation'),
            'floor_spike': import_folder(BASE_PATH, 'graphics', 'enemies', 'floor_spikes'),
            'palms': import_sub_folders(BASE_PATH, 'graphics', 'level', 'palms'),
            'candle': import_folder(BASE_PATH, 'graphics', 'level', 'candle'),
            'window': import_folder(BASE_PATH, 'graphics', 'level', 'window'),
            'big_chain': import_folder(BASE_PATH, 'graphics', 'level', 'big_chains'),
            'small_chain': import_folder(BASE_PATH, 'graphics', 'level', 'small_chains'),
            'candle_light': import_folder(BASE_PATH, 'graphics', 'level', 'candle light'),
            'player': import_sub_folders(BASE_PATH, 'graphics', 'player'),
            'saw_chain': import_image(BASE_PATH, 'graphics', 'enemies', 'saw', 'saw_chain'),
            'helicopter': import_folder(BASE_PATH, 'graphics', 'level', 'helicopter'),
            'boat': import_folder(BASE_PATH, 'graphics', 'objects', 'boat'),
            'spike': import_image(BASE_PATH, 'graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
            'spike_chain': import_image(BASE_PATH, 'graphics', 'enemies', 'spike_ball', 'spiked_chain'),
            'tooth': import_folder(BASE_PATH, 'graphics', 'enemies', 'tooth', 'run'),
            'shell': import_sub_folders(BASE_PATH, 'graphics', 'enemies', 'shell'),
            'pearl': import_image(BASE_PATH, 'graphics', 'enemies', 'bullets', 'pearl'),
            'items': import_sub_folders(BASE_PATH, 'graphics', 'items'),
            'particle': import_folder(BASE_PATH, 'graphics', 'effects', 'particle'),
            'water_top': import_folder(BASE_PATH, 'graphics', 'level', 'water', 'top'),
            'water_body': import_image(BASE_PATH, 'graphics', 'level', 'water', 'body'),
            'bg_tiles': import_folder_dict(BASE_PATH, 'graphics', 'level', 'bg', 'tiles'),
            'cloud_small': import_folder(BASE_PATH, 'graphics', 'level', 'clouds', 'small'),
            'cloud_large': import_image(BASE_PATH, 'graphics', 'level', 'clouds', 'large_cloud'),
        }
        self.font = pygame.font.Font(join(BASE_PATH, 'graphics', 'ui', 'runescape_uf.ttf'), 40)
        self.ui_frames = {
            'heart': import_folder(BASE_PATH, 'graphics', 'ui', 'heart'),
            'coin': import_image(BASE_PATH, 'graphics', 'ui', 'coin')
        }
        self.overworld_frames = {
            'palms': import_folder(BASE_PATH, 'graphics', 'overworld', 'palm'),
            'water': import_folder(BASE_PATH, 'graphics', 'overworld', 'water'),
            'path': import_folder_dict(BASE_PATH, 'graphics', 'overworld', 'path'),
            'icon': import_sub_folders(BASE_PATH, 'graphics', 'overworld', 'icon'),
        }

        self.audio_files = {
            'coin': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'coin.wav')),
            'attack': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'attack.wav')),
            'jump': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'jump.wav')),
            'damage': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'damage.wav')),
            'pearl': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'pearl.wav')),
        }
        self.bg_music = pygame.mixer.Sound(join(BASE_PATH, 'audio', 'starlight_city.mp3'))
        self.bg_music.set_volume(0.5)  # Ajusta el volumen de la música de fondo

    def check_game_over(self):
        # Verifica si la salud del jugador es menor o igual a cero
        if self.data.health <= 0:
            self.display_game_over()  # Muestra la pantalla de "Game Over"
            pygame.time.wait(3000)  # Espera 3 segundos para mostrar el mensaje
            pygame.quit()
            sys.exit()

    def display_game_over(self):
        # Muestra la pantalla de "Game Over"
        self.display_surface.fill((0, 0, 0))  # Rellena la pantalla con negro
        game_over_text = self.font.render("Game Over", True, (255, 0, 0))  # Texto rojo
        # Centra el texto en la pantalla
        self.display_surface.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - game_over_text.get_height() // 2))
        pygame.display.update()

    def run(self):
        # Bucle principal del juego
        while True:
            dt = self.clock.tick() / 1000  # Calcula el delta tiempo
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused  # Alternar el estado de pausa
                    if self.paused:
                        if event.key == pygame.K_UP:
                            self.selected_option = (self.selected_option - 1) % 3
                        if event.key == pygame.K_DOWN:
                            self.selected_option = (self.selected_option + 1) % 3
                        if event.key == pygame.K_RETURN:
                            self.handle_pause_menu_selection()

            self.check_game_over()

            if self.paused:
                self.display_pause_menu()
            else:
                self.current_stage.run(dt)  # Ejecuta la etapa actual del juego
                self.ui.update(dt)  # Actualiza la interfaz de usuario

            pygame.display.update()

    def display_pause_menu(self):
        # Muestra el menú de pausa
        options = ["Continuar", "Reiniciar nivel", "Niveles"]
        pause_text = self.font.render("Pausa", True, (255, 255, 255))
        # Centra el texto de pausa en la pantalla
        self.display_surface.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, WINDOW_HEIGHT // 2 - 100))

        for index, option in enumerate(options):
            # Cambia el color de la opción seleccionada
            color = (255, 255, 255) if index == self.selected_option else (150, 150, 150)
            option_text = self.font.render(option, True, color)
            # Dibuja el texto de la opción en la pantalla
            self.display_surface.blit(option_text, (WINDOW_WIDTH // 2 - option_text.get_width() // 2, WINDOW_HEIGHT // 2 + index * 40))

    def handle_pause_menu_selection(self):
        # Maneja la selección de opciones del menú de pausa
        if self.selected_option == 0:
            self.paused = False
        elif self.selected_option == 1:
            self.restart_level()
        elif self.selected_option == 2:
            self.exit_to_levels()  

    def restart_level(self):
        # Reinicia el nivel actual
        self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files, self.data, self.switch_stage)
        self.paused = False

    def exit_to_levels(self):
        # Cambia al overworld
        self.switch_stage('overworld')  
        self.paused = False

if __name__ == '__main__':
    # Ejecuta el juego
    game = Game()
    game.run()
