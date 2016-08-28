from os.path import dirname, join, abspath
from random import choice
import itertools

import kivy
from kivy.app import App
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.factory import Factory

import kivent_core
from kivent_core.gameworld import GameWorld
from kivent_core.managers.resource_managers import texture_manager
from kivent_core.systems.gamesystem import GameSystem

import noise

from app.tilesystem import TileSystem

TILES = {'desert': 'desert.png',
         'grass': 'grass.png',
         'hills': 'hills.png',
         'mountains': 'mountains.png',
         'wetland': 'wetland.png'}


def asset_path(asset, asset_loc):
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
        self.setup_sound()
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
        elif text == '/':
            print('Window Size:', Window.size)
            print("Camera Position: ", self.gameworld.camera.camera_pos)
            print("Camera Scale: ", self.gameworld.camera.camera_scale)
            # print(dir(self.gameworld.camera))
        elif text == 'q':
            Window.close()
        return True

    def load_textures(self):
        for tile_file in TILES.values():
            texture_manager.load_image(asset_path(tile_file, 'assets/tiles'))

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
                if val < -.6:
                    model_key = 'wetland'
                elif val < .6:
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

    def setup_sound(self):
        self.sounds = {
            'main1abc': 'Main1abc.wav',
            'main1bc': 'Main1bc.wav',
            'main1intro': 'Main1Intro.wav',
            'main2ab': 'Main2ab.wav',
            'main2abc': 'Main2abc.wav',
            'main2ac': 'Main2ac.wav',
            'main2b': 'Main2b.wav',
            'main2bc': 'Main2bc.wav',
            'main3a': 'Main3a.wav',
            'main3ab': 'Main3ab.wav',
            'main3abc': 'Main3abc.wav',
            'main3b': 'Main3b.wav',
            }
        self.sound_cycle = itertools.cycle([
            'main1intro', 'main1abc', 'main1bc',
            'main2bc', 'main2ab', 'main2b',
            'main2bc', 'main2abc', 'main2ac',
            'main1abc', 'main1abc', 'main2bc',
            'main3b', 'main3a', 'main3abc',
            'main1abc', 'main3ab', 'main3b'])
        for key in self.sounds.keys():
            self.sounds[key] = self.load_sound(self.sounds[key])
        self.play_next()

    def load_sound(self, filename):
        sound = SoundLoader.load(asset_path(filename, 'assets/sound'))
        sound.on_stop = self.play_next
        return sound

    def play_next(self, *args, **kwargs):
        next_sound = next(self.sound_cycle)
        print("playing next song: \"{}\"".format(next_sound))
        self.sounds[next_sound].play()


class LD36(App):
    pass


def main():
    LD36().run()
