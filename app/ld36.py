import itertools

from kivy.app import App
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget



from app.utils import asset_path

MUTE = True


class Character(Widget):
    pass


class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.in_motion = False
        gamesystems = ['renderer', 'position',
                       'camera1', 'terrain',
                       'roads', 'buildings']
        self.gameworld.init_gameworld(gamesystems, callback=self.init_game)

    def init_game(self):
        Window.size = (64*15, 64*15)
        self.setup_sound()
        self.setup_states()
        self.gameworld.terrain.setup()
        self.gameworld.roads.setup()
        self.gameworld.buildings.setup()
        self.set_state()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

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
            anim = Animation(camera_pos=(camera_pos[0]+motion[0],
                                         camera_pos[1]+motion[1]),
                             duration=0.25, t='out_sine')

            def motion_start(_):
                self.in_motion = True

            def motion_complete(_):
                self.in_motion = False
            anim.on_start = motion_start
            anim.on_complete = motion_complete
            anim.start(self.gameworld.camera)
            self.gameworld.terrain.tile_trigger()
            self.gameworld.roads.tile_trigger()

        elif text in '=-':
            scale = self.gameworld.camera.camera_scale
            if text == '=':
                scale_new = scale * 1.1
            else:
                scale_new = scale / 1.1
            if 0.25 < scale_new < 4:
                pos_x, pos_y = self.gameworld.camera.camera_pos
                size_x, size_y = Window.size
                center_x, center_y = (-pos_x + size_x*scale/2,
                                      -pos_y + size_y*scale/2)
                pos_x_new, pos_y_new = (0.5*size_x*scale_new-center_x,
                                        0.5*size_y*scale_new-center_y)
                self.gameworld.camera.camera_scale = scale_new
                self.gameworld.camera.camera_pos = pos_x_new, pos_y_new
                self.gameworld.terrain.tile_trigger()
                self.gameworld.roads.tile_trigger()
        elif text == '/':
            print('Window Size:', Window.size)
            print("Camera Position: ", self.gameworld.camera.camera_pos)
            print("Camera Scale: ", self.gameworld.camera.camera_scale)
        elif text == ' ':
            pass
            # building = self.gameworld.buildings.get_tile(*tile_pos).texture
            # background = self.gameworld.buildings.get_tile(*tile_pos).texture
            # print('Tile at player position: {}:{}'.format(building, background))
        elif text == 'q':
            Window.close()
        return True

    def on_touch_down(self, event):
        scale = self.gameworld.camera.camera_scale
        cam_pos = self.gameworld.camera.camera_pos
        tile_height = self.gameworld.buildings.tile_height
        tile_width = self.gameworld.buildings.tile_width
        world_pos = ((event.pos[0]*scale-cam_pos[0]),
                     (event.pos[1]*scale-cam_pos[1]))
        tile_pos = ((world_pos[0]+tile_width/2)//tile_width,
                    (world_pos[1]+tile_height/2)//tile_height)
        comp = self.gameworld.buildings.get_tile(*tile_pos)
        cycle = {'building_blank': 'building_well',
                 'building_well': 'building_house',
                 'building_house': 'building_granary',
                 'building_granary': 'building_field',
                 'building_field': 'building_blank'}
        self.gameworld.buildings.set_tile(tile_pos[0],
                                          tile_pos[1],
                                          model=cycle[comp.model])

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
