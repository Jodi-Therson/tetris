from settings import *
import math
from tetromino import Tetromino
import pygame.freetype as ft
import os

from utils import resource_path

class Text:
    def __init__(self, app):
        self.app = app
        
        font_path = resource_path(FONT_PATH)
        self.font = ft.Font(font_path)

    def draw(self):
        if self.app.tetris.game_over:
            overlay = pg.Surface((WIN_W, WIN_H))
            overlay.set_alpha(128)
            overlay.fill((255,255,255))
            self.app.screen.blit(overlay, (0, 0))

            font = self.font
            screen = self.app.screen

            def draw_centered(text, y_ratio, color, size):
                surf, _ = font.render(text, fgcolor=color, size=size)
                rect = surf.get_rect(center=(WIN_W // 2, int(WIN_H * y_ratio)))
                screen.blit(surf, rect)

            draw_centered('GAME OVER', 0.3, 'red', TILE_SIZE * 1.8)
            draw_centered(f'SCORE: {self.app.tetris.score}', 0.45, 'black', TILE_SIZE * 1.5)
            draw_centered(f'HIGH SCORE: {self.app.tetris.high_score}', 0.55, 'darkorange', TILE_SIZE * 1.5)

            if pg.time.get_ticks() - self.app.tetris.game_over_time >= 500:
                draw_centered('Press R to Restart', 0.7, 'black', TILE_SIZE * 1.2)
        
        else:
            self.font.render_to(self.app.screen, (WIN_W * 0.595, WIN_H * 0.02), text='TETRIS', fgcolor='white', size=TILE_SIZE * 1.65, bgcolor='black')
            self.font.render_to(self.app.screen, (WIN_W * 0.65, WIN_H * 0.22), text='next', fgcolor='orange', size=TILE_SIZE * 1.4, bgcolor='black')
            self.font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.67), text='score', fgcolor='orange', size=TILE_SIZE * 1.4, bgcolor='black')
            self.font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.8), text=f'{self.app.tetris.score}', fgcolor='white', size=TILE_SIZE * 1.8)

class Tetris:
    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as file:
                return int(file.read())
        except:
            return 0

    def save_high_score(self):
        with open("high_score.txt", "w") as file:
            file.write(str(self.high_score))

    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.speed_up = False

        self.score = 0
        self.full_lines = 0
        self.points_per_lines = {0: 0, 1: 100, 2: 250, 3:500, 4:1000}
        self.high_score = self.load_high_score()
        self.game_over = False
        self.game_over_time = 0

    def get_score(self):
        self.score += self.points_per_lines[self.full_lines]
        self.full_lines = 0

    def check_full_lines(self):
        row = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1):
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x]

                if self.field_array[y][x]:
                    self.field_array[row][x].pos = vec(x, y)

            if sum(map(bool, self.field_array[y])) < FIELD_W:
                row -= 1
            else: 
                for x in range(FIELD_W):
                    self.field_array[row][x].alive = False
                    self.field_array[row][x] = 0

                self.full_lines += 1

    def put_tetromino_blocks_in_array(self):
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            self.field_array[y][x] = block

    def get_field_array(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def is_game_over(self):
        if self.tetromino.blocks[0].pos.y == INIT_POS_OFFSET[1]:
            self.game_over = True
            self.game_over_time = pg.time.get_ticks()
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return True
        return False

    def check_tetromino_landing(self):
        if self.tetromino.landing:
            if self.is_game_over():
                self.game_over = True
                self.game_over_time = pg.time.get_ticks()
            else:
                self.speed_up = False
                self.put_tetromino_blocks_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)

    def control(self, pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction='right')
        elif pressed_key == pg.K_UP:
            self.tetromino.rotate()
        elif pressed_key == pg.K_DOWN:
            self.speed_up = True
        elif pressed_key == pg.K_SPACE:
            self.tetromino.hard_drop()

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black', (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def update(self):
        if self.game_over:
            return
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]
        if trigger:
            self.check_full_lines()
            self.tetromino.update()
            self.check_tetromino_landing()
            self.get_score()
        self.sprite_group.update()

    def draw(self):
        self.draw_grid()
        self.tetromino.draw_ghost()
        self.sprite_group.draw(self.app.screen)

    def reset(self):
        self.__init__(self.app)