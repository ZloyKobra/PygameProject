import pygame
from pygame.locals import *
import time
import math
import random
import requests
import io
from urllib.request import urlopen

pygame.init()

game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption('Pokemon Battle')

black = (0, 0, 0)
gold = (218, 165, 32)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)

base_url = 'https://pokeapi.co/api/v2'

count_restart = 0

class Move():

    def __init__(self, url):
        req = requests.get(url)
        self.json = req.json()

        self.name = self.json['name']
        self.power = self.json['power']
        self.type = self.json['type']['name']


class Pokemon(pygame.sprite.Sprite):

    def __init__(self, name, level, x, y):

        pygame.sprite.Sprite.__init__(self)

        req = requests.get(f'{base_url}/pokemon/{name.lower()}')
        self.json = req.json()

        self.name = name
        self.level = level

        self.hp_x = 275
        self.hp_y = 250
        self.hp_x = 50
        self.hp_y = 50

        self.x = x
        self.y = y

        self.num_potions = 3

        stats = self.json['stats']
        for stat in stats:
            if stat['stat']['name'] == 'hp':
                self.current_hp = stat['base_stat'] + self.level
                self.max_hp = stat['base_stat'] + self.level
            elif stat['stat']['name'] == 'attack':
                self.attack = stat['base_stat']
            elif stat['stat']['name'] == 'defense':
                self.defense = stat['base_stat']
            elif stat['stat']['name'] == 'speed':
                self.speed = stat['base_stat']

        self.types = []
        for i in range(len(self.json['types'])):
            type = self.json['types'][i]
            self.types.append(type['type']['name'])

        self.size = 150

        self.set_sprite('front_default')

    def perform_attack(self, other, move):

        display_message(f'{self.name} использовал {move.name}')

        time.sleep(2)

        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power

        if move.type in self.types:
            damage *= 1.5

        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5

        damage = math.floor(damage)

        other.take_damage(damage)

    def take_damage(self, damage):

        self.current_hp -= damage

        if self.current_hp < 0:
            self.current_hp = 0

    def use_potion(self):

        if self.num_potions > 0:

            self.current_hp += 30
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp

            self.num_potions -= 1

    def set_sprite(self, side):

        image = self.json['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()

        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

    def set_moves(self):

        self.moves = []

        for i in range(len(self.json['moves'])):

            versions = self.json['moves'][i]['version_group_details']
            for j in range(len(versions)):

                version = versions[j]

                if version['version_group']['name'] != 'red-blue':
                    continue

                learn_method = version['move_learn_method']['name']
                if learn_method != 'level-up':
                    continue

                level_learned = version['level_learned_at']
                if self.level >= level_learned:
                    move = Move(self.json['moves'][i]['move']['url'])

                    if move.power is not None:
                        self.moves.append(move)

        if len(self.moves) > 4:
            self.moves = random.sample(self.moves, 4)

    def draw(self, alpha=255):

        sprite = self.image.copy()
        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))

    def draw_hp(self):

        bar_scale = 200 // self.max_hp
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, red, bar)

        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, green, bar)

        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(f'HP: {self.current_hp} / {self.max_hp}', True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y + 30
        game.blit(text, text_rect)

    def get_rect(self):

        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


def display_message(message):
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)

    pygame.display.update()


def create_button(width, height, left, top, text_cx, text_cy, label):
    mouse_cursor = pygame.mouse.get_pos()

    button = Rect(left, top, width, height)

    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)

    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)

    return button


level = 30
bulbasaur = Pokemon('Bulbasaur', level, 25, 175)
charmander = Pokemon('Charmander', level, 175, 175)
squirtle = Pokemon('Squirtle', level, 325, 175)
pikachu = Pokemon("Pikachu", level, 25, 25)
jigglypuff = Pokemon('Jigglypuff', level, 175, 25)
haunter = Pokemon('Haunter', level, 325, 25)
magikarp = Pokemon('Magikarp', level, 25, 325)
rattata = Pokemon('Rattata', level, 175, 325)
pidgey = Pokemon("Pidgey", level, 325, 325)

pokemons = [bulbasaur, charmander, squirtle, pikachu, jigglypuff, haunter, magikarp, rattata, pidgey]

player_pokemon = None
rival_pokemon = None

