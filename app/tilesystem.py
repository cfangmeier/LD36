import os.path as path

from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivent_core.systems.gamesystem import GameSystem
from kivent_core.managers.resource_managers import texture_manager
from kivy.factory import Factory

from app.utils import asset_path

#  TODO: Subclass TileSystem
#        Terrain
#        Buildings
#        Roads
#        Roads


class TileSystem(GameSystem):
    tile_width = NumericProperty(64.)
    tile_height = NumericProperty(64.)
    camera_pos = ListProperty(None, allownone=True)
    camera_size = ListProperty(None, allownone=True)
    camera_scale = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(TileSystem, self).__init__(**kwargs)
        self.tiles_on_screen_last_frame = set()
        self.tile_trigger = Clock.create_trigger(self.handle_tile_drawing)
        self.tiles = {}
        self.initialized = False

    def setup(self):
        ld_img = texture_manager.load_image
        ld_rec = self.gameworld.model_manager.load_textured_rectangle
        for tile in self.tile_models:
            tex_file = asset_path(tile['texture_file'], 'assets/textures')
            tex_name = path.splitext(path.basename(tex_file))[0]
            print("Creating Texture for tile: {}".format(tex_name))
            ld_img(tex_file)
            mod_name = tile['model']
            print("Creating Model for tile: {}".format(mod_name))
            model_name = ld_rec('vertex_format_4f', 64., -64., tex_name, mod_name)
            print('Model name:', model_name)
        self.initialized = True
        self.tile_trigger()

    def ensure_tile_exists(self, x, y):
        if (x, y) not in self.tiles:
            self.gen_new_tile(x, y)

    def handle_tile_drawing(self, dt):
        if self.camera_pos is not None and self.camera_size is not None:
            last_frame = self.tiles_on_screen_last_frame
            init_entity = self.gameworld.init_entity
            remove_entity = self.gameworld.remove_entity
            tiles_in_view = set(self.calculate_tiles_in_view())
            screen_pos_from_tile_pos = self.get_screen_pos_from_tile_pos
            to_add = set()
            to_rem = set()
            for component_index in tiles_in_view:
                do_update = (self.components[component_index].dirty
                             and component_index in last_frame)
                if do_update:
                    to_rem.add(component_index)  # remove old tile
                    to_add.add(component_index)  # add new tile
                elif component_index not in last_frame:
                    to_add.add(component_index)  # add new tile
            to_rem = to_rem.union(last_frame - tiles_in_view)
            self.tiles_on_screen_last_frame = tiles_in_view

            for component_index in to_rem:
                tile_comp = self.components[component_index]
                remove_entity(tile_comp.current_entity)
                tile_comp.current_entity = None
            for component_index in to_add:
                tile_comp = self.components[component_index]
                screen_pos = screen_pos_from_tile_pos(tile_comp.tile_pos)
                model = self.get_model_at_tile(component_index)
                # print(model)
                create_dict = {
                    'position': screen_pos,
                    'renderer': {'model_key': model},
                    }
                ent = init_entity(create_dict, ['position', 'renderer'])
                tile_comp.current_entity = ent
                tile_comp.dirty = False

    def get_screen_pos_from_tile_pos(self, tile_pos):
        wx, wy = self.get_world_pos_from_tile_pos(tile_pos)
        return wx, wy

    def get_world_pos_from_tile_pos(self, tile_pos):
        return (tile_pos[0] * self.tile_width,
                tile_pos[1] * self.tile_height)

    def get_tile_at_world_pos(self, world_pos):
        return (int(world_pos[0] // self.tile_width),
                int(world_pos[1] // self.tile_height))

    def calculate_tiles_in_view(self):
        cx, cy = -self.camera_pos[0], -self.camera_pos[1]
        cw, ch = self.camera_size
        scale = self.camera_scale
        tile_width = self.tile_width
        tile_height = self.tile_height
        x_count = int(scale*cw // tile_width) + 4
        y_count = int(scale*ch // tile_height) + 4
        starting_x = int(cx/tile_width) - 1
        starting_y = int(cy/tile_height) - 1
        end_x = starting_x + x_count
        end_y = starting_y + y_count
        tiles_in_view = []
        tiles = self.tiles
        for x in range(starting_x, end_x):
            for y in range(starting_y, end_y):
                self.ensure_tile_exists(x, y)
                tile = tiles.get((x, y))
                if tile is not None:
                    tiles_in_view.append(tile)
        return tiles_in_view

    def set_tile(self, x, y, **kwargs):
        self.ensure_tile_exists(x, y)
        component = self.components[self.tiles[(x, y)]]
        for key, val in kwargs.items():
            setattr(component, key, val)
        component.dirty = True
        self.tile_trigger()

    def get_model_at_tile(self, component_index):
        return self.components[component_index].model

    def get_tile(self, x, y):
        self.ensure_tile_exists()
        component = self.components[self.tiles[(x, y)]]
        return component

    def init_component(self, component_index, entity_id, zone, args):
        component = self.components[component_index]
        component.entity_id = entity_id
        component.model = args.get('model')
        component.tile_pos = tx, ty = args.get('tile_pos')
        component.current_entity = None
        component.dirty = True
        self.tiles[(tx, ty)] = component_index


class Terrain(TileSystem):
    tile_models = [
        {'texture_file': 'desert.png',
         'model': 'desert',
         'cw_rotate': 0,
         'mirror_vert': False,
         'mirror_horz': False},
        {'texture_file': 'grass.png',
         'model': 'grass',
         'cw_rotate': 0,
         'mirror_vert': False,
         'mirror_horz': False},
        {'texture_file': 'hills.png',
         'model': 'hills',
         'cw_rotate': 0,
         'mirror_vert': False,
         'mirror_horz': False},
        {'texture_file': 'wetland.png',
         'model': 'wetland',
         'cw_rotate': 0,
         'mirror_vert': False,
         'mirror_horz': False},
        {'texture_file': 'mountains.png',
         'model': 'mountains',
         'cw_rotate': 0,
         'mirror_vert': False,
         'mirror_horz': False},
            ]

Factory.register('TileSystem', cls=TileSystem)
Factory.register('Terrain', cls=Terrain)
