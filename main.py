import arcade

from random import randrange
from threading import Thread

SCREEN_WIDTH = 730
SCREEN_HEIGHT = 730
SCREEN_TITLE = "Airplane"

RECT_WIDTH = 70
RECT_HEIGHT = 70

MOVEMENT_SPEED = 5

BULLET_SPEED = 10

BACKGROUND_COLOR = arcade.color.AMAZON

RED = arcade.color.RED
BLACK = arcade.color.BLACK
WHITE = arcade.color.WHITE

ENEMY_SPEED = -MOVEMENT_SPEED / 5

END = -9999


class Enemy(arcade.Sprite):

    def __init__(self, enemy_speed):
        super().__init__('enemy.png')

        self.width = RECT_WIDTH - RECT_WIDTH / 4
        self.height = RECT_HEIGHT - RECT_HEIGHT / 4

        self.angle = 180

        self.speed = enemy_speed

    def update(self):
        self.center_x = self.center_x
        self.center_y += self.speed


class Airplane(arcade.Sprite):

    def __init__(self):
        super().__init__('aircraft.png')

        self.width = RECT_WIDTH
        self.height = RECT_HEIGHT

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y


class Bullet(arcade.Sprite):

    def __init__(self):
        super().__init__('laserRed01.png')

        self.width = RECT_WIDTH / 4
        self.height = RECT_HEIGHT / 4

    def update(self):
        self.center_x = self.center_x
        self.center_y += BULLET_SPEED


class Heart(arcade.Sprite):

    def __init__(self):
        super().__init__('heart.png')

        self.width = 15
        self.height = 15

    def update(self):
        self.center_x = self.center_x
        self.center_y = self.center_y


class MyGame(arcade.Window):

    def __init__(self, width, height, title):

        super().__init__(width, height, title)

        self.enemy_list = None

        self.airplane = None

        self.bullet_list = None

        self.heart_list = None

        self.hit_sound = None

        self.laser_sound = None

        self.score = 0

        self.total_time = 0

        self.elapsed_time = 0

        self.enter_delay = 0

        self.enemy_speed = ENEMY_SPEED

        self.increased = False

        self.interval = 7

        self.lost = False

        self.threads = []

    def setup(self):
        """ Set up the game and initialize the variables. """

        arcade.set_background_color(BACKGROUND_COLOR)

        self.enemy_list = arcade.SpriteList()

        self.airplane = Airplane()
        self.airplane.center_x = randrange(35, SCREEN_WIDTH - 35, 35)
        self.airplane.center_y = randrange(35, 185, 35)

        self.bullet_list = arcade.SpriteList()

        enemy = Enemy(self.enemy_speed)

        enemy.center_x = randrange(35, SCREEN_WIDTH - 35, 35)
        enemy.center_y = SCREEN_HEIGHT

        self.enemy_list.append(enemy)

        self.heart_list = arcade.SpriteList()

        heart = Heart()
        heart.center_x = 10
        heart.center_y = 10

        self.heart_list.append(heart)

        heart = Heart()
        heart.center_x = 30
        heart.center_y = 10

        self.heart_list.append(heart)

        heart = Heart()
        heart.center_x = 50
        heart.center_y = 10

        self.heart_list.append(heart)

        self.hit_sound = arcade.sound.load_sound('hit_sound.wav', False)

        self.laser_sound = arcade.sound.load_sound('laser_sound.wav', False)

        self.enter_delay = 16

    def on_draw(self):
        arcade.start_render()

        if not self.lost:
            self.enemy_list.draw()

            self.airplane.draw()

            self.heart_list.draw()

            self.bullet_list.draw()
        else:
            game_over = "GAME OVER"
            arcade.draw_text(game_over,
                             SCREEN_WIDTH / 2 - 75,
                             SCREEN_HEIGHT / 2,
                             RED,
                             22)

        score_board = f'Score = {self.score}'
        arcade.draw_text(score_board, SCREEN_WIDTH - 90, 10, WHITE, 10)

    def my_enemy_handler(self):
        enemy = Enemy(self.enemy_speed)

        enemy.center_x = randrange(35, SCREEN_WIDTH - 35, 35)
        enemy.center_y = SCREEN_HEIGHT

        self.enemy_list.append(enemy)


    def on_update(self, delta_time):
        if not self.lost:

            self.total_time += delta_time
            self.elapsed_time += delta_time

            total_seconds = int(self.total_time) % 60

            elapsed_seconds = int(self.elapsed_time) % 60

            if total_seconds % 5 == 0 and self.increased is not True and \
                    not self.enemy_speed < -5:
                self.enemy_speed -= 0.2
                self.increased = True
                if self.interval > 3:
                    self.interval -= 1

            if total_seconds % 5 != 0:
                self.increased = False

            if elapsed_seconds == self.enter_delay:
                thread = Thread(target=self.my_enemy_handler)
                thread.start()
                self.threads.append(thread)

                self.elapsed_time = 0

                self.enter_delay = randrange(0, self.interval, 1)

            if self.airplane.left <= 0:
                self.airplane.left = 1
                self.airplane.change_x = 0
            elif self.airplane.right >= SCREEN_WIDTH:
                self.airplane.right = SCREEN_WIDTH - 1
                self.airplane.change_x = 0
            if self.airplane.bottom <= 30:
                self.airplane.change_y = 0
                self.airplane.bottom = 31
            elif self.airplane.top >= 200:
                self.airplane.change_y = 0
                self.airplane.top = 200 - 1

            for enemy in self.enemy_list:
                if enemy.bottom < 0:
                    self.heart_list.remove(self.heart_list[-1])
                    enemy.remove_from_sprite_lists()

            if len(self.heart_list) == 0:
                self.lost = True

            for bullet in self.bullet_list:
                enemy_hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

                if len(enemy_hit_list) > 0:

                    self.score += 1

                    arcade.play_sound(self.hit_sound, 1.0, -1, False)
                    bullet.remove_from_sprite_lists()

                    for enemy in enemy_hit_list:
                        enemy.remove_from_sprite_lists()

                elif bullet.top >= SCREEN_HEIGHT:
                    bullet.remove_from_sprite_lists()

            self.enemy_list.update()

            self.airplane.update()

            self.heart_list.update()

            self.bullet_list.update()
        else:
            self.airplane = None
            self.enemy_list = None
            self.bullet_list = None
            self.time_delta = END
            for t in self.threads:
                t.join()
            arcade.set_background_color(BLACK)

    def on_key_press(self, key, modifiers):
        if not self.lost:
            if key == arcade.key.UP:
                self.airplane.change_y += MOVEMENT_SPEED
            elif key == arcade.key.DOWN:
                self.airplane.change_y += -MOVEMENT_SPEED
            elif key == arcade.key.LEFT:
                self.airplane.change_x += -MOVEMENT_SPEED
            elif key == arcade.key.RIGHT:
                self.airplane.change_x += MOVEMENT_SPEED

            if key == arcade.key.SPACE:
                bullet = Bullet()

                bullet.center_x = self.airplane.center_x
                bullet.center_y = self.airplane.center_y
                arcade.play_sound(self.laser_sound, 1.0, -1, False)
                self.bullet_list.append(bullet)

    def on_key_release(self, key, modifiers):
        if not self.lost:
            if key == arcade.key.UP or key == arcade.key.DOWN:
                self.airplane.change_y = 0
            elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
                self.airplane.change_x = 0


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
