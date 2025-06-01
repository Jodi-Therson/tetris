from settings import *
import random

class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, pos):
        self.tetromino = tetromino
        self.pos = vec(pos) + INIT_POS_OFFSET
        self.next_pos = vec(pos) + NEXT_POS_OFFSET
        self.alive = True

        super().__init__(tetromino.tetris.sprite_group)
        self.image = tetromino.image
        # self.image = pg.Surface([TILE_SIZE, TILE_SIZE])
        # pg.draw.rect(self.image, 'orange', (1, 1, TILE_SIZE - 2, TILE_SIZE - 2), border_radius=8)
        self.rect = self.image.get_rect()

    def is_alive(self):
        if not self.alive:
            self.kill()

    def rotate(self, pivot_pos):
        translated = self.pos - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos

    def set_rect_pos(self):
        pos = [self.next_pos, self.pos][self.tetromino.current]
        self.rect.topleft = pos * TILE_SIZE

    def update(self):
        self.is_alive()
        self.set_rect_pos()

    def is_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (
            y < 0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True

class Tetromino:
    def __init__(self, tetris, current=True):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.image = random.choice(tetris.app.images)
        self.blocks = [Block(self, pos) for pos in TETROMINOES[self.shape]]
        self.landing = False
        self.current = current

    def rotate(self):
        pivot_pos = self.blocks[0].pos
        new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

        if not self.is_collide(new_block_positions):
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]
            return
        
        for dx in [-1, 1]:
            kicked_positions = [pos + vec(dx, 0) for pos in new_block_positions]
            if not self.is_collide(kicked_positions):
                for i, block in enumerate(self.blocks):
                    block.pos = kicked_positions[i]
                return

    def is_collide(self, block_positions):
        return any(map(Block.is_collide, self.blocks, block_positions))

    def move(self, direction):
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_positions = [block.pos + move_direction for block in self.blocks]
        is_collide = self.is_collide(new_block_positions)

        if not is_collide:
            for block in self.blocks:
                block.pos += move_direction
        elif direction == 'down':
            self.landing = True

    def update(self):
        self.move(direction='down')

    def get_ghost_positions(self):
        ghost_positions = [vec(block.pos) for block in self.blocks]

        while True:
            test_positions = [pos + vec(0, 1) for pos in ghost_positions]
            if any(self.is_position_collide(pos) for pos in test_positions):
                break
            ghost_positions = test_positions

        return ghost_positions

    def is_position_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (
            y < 0 or not self.tetris.field_array[y][x]):
            return False
        return True

    
    def draw_ghost(self):
        ghost_positions = self.get_ghost_positions()

        ghost_image = self.image.copy()
        ghost_image.set_alpha(80)  # 0 = invisible, 255 = fully opaque

        for pos in ghost_positions:
            rect = ghost_image.get_rect(topleft=(pos.x * TILE_SIZE, pos.y * TILE_SIZE))
            self.tetris.app.screen.blit(ghost_image, rect.topleft)

    def hard_drop(self):
        while not self.landing:
            self.move('down')