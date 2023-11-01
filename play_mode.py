from pico2d import *
import game_framework

import game_world
from grass import Grass
from bird import Bird


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            bird.handle_event(event)

def init():
    global grass
    global bird
    global birds
    running = True

    grass = Grass()
    game_world.add_object(grass, 0)

    bird = Bird(400, 90)
    birds = [Bird(100 * i, 90) for i in range(10)]
    game_world.add_objects(birds, 1)


def finish():
    game_world.clear()
    pass


def update():
    game_world.update()
    # delay(0.1)


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause():
    pass

def resume():
    pass

