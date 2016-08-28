from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivent_core.systems.gamesystem import GameSystem
from kivy.factory import Factory
from time import sleep


class TileSystem(GameSystem):
    tile_width = NumericProperty(64.)
    tile_height = NumericProperty(64.)
    tiles_in_x = NumericProperty(200)
    tiles_in_y = NumericProperty(200)
    camera_pos = ListProperty(None, allownone=True)
    camera_size = ListProperty(None, allownone=True)
    camera_scale = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(TileSystem, self).__init__(**kwargs)
        self.tiles_on_screen_last_frame = set()
        self.tile_trigger = Clock.create_trigger(self.handle_tile_drawing)
        self.calc_tiles(0)
        self.calc_tiles_trigger = Clock.create_trigger(self.calc_tiles)

    def calc_tiles(self, dt):
        self.tiles = [[None for y in range(self.tiles_in_y)] for x in range(
                     self.tiles_in_x)]

    def on_tiles_in_x(self, instance, value):
        self.calc_tiles_trigger()

    def on_tiles_in_y(self, instance, value):
        self.calc_tiles_trigger()

    def on_camera_pos(self, instance, value):
        self.tile_trigger()

    def on_camera_scale(self, instance, value):
        self.tile_trigger()

    def handle_tile_drawing(self, dt):
        if self.camera_pos is not None and self.camera_size is not None:
            last_frame = self.tiles_on_screen_last_frame
            init_entity = self.gameworld.init_entity
            remove_entity = self.gameworld.remove_entity
            tiles_in_view = set(self.calculate_tiles_in_view())
            screen_pos_from_tile_pos = self.get_screen_pos_from_tile_pos
            new = tiles_in_view - last_frame
            removed = last_frame - tiles_in_view
            self.tiles_on_screen_last_frame = tiles_in_view
            for component_index in removed:
                tile_comp = self.components[component_index]
                remove_entity(tile_comp.current_entity)
                tile_comp.current_entity = None
            for component_index in new:
                tile_comp = self.components[component_index]
                screen_pos = screen_pos_from_tile_pos(
                        tile_comp.tile_pos)
                create_dict = {
                    'position': screen_pos,
                    'renderer': {'texture': tile_comp.texture,
                                 'model_key': tile_comp.texture},
                    }
                ent = init_entity(create_dict, ['position', 'renderer'])
                tile_comp.current_entity = ent

    def on_camera_size(self, instance, value):
        self.tile_trigger()

    def get_world_pos(self, pos):
        tile_max_x = self.tiles_in_x * self.tile_width
        tile_max_y = self.tiles_in_y * self.tile_height
        return (pos[0] % tile_max_x, pos[1] % tile_max_y)

    def get_screen_pos_from_tile_pos(self, tile_pos):
        cx, cy = -self.camera_pos[0], -self.camera_pos[1]
        tile_max_x = self.tiles_in_x * self.tile_width
        tile_max_y = self.tiles_in_y * self.tile_height
        tcx, tcy = self.get_tile_at_world_pos(
            self.get_world_pos((cx, cy)))
        wx, wy = self.get_world_pos_from_tile_pos(tile_pos)
        origin_x, origin_y = None, None
        if tile_pos[0] < tcx:
            origin_x = (cx // tile_max_x + 1) * tile_max_x
        else:
            origin_x = (cx // tile_max_x) * tile_max_x
        if tile_pos[1] < tcy:
            origin_y = (cy // tile_max_y + 1) * tile_max_y
        else:
            origin_y = (cy // tile_max_y) * tile_max_y
        return origin_x + wx, origin_y + wy

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
        tiles_in_x = self.tiles_in_x
        tiles_in_y = self.tiles_in_y
        world_pos = self.get_world_pos((cx, cy))
        x_count = int(scale*cw // tile_width) + 4
        y_count = int(scale*ch // tile_height) + 4
        starting_x, starting_y = self.get_tile_at_world_pos(world_pos)
        end_x = starting_x + x_count
        end_y = starting_y + y_count
        tiles_in_view = []
        tiles_a = tiles_in_view.append
        tiles = self.tiles
        for x in range(starting_x, end_x):
            actual_x = x % tiles_in_x
            for y in range(starting_y, end_y):
                actual_y = y % tiles_in_y
                tile = tiles[actual_x][actual_y]
                if tile is not None:
                    tiles_a(tile)
        return tiles_in_view

    def init_component(self, component_index, entity_id, zone, args):
        component = self.components[component_index]
        component.entity_id = entity_id
        component.texture = args.get('texture')
        component.tile_pos = tx, ty = args.get('tile_pos')
        component.current_entity = None
        self.tiles[tx][ty] = component_index

Factory.register('TileSystem', cls=TileSystem)
