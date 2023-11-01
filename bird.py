# 이것은 각 상태들을 객체로 구현한 것임.
PIXEL_PER_METER = (20.0 / 0.3) # 10픽셀에 0.3 미터
RUN_SPEED_KMPH = 20.0 # 시간당 20km
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACITON = 14
FRAMES_PER_TIME = ACTION_PER_TIME * FRAMES_PER_ACITON

from pico2d import get_time, load_image, load_font, clamp,  SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT
from ball import Ball, BigBall
import game_world
import game_framework

# state event check
# ( state event type, event value )

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def time_out(e):
    return e[0] == 'TIME_OUT'

# time_out = lambda e : e[0] == 'TIME_OUT'




# bird Run Speed
# fill here

# bird Action Speed
# fill here









class Idle:

    @staticmethod
    def enter(bird, e):
        if bird.face_dir == -1:
            bird.action = 2
        elif bird.face_dir == 1:
            bird.action = 3
        bird.dir = 0
        bird.frame = 0
        bird.wait_time = get_time() # pico2d import 필요
        pass

    @staticmethod
    def exit(bird, e):
        if space_down(e):
            bird.fire_ball()
        pass

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + FRAMES_PER_TIME * game_framework.frame_time) % 5
        if get_time() - bird.wait_time > 2:
            bird.state_machine.handle_event(('TIME_OUT', 0))

    @staticmethod
    def draw(bird):
        bird.image.clip_draw(int(bird.frame) * 182, 0, 150, 150, bird.x, bird.y)



class Run:

    @staticmethod
    def enter(bird, e):
        if right_down(e) or left_up(e): # 오른쪽으로 RUN
            bird.dir, bird.action, bird.face_dir = 1, 1, 1
        elif left_down(e) or right_up(e): # 왼쪽으로 RUN
            bird.dir, bird.action, bird.face_dir = -1, 0, -1

    @staticmethod
    def exit(bird, e):
        if space_down(e):
            bird.fire_ball()

        pass

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + FRAMES_PER_TIME * game_framework.frame_time) % 14
        if int(bird.frame) < 6:
            bird.height = 362
            bird.cnt = int(bird.frame) % 5
        elif int(bird.frame) < 11:
            bird.height = 161
            bird.cnt = int(bird.frame) % 5
        elif int(bird.frame) >= 11:
            bird.height = 0
            bird.cnt = int(bird.frame) % 5

        bird.x += bird.dir * RUN_SPEED_PPS * game_framework.frame_time
        if(bird.x > 1500):
            bird.dir = -1
        elif (bird.x < 50):
            bird.dir = 1
    @staticmethod
    def draw(bird):
        if(bird.dir > 0):
            bird.image.clip_draw(bird.cnt * 182 + 10, bird.height, 180, 150, bird.x, bird.y, 100, 100)
        else:
            bird.image.clip_composite_draw(bird.cnt * 182 + 10, bird.height, 180, 150, 0, 'h', bird.x, bird.y, 100, 100)



class StateMachine:
    def __init__(self, bird):
        self.bird = bird
        self.cur_state = Run
        self.transitions = {
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, space_down: Idle},
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, space_down: Run},
        }

    def start(self):
        self.cur_state.enter(self.bird, ('NONE', 0))

    def update(self):
        self.cur_state.do(self.bird)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.bird, e)
                self.cur_state = next_state
                self.cur_state.enter(self.bird, e)
                return True

        return False

    def draw(self):
        self.cur_state.draw(self.bird)





class Bird:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.frame = 0
        self.action = 0
        self.face_dir = 1
        self.dir = 1
        self.cnt = -1
        self.image = load_image('bird_animation.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        self.font = load_font('ENCR10B.TTF', 16)
        self.height = 0

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        self.font.draw(self.x - 60, self.y + 50, f'(Time: {get_time():2f})', (255, 255, 0))