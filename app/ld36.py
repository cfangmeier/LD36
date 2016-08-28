from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from random import choice
import kivent_core
from kivent_core.gameworld import GameWorld
from kivent_core.managers.resource_managers import texture_manager
from kivy.properties import StringProperty, NumericProperty, ListProperty
from os.path import dirname, join, abspath
from kivent_core.systems.gamesystem import GameSystem
from kivy.factory import Factory
import noise

from app.tilesystem import TileSystem

# TILES = {'desert': 'desert.png',
#          'grass': 'grass.png'}
TILES = {'desert': 'desert.png',
         'grass': 'grass.png',
         'hills': 'hills.png',
         'mountains': 'mountains.png',
         'wetland': 'wetland.png'}


def get_asset_path(asset, asset_loc):
    return join(dirname(dirname(abspath(__file__))), asset_loc, asset)


class Character(Widget):
    pass


class TestGame(Widget):
    def __init__(self, **kwargs):
        super(TestGame, self).__init__(**kwargs)
        self.in_motion = False
        self.gameworld.init_gameworld(
            ['renderer', 'position', 'camera1', 'tiles'],
            callback=self.init_game)

    def init_game(self):
        Window.size = (64*15, 64*15)
        self.setup_states()
        self.load_textures()
        self.load_models()
        self.set_state()
        self.setup_tiles()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # print(text)
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

        elif text in '=-':
            zoom = {'=': 1.1,
                    '-': .9}
            current_zoom = self.gameworld.camera.camera_scale
            new_zoom = current_zoom*zoom[text]
            if 0.25 < new_zoom < 4:
                self.gameworld.camera.camera_scale = new_zoom
        elif text == '/':
            print('Window Size:', Window.size)
            print("Current Zoom: ", self.gameworld.camera.camera_scale)
            print("Current Position: ", self.gameworld.camera.camera_pos)
        elif text == 'q':
            Window.close()
        return True

    def load_textures(self):
        for tile_file in TILES.values():
            texture_manager.load_image(get_asset_path(tile_file,
                                                      'assets/tiles'))

    def load_models(self):
        model_manager = self.gameworld.model_manager
        for tile in TILES.keys():
            model_manager.load_textured_rectangle('vertex_format_4f',
                                                  64., 64.,
                                                  tile, tile)

    def setup_tiles(self):
        init_entity = self.gameworld.init_entity
        tile_system = self.ids.tiles
        for x in range(tile_system.tiles_in_x):
            for y in range(tile_system.tiles_in_y):
                scale = 20
                val = noise.snoise2(x/scale, y/scale)
                if val < -.4:
                    model_key = 'wetland'
                elif val < .4:
                    model_key = 'grass'
                else:
                    model_key = 'mountains'
                create_dict = {
                    'tiles': {'texture': model_key, 'tile_pos': (x, y)},
                }
                init_entity(create_dict, ['tiles'])
        tile_system.tile_trigger()

    def setup_states(self):
        self.gameworld.add_state(state_name='main', systems_added=['renderer'],
                                 systems_unpaused=['renderer'])

    def set_state(self):
        self.gameworld.state = 'main'


class LD36(App):
    pass


def main():
    LD36().run()
