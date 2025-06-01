from settings import *
from tetris import Tetris, Text
import sys, os
import pathlib

from utils import resource_path

class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('HomeMade Tetris')
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.set_timer()
        self.images = self.load_images()
        self.tetris = Tetris(self)
        self.text = Text(self)

        self.left_pressed = False
        self.right_pressed = False
        self.move_delay = 150
        self.move_interval = 50
        self.last_move_time = 0
        self.initial_hold = True

        self.is_paused = False
        self.forfeit_prompt = False

    def load_images(self):
        images = []
        sprite_path = resource_path(SPRITE_DIR_PATH)

        # Ensure we use absolute path with resource_path
        for item in pathlib.Path(sprite_path).rglob('*.png'):
            if item.is_file():
                image = pg.image.load(item).convert_alpha()
                image = pg.transform.scale(image, (TILE_SIZE, TILE_SIZE))
                images.append(image)

        return images


    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        self.fast_user_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        if self.is_paused or self.forfeit_prompt or self.tetris.game_over:
            self.clock.tick(FPS)
            return
        self.tetris.update()
        current_time = pg.time.get_ticks()

        if self.left_pressed or self.right_pressed:
            direction = pg.K_LEFT if self.left_pressed else pg.K_RIGHT
            delay = self.move_delay if self.initial_hold else self.move_interval

            if current_time - self.last_move_time >= delay:
                self.tetris.control(direction)
                self.last_move_time = current_time
                self.initial_hold = False
        self.clock.tick(FPS)

    def draw(self):
        self.screen.fill(color=BG_COLOR)
        self.screen.fill(color=FIELD_COLOR, rect=(0, 0, *FIELD_RES))
        self.tetris.draw()
        self.text.draw()

        if self.forfeit_prompt:
            overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))

            font = pg.font.Font(resource_path(FONT_PATH), 32)
            msg = font.render("Forfeit? [Y/N]", True, 'white')
            rect = msg.get_rect(center=(WIN_RES[0] // 2, WIN_RES[1] // 2))
            self.screen.blit(msg, rect)

        pg.display.flip()

    def check_events(self):
        self.anim_trigger = False
        self.fast_anim_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if self.forfeit_prompt:
                    if event.key == pg.K_y:
                        self.tetris.game_over = True
                        self.tetris.game_over_time = pg.time.get_ticks()
                        self.forfeit_prompt = False
                        self.is_paused = False
                    elif event.key == pg.K_n:
                        self.forfeit_prompt = False
                        self.is_paused = False
                    return

                if event.key == pg.K_f and not self.tetris.game_over:
                    self.forfeit_prompt = True
                    self.is_paused = True
                    return

                if event.key == pg.K_r and self.tetris.game_over:
                    if pg.time.get_ticks() - self.tetris.game_over_time >= 500:
                        self.tetris.reset()

                if not self.is_paused:
                    if event.key == pg.K_LEFT:
                        self.tetris.control(pg.K_LEFT)
                        self.left_pressed = True
                        self.last_move_time = pg.time.get_ticks()
                        self.initial_hold = True
                    elif event.key == pg.K_RIGHT:
                        self.tetris.control(pg.K_RIGHT)
                        self.right_pressed = True
                        self.last_move_time = pg.time.get_ticks()
                        self.initial_hold = True
                    else:
                        self.tetris.control(pressed_key=event.key)

            elif event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    self.left_pressed = False
                if event.key == pg.K_RIGHT:
                    self.right_pressed = False

            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.fast_user_event:
                self.fast_anim_trigger = True



    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    app = App()
    app.run()