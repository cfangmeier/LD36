from enum import IntEnum

from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivent_core.systems.gamesystem import GameSystem
from kivent_core.managers.resource_managers import texture_manager
from kivy.factory import Factory

from app.utils import asset_path
from app.config import TILE_WIDTH, TILE_HEIGHT


class TileSystem(GameSystem):
    camera_pos = ListProperty(None, allownone=True)
    camera_size = ListProperty(None, allownone=True)
    camera_scale = NumericProperty(1.)
    atlas = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tiles_on_screen_last_frame = set()
        self.tile_trigger = Clock.create_trigger(self.handle_tile_drawing)
        self.tiles = {}
        self.initialized = False

    def setup(self):
        import json
        atlas_path = asset_path('{}.atlas'.format(self.atlas),
                                'assets/textures')
        texture_manager.load_atlas(atlas_path)
        ld_rec = self.gameworld.model_manager.load_textured_rectangle
        with open(atlas_path) as atlas:
            js = json.load(atlas)
            self.tile_keys = js['{}-0.png'.format(self.atlas)].keys()
        for tile in self.tile_keys:
            ld_rec('vertex_format_4f', 64., 64., tile, tile)
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
                remove_entity(tile_comp.graphics_entity)
                tile_comp.current_entity = None
            for component_index in to_add:
                tile_comp = self.components[component_index]
                screen_pos = screen_pos_from_tile_pos(tile_comp.tile_pos)
                model = self.get_model_at_tile(component_index)
                create_dict = {
                    'position': screen_pos,
                    'renderer': {'texture': model,
                                 'model_key': model}
                    }
                ent = init_entity(create_dict, ['position', 'renderer'])
                tile_comp.graphics_entity = ent
                tile_comp.dirty = False

    def get_screen_pos_from_tile_pos(self, tile_pos):
        wx, wy = self.get_world_pos_from_tile_pos(tile_pos)
        return wx, wy

    def get_world_pos_from_tile_pos(self, tile_pos):
        return (tile_pos[0] * TILE_WIDTH,
                tile_pos[1] * TILE_HEIGHT)

    def get_tile_at_world_pos(self, world_pos):
        return (int(world_pos[0] // TILE_WIDTH),
                int(world_pos[1] // TILE_HEIGHT))

    def calculate_tiles_in_view(self):
        cx, cy = -self.camera_pos[0], -self.camera_pos[1]
        cw, ch = self.camera_size
        scale = self.camera_scale
        x_count = int(scale*cw // TILE_WIDTH) + 4
        y_count = int(scale*ch // TILE_HEIGHT) + 4
        starting_x = int(cx/TILE_WIDTH) - 1
        starting_y = int(cy/TILE_HEIGHT) - 1
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
        type_ = self.components[component_index].type
        model_name = '{}_{}'.format(self.atlas, type_.name)
        return model_name

    def get_tile(self, x, y):
        self.ensure_tile_exists(x, y)
        component = self.components[self.tiles[(x, y)]]
        return component

    def init_component(self, component_index, entity_id, zone, args):
        component = self.components[component_index]
        component.entity_id = entity_id
        component.type = args.get('type')
        component.tile_pos = tx, ty = args.get('tile_pos')
        component.current_entity = None
        component.dirty = True
        self.tiles[(tx, ty)] = component_index

    def gen_new_tile(self, x, y):
        raise NotImplementedError("Override this in the subclass!")


class Terrain(TileSystem):
    atlas = 'terrain'

    class Type(IntEnum):
        blank = 0
        desert = 1
        grass = 2
        hills = 3
        mountains = 4
        wetland = 5

    def gen_new_tile(self, x, y):
        import noise
        scale = 20
        val = noise.snoise2(x/scale, y/scale)
        if val < -.6:
            type_ = Terrain.Type.hills
        elif val < .6:
            type_ = Terrain.Type.grass
        else:
            type_ = Terrain.Type.mountains
        create_dict = {
            'terrain': {'type': type_, 'tile_pos': (x, y)},
        }
        self.gameworld.init_entity(create_dict, ['terrain'])


class Buildings(TileSystem):
    atlas = 'building'

    class Type(IntEnum):
        blank = 0
        field = 1
        granary = 2
        house = 3
        temple = 4
        well = 5
        road = 6

    def get_road_texture(self, component_index):
        road_texture_lookup = {
                '0000': 'road_start', '0001': 'road_end_W',
                '0010': 'road_end_E', '0011': 'road_plain_EW',
                '0100': 'road_end_S', '0101': 'road_L_SW',
                '0110': 'road_L_SE', '0111': 'road_T_S',
                '1000': 'road_end_N', '1001': 'road_L_NW',
                '1010': 'road_L_NE', '1011': 'road_T_N',
                '1100': 'road_plain_NS', '1101': 'road_T_W',
                '1110': 'road_T_E', '1111': 'road_cross'}
        component = self.components[component_index]
        road_type = Buildings.Type.road
        tx, ty = component.tile_pos
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x, y = tx+dx, ty+dy
            if (x, y) in self.tiles:
                neighbor_index = self.tiles[(x, y)]
                building_type = self.components[neighbor_index].type
                has_road = '1' if building_type == road_type else '0'
                neighbors.append(has_road)
            else:
                neighbors.append('0')
        key = ''.join(neighbors)
        return road_texture_lookup[key]

    def get_model_at_tile(self, component_index):
        building_type = self.components[component_index].type
        if building_type == Buildings.Type.road:
            texture = self.get_road_texture(component_index)
        else:
            texture = building_type.name
        return '{}_{}'.format(self.atlas, texture)

    def gen_new_tile(self, x, y):
        create_dict = {
            'buildings': {'type': Buildings.Type.blank, 'tile_pos': (x, y)},
        }
        self.gameworld.init_entity(create_dict, ['buildings'])

    def set_tile(self, x, y, building_type):
        if type(building_type) == str:
            building_type = Buildings.Type[building_type]
        self.ensure_tile_exists(x, y)
        component = self.components[self.tiles[(x, y)]]
        component.type = building_type
        component.tile_pos = (x, y)
        component.dirty = True
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            tx, ty = x+dx, y+dy
            try:
                self.components[self.tiles[(tx, ty)]].dirty = True
            except KeyError:
                pass
        self.tile_trigger()


Factory.register('TileSystem', cls=TileSystem)
Factory.register('Terrain', cls=Terrain)
Factory.register('Buildings', cls=Buildings)