game_status = 'select pokemon'
while game_status != 'quit':
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit'

        if event.type == KEYDOWN:

            if event.key == K_y:
                count_restart += 1
                level += 25
                bulbasaur = Pokemon('Bulbasaur', level, 25, 175)
                charmander = Pokemon('Charmander', level, 175, 175)
                squirtle = Pokemon('Squirtle', level, 325, 175)
                pikachu = Pokemon("Pikachu", level, 25, 25)
                jigglypuff = Pokemon('Jigglypuff', level, 175, 25)
                haunter = Pokemon('Haunter', level, 325, 25)
                magikarp = Pokemon('Magikarp', level, 25, 325)
                rattata = Pokemon('Rattata', level, 175, 325)
                pidgey = Pokemon("Pidgey", level, 325, 325)
                pokemons = [bulbasaur, charmander, squirtle, pikachu, jigglypuff, haunter, magikarp, rattata, pidgey]
                game_status = 'select pokemon'

            elif event.key == K_n:
                game_status = 'quit'

        if event.type == MOUSEBUTTONDOWN:

            mouse_click = event.pos

            if game_status == 'select pokemon':

                for i in range(len(pokemons)):

                    if pokemons[i].get_rect().collidepoint(mouse_click):
                        player_pokemon = pokemons[i]
                        rival_pokemon = pokemons[(i + random.randint(1, 8)) % len(pokemons)]

                        rival_pokemon.level = int(rival_pokemon.level * .75)
                        player_pokemon.level -= 1 * count_restart

                        player_pokemon.hp_x = 275
                        player_pokemon.hp_y = 250
                        rival_pokemon.hp_x = 50
                        rival_pokemon.hp_y = 50

                        game_status = 'prebattle'

            elif game_status == 'player turn':

                game.fill(white)
                player_pokemon.draw()
                rival_pokemon.draw()
                player_pokemon.draw_hp()
                rival_pokemon.draw_hp()

                fight_button = create_button(240, 140, 10, 350, 130, 412, 'Fight')
                potion_button = create_button(240, 140, 250, 350, 370, 412,
                                              f'Использовал зелье ({player_pokemon.num_potions})')

                pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
                pygame.display.update()

                if fight_button.collidepoint(mouse_click):
                    game_status = 'player move'

                if potion_button.collidepoint(mouse_click):

                    if player_pokemon.num_potions == 0:
                        display_message('Не осталось зельей здоровья')
                        time.sleep(2)
                        game_status = 'player move'
                    else:
                        player_pokemon.use_potion()
                        display_message(f'{player_pokemon.name} использовал зелье')
                        time.sleep(2)
                        game_status = 'rival turn'

            elif game_status == 'player move':

                game.fill(white)
                player_pokemon.draw()
                rival_pokemon.draw()
                player_pokemon.draw_hp()
                rival_pokemon.draw_hp()

                move_buttons = []
                for i in range(len(player_pokemon.moves)):
                    move = player_pokemon.moves[i]
                    button_width = 240
                    button_height = 70
                    left = 10 + i % 2 * button_width
                    top = 350 + i // 2 * button_height
                    text_center_x = left + 120
                    text_center_y = top + 35
                    button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                           move.name.capitalize())
                    move_buttons.append(button)
                pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
                pygame.display.update()


                for i in range(len(move_buttons)):
                    button = move_buttons[i]

                    if button.collidepoint(mouse_click):
                        move = player_pokemon.moves[i]
                        player_pokemon.perform_attack(rival_pokemon, move)

                        if rival_pokemon.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'rival turn'

    if game_status == 'select pokemon':

        game.fill(white)

        for pokemon in pokemons:
            pokemon.draw()

        mouse_cursor = pygame.mouse.get_pos()
        for pokemon in pokemons:

            if pokemon.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, black, pokemon.get_rect(), 2)

        pygame.display.update()

    if game_status == 'prebattle':
        game.fill(white)
        player_pokemon.draw()
        pygame.display.update()

        player_pokemon.set_moves()
        rival_pokemon.set_moves()

        player_pokemon.x = -50
        player_pokemon.y = 100
        rival_pokemon.x = 250
        rival_pokemon.y = -50

        player_pokemon.size = 300
        rival_pokemon.size = 300
        player_pokemon.set_sprite('back_default')
        rival_pokemon.set_sprite('front_default')

        game_status = 'start battle'

    if game_status == 'start battle':

        alpha = 0
        while alpha < 255:
            game.fill(white)
            rival_pokemon.draw(alpha)
            display_message(f'На вас напал {rival_pokemon.name}!')
            alpha += .4

            pygame.display.update()

        alpha = 0
        while alpha < 255:
            game.fill(white)
            rival_pokemon.draw()
            player_pokemon.draw(alpha)
            display_message(f'Вперёд {player_pokemon.name}!')
            alpha += .4

            pygame.display.update()

        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        if rival_pokemon.speed > player_pokemon.speed:
            game_status = 'rival turn'
        else:
            game_status = 'player turn'

        pygame.display.update()


    if game_status == 'player turn':
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        fight_button = create_button(240, 140, 10, 350, 130, 412, 'Fight')
        potion_button = create_button(240, 140, 250, 350, 370, 412,
                                      f'Использовать зелье ({player_pokemon.num_potions})')
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

        pygame.display.update()

    if game_status == 'player move':

        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        move_buttons = []
        for i in range(len(player_pokemon.moves)):
            move = player_pokemon.moves[i]
            button_width = 240
            button_height = 70
            left = 10 + i % 2 * button_width
            top = 350 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                   move.name.capitalize())
            move_buttons.append(button)

        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

        pygame.display.update()

    if game_status == 'rival turn':

        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        display_message('')
        move = random.choice(rival_pokemon.moves)
        time.sleep(2)
        rival_pokemon.perform_attack(player_pokemon, move)

        if player_pokemon.current_hp == 0:
            game_status = 'fainted'
        else:
            game_status = 'player turn'

        pygame.display.update()

    if game_status == 'fainted':

        alpha = 255
        while alpha > 0:

            game.fill(white)
            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()

            if rival_pokemon.current_hp == 0:
                player_pokemon.draw()
                rival_pokemon.draw(alpha)
                display_message(f'{rival_pokemon.name} уничтожен!')
            else:
                player_pokemon.draw(alpha)
                rival_pokemon.draw()
                count_restart = 0
                display_message(f'{player_pokemon.name} унижен!')
            alpha -= .4

            pygame.display.update()

        game_status = 'gameover'

    if game_status == 'gameover':
        display_message('Сыграть ещё раз(Y/N)?')

pygame.quit()
