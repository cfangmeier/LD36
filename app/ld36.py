import itertools

from kivy.app import App
from kivy.config import Config
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget

from app.utils import asset_path
from app.config import TILE_WIDTH, TILE_HEIGHT, SCALE_STEP


Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
MUTE = True


class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.in_motion = False
        gamesystems = ['renderer', 'position',
                       'camera1', 'terrain',
                       'buildings']
        self.gameworld.init_gameworld(gamesystems, callback=self.init_game)

    def init_game(self):
        Window.size = (64*15, 64*15)
        self.setup_sound()
        self.setup_states()
        self.gameworld.terrain.setup()
        self.gameworld.buildings.setup()
        self.set_state()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def shift_camera(self, final_pos=None, final_scale=None):
        if self.in_motion:
            return
        if final_pos is None:
            final_pos = self.gameworld.camera.camera_pos
        if final_scale is None:
            final_scale = self.gameworld.camera.camera_scale

        def motion_start(_):
            self.in_motion = True

        def motion_complete(_):
            self.in_motion = False
            self.gameworld.terrain.tile_trigger()
            self.gameworld.buildings.tile_trigger()
        anim = Animation(camera_pos=final_pos,
                         camera_scale=final_scale,
                         duration=0.15, t='out_sine')
        anim.on_start = motion_start
        anim.on_complete = motion_complete
        anim.start(self.gameworld.camera)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if not text:
            return True
        if not self.in_motion and text in 'wsad':
            motions = {'w': (0, -64),
                       's': (0, 64),
                       'a': (64, 0),
                       'd': (-64, 0)}
            motion = motions.get(text, (0, 0))
            camera_pos = self.gameworld.camera.camera_pos
            self.shift_camera(final_pos=(camera_pos[0]+motion[0],
                                         camera_pos[1]+motion[1]))

        elif text in '=-':
            scale = self.gameworld.camera.camera_scale
            if text == '=':
                scale_new = scale * SCALE_STEP
            else:
                scale_new = scale / SCALE_STEP
            if 0.25 < scale_new < 4:
                pos_x, pos_y = self.gameworld.camera.camera_pos
                size_x, size_y = Window.size
                center_x, center_y = (-pos_x + size_x*scale/2,
                                      -pos_y + size_y*scale/2)
                pos_x_new, pos_y_new = (0.5*size_x*scale_new-center_x,
                                        0.5*size_y*scale_new-center_y)
                self.shift_camera(final_pos=(pos_x_new, pos_y_new), final_scale=scale_new)
        elif text == '/':
            print('Window Size:', Window.size)
            print("Camera Position: ", self.gameworld.camera.camera_pos)
            print("Camera Scale: ", self.gameworld.camera.camera_scale)
        elif text == ' ':
            pass
        elif text == 'q':
            Window.close()
        return True

    def window_pos_to_tile_pos(self, wx, wy):
        cam = self.gameworld.camera
        scale = cam.camera_scale
        cam_pos = cam.camera_pos
        world_pos = ((wx*scale-cam_pos[0]),
                     (wy*scale-cam_pos[1]))
        tile_pos = ((world_pos[0]+TILE_WIDTH/2)//TILE_WIDTH,
                    (world_pos[1]+TILE_HEIGHT/2)//TILE_HEIGHT)
        return tile_pos

    def on_touch_down(self, event):
        # print(dir(event))
        tile_pos = self.window_pos_to_tile_pos(*event.pos)
        comp = self.gameworld.buildings.get_tile(*tile_pos)
        if event.button == 'left':
            cycle = {'blank': 'road',
                     'road': 'house',
                     'house': 'granary',
                     'granary': 'well',
                     'well': 'field',
                     'field': 'blank'}
            self.gameworld.buildings.set_tile(tile_pos[0],
                                              tile_pos[1],
                                              cycle[comp.type.name])
        elif event.button == 'right':
            self.gameworld.buildings.set_tile(tile_pos[0],
                                              tile_pos[1],
                                              'blank')

    def setup_states(self):
        self.gameworld.add_state(state_name='main',
                                 systems_added=['renderer'],
                                 systems_unpaused=['renderer'])

    def set_state(self):
        self.gameworld.state = 'main'

    def setup_sound(self):
        self.sounds = {
            'main_theme': 'LD36.ogg',
            }
        self.sound_cycle = itertools.cycle(['main_theme'])
        for key in self.sounds.keys():
            self.sounds[key] = self.load_sound(self.sounds[key])
        self.play_next()

    def load_sound(self, filename):
        sound = SoundLoader.load(asset_path(filename, 'assets/sound'))
        sound.on_stop = self.play_next
        return sound

    def play_next(self, *args, **kwargs):
        next_sound = next(self.sound_cycle)
        if MUTE:
            self.sounds[next_sound].volume = 0
        else:
            self.sounds[next_sound].volume = 1
        self.sounds[next_sound].play()


class LD36(App):
    pass


def main():
    LD36().run()
