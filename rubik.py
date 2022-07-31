from ursina import *


class Game(Ursina):
    ANIM_DURATION = 0.3
    RUBIK_MOD = 'assets/rubik'
    RUBIK_TEX = 'assets/rubik_texture'
    SKY_TEX = 'assets/sky0'

    def __init__(self):
        super().__init__()
        self.DOWN_SENSOR = None
        self.UP_SENSOR = None
        self.BACK_SENSOR = None
        self.FACE_SENSOR = None
        self.RIGHT_SENSOR = None
        self.LEFT_SENSOR = None
        window.fullscreen = True
        # Plane
        Entity(model='quad', scale=60, texture='white_cube', texture_scale=(60, 60), rotation_x=90, y=-5,
               color=color.light_gray)
        # Sky
        Entity(model='sphere', scale=100, texture=self.SKY_TEX, double_sided=True)
        EditorCamera()
        camera.world_position = (0, 0, -15)
        self.message = Text(origin=(0, 19), color=color.black)
        self.action_trigger = True
        self.action_mode = True
        self.BACK = None
        self.FACE = None
        self.UP = None
        self.RIGHT = None
        self.LEFT = None
        self.DOWN = None
        self.CUBES = None
        self.SIDES = None
        self.cube_side_positions = None
        self.rotation_axis = None
        self.PARENT = None
        self.load_game()

    def rotate_side(self, side_name: str):
        rotation_side = self.cube_side_positions[side_name]
        rotation_axis = self.rotation_axis[side_name]
        self.reparent_to_scene()
        for cube in self.CUBES:
            if cube.position in rotation_side:
                cube.parent = self.PARENT
                exec(f'self.PARENT.rotation_{rotation_axis}=90')

    def random_state(self, rotation: int = 5):
        for i in range(rotation):
            self.rotate_side(random.choice(list(self.rotation_axis)))

    def toggle_action_trigger(self):
        self.action_trigger = not self.action_trigger

    def create_cube_position(self):
        self.LEFT = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.DOWN = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}
        self.RIGHT = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.UP = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}
        self.FACE = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        self.BACK = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        self.SIDES = self.LEFT | self.DOWN | self.RIGHT | self.UP | self.FACE | self.BACK

    def create_sensors(self):
        def make_sensor(name, pos, scale):
            return Entity(name=name, position=pos, model='cube', scale=scale, collider='box', visible=False)
        self.LEFT_SENSOR = make_sensor('L', (-0.99, 0, 0), (1.01, 3.01, 3.01))
        self.RIGHT_SENSOR = make_sensor('R', (0.99, 0, 0), (1.01, 3.01, 3.01))
        self.FACE_SENSOR = make_sensor('F', (0, 0, -0.99), (3.01, 3.01, 1.01))
        self.BACK_SENSOR = make_sensor('B', (0, 0, 0.99), (3.01, 3.01, 1.01))
        self.UP_SENSOR = make_sensor('U', (0, 1, 0), (3.01, 1.01, 3.01))
        self.DOWN_SENSOR = make_sensor('D', (0, -1, 0), (3.01, 1.01, 3.01))

    def toggle_game_mode(self):
        self.action_mode = not self.action_mode
        msg = dedent(f"{'ACTION mode ON' if self.action_mode else 'VIEW mode ON'}"
                     f"(to switch - press Middle Mouse Button)").strip()
        self.message.text = msg

    def load_game(self):
        self.create_cube_position()
        self.CUBES = [Entity(model=self.RUBIK_MOD, texture=self.RUBIK_TEX, position=pos) for pos in self.SIDES]
        self.PARENT = Entity()
        self.rotation_axis = {'L': 'x', 'R': 'x', 'U': 'y', 'D': 'y', 'F': 'z', 'B': 'z'}
        self.cube_side_positions = {'L': self.LEFT, 'D': self.DOWN, 'R': self.RIGHT, 'U': self.UP, 'F': self.FACE,
                                    'B': self.BACK}
        self.toggle_game_mode()
        self.create_sensors()
        self.random_state(20)

    def rotate_side_animate(self, side_name: str, reverse: bool = False):
        self.action_trigger = False
        cube_position = self.cube_side_positions[side_name]
        rotation_axis = self.rotation_axis[side_name]
        self.reparent_to_scene()
        for cube in self.CUBES:
            if cube.position in cube_position:
                cube.parent = self.PARENT
                if side_name in 'RFU':
                    deg = -90 if reverse else 90
                else:
                    deg = 90 if reverse else -90
                eval(f'self.PARENT.animate_rotation_{rotation_axis}({deg}, duration=self.ANIM_DURATION)')
        invoke(self.toggle_action_trigger, delay=self.ANIM_DURATION + 0.1)

    def reparent_to_scene(self):
        for cube in self.CUBES:
            if cube.parent == self.PARENT:
                world_pos, world_rot = round(cube.world_position, 1), cube.world_rotation
                cube.parent = scene
                cube.position, cube.rotation = world_pos, world_rot
        self.PARENT.rotation = 0

    def input(self, key):
        if key in 'mouse1 mouse3' and self.action_mode and self.action_trigger:
            for hitinfo in mouse.collisions:
                collider_name = hitinfo.entity.name
                if key == 'mouse1' and collider_name in 'LRFB' or key == 'mouse3' and collider_name in 'UD':
                    if held_keys['space']:
                        self.rotate_side_animate(collider_name, True)
                    else:
                        self.rotate_side_animate(collider_name)
                    break
        if key == 'mouse2':
            self.toggle_game_mode()
        super().input(key)


if __name__ == '__main__':
    game = Game()
    game.run()
