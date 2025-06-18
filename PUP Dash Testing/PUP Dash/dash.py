import pygame
import sys
import random
import spritesheet
from title_screen import show_title_screen
from welcoming_screen import show_welcoming_screen

pygame.init()

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

show_title_screen(screen)  # Show the title screen first

result = show_welcoming_screen(screen)  # Show the welcoming screen next

if result == "back":
    # Optionally, go back to title or exit
    pygame.quit()
    sys.exit()

# Virtual resolution (fixed)
VIRTUAL_WIDTH = 1600
VIRTUAL_HEIGHT = 900

# Fullscreen display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

# Virtual surface (dito ka mag-draw ng lahat)
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# --- Load assets as usual, use fixed positions/sizes ---
background_image = pygame.image.load("PUP Dash/assets/images/Background.png")
background_image = pygame.transform.scale(background_image, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

overlay_image = pygame.image.load("PUP Dash/assets/images/pup building block (1).png")
overlay_image = pygame.transform.scale(overlay_image, (1400, 840))
overlay_position = (82, 117)

char_sprite_image = pygame.image.load("PUP Dash/assets/images/piyotttt-1.png.png").convert_alpha()
char_sprite_sheet = spritesheet.SpriteSheet(char_sprite_image)

char_frame_width, char_frame_height = 26, 26
char_scale = 3
char_animation_steps = 4
char_animation_cooldown = 130

char_right_frames = []
char_left_frames = []

for i in range(char_animation_steps):
    image = char_sprite_sheet.get_image(i, char_frame_width, char_frame_height, char_scale, None)
    char_right_frames.append(image)
    char_left_frames.append(pygame.transform.flip(image, True, False))

char_x = VIRTUAL_WIDTH - char_frame_width * char_scale - 50
char_y = 760
char_speed = 8
char_facing_right = False
char_frame = 0
char_last_update = pygame.time.get_ticks()
char_target_x, char_target_y = char_x, char_y

# Added for character pathfinding
char_path = []
CHAR_STATE_IDLE = 0
CHAR_STATE_MOVING_TO_POINT = 1
CHAR_STATE_FOLLOWING_PATH = 2
char_state = CHAR_STATE_IDLE


group_frame_width = 144
group_frame_height = 76
group_scale = 1
group_animation_cooldown = 150
group_animation_steps = 3

group_sprites = {
    "normal": pygame.image.load("PUP Dash/assets/images/normal_stud.png").convert_alpha(),
    "ie": pygame.image.load("PUP Dash/assets/images/ie_stud.png").convert_alpha(),
    "comsoc": pygame.image.load("PUP Dash/assets/images/comsoc_stud.png").convert_alpha(),
    "psych": pygame.image.load("PUP Dash/assets/images/psych_stud.png").convert_alpha(),
    "ptso": pygame.image.load("PUP Dash/assets/images/ptso_stud.png").convert_alpha(),
}

def load_group_frames(sprite_image):
    sheet = spritesheet.SpriteSheet(sprite_image)
    right_frames, left_frames = [], []
    for i in range(group_animation_steps):
        frame = sheet.get_image(i, group_frame_width, group_frame_height, group_scale, None)
        right_frames.append(frame)
        left_frames.append(pygame.transform.flip(frame, True, False))
    return right_frames, left_frames

key_image = pygame.image.load("PUP Dash/assets/images/keyrida.png").convert_alpha()
key_mask = pygame.mask.from_surface(key_image)
key_width, key_height = key_image.get_width(), key_image.get_height()

room_image = pygame.image.load("PUP Dash/assets/images/keyroom.png").convert_alpha()
room_image = pygame.transform.scale(room_image, (1300, 740))
room_position = (88, 202)

bord_image = pygame.image.load("PUP Dash/assets/images/keyborder.png").convert_alpha()
bord_image = pygame.transform.scale(bord_image, (1300, 740))
bord_position = (88, 202)

mid_image = pygame.image.load("PUP Dash/assets/images/gwardiii.png").convert_alpha()
mid_sheet = spritesheet.SpriteSheet(mid_image)
mid_frame_width, mid_frame_height = 50, 97
mid_animation_steps = 2
mid_scale = 1
mid_animation_cooldown = 300

class MidLayer:
    def __init__(self, x, y):
        self.frames = [
            mid_sheet.get_image(i, mid_frame_width, mid_frame_height, mid_scale, None)
            for i in range(mid_animation_steps)
        ]
        self.x = x
        self.y = y
        self.frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self, current_time):
        if current_time - self.last_update > mid_animation_cooldown:
            self.frame = (self.frame + 1) % mid_animation_steps
            self.last_update = current_time

    def draw(self, surface):
        surface.blit(self.frames[self.frame], (self.x, self.y))

sheet = MidLayer(292, 717)

class DoorManager:
    def __init__(self):
        # Define clickable areas for doors
        # Adjust width/height based on your door graphics
        self.door_click_areas = {
            "door1": pygame.Rect(232, 550, 50, 50),
            "door2": pygame.Rect(395, 550, 50, 50),
            "door3": pygame.Rect(1117, 550, 50, 50),
            "door4": pygame.Rect(1278, 550, 50, 50)
        }
        # Define the exact point Pio Pi should stand at for each door
        self.door_target_positions = {
            "door1": (207, 573), # Left side, 2nd floor
            "door2": (370, 573), # Left side, 2nd floor
            "door3": (1082, 573), # Right side, 2nd floor
            "door4": (1243, 573) # Right side, 2nd floor
        }
        # Helper to categorize doors by side for pathing logic
        self.left_doors = ["door1", "door2"]
        self.right_doors = ["door3", "door4"]
        # Helper to quickly check if a door is on a specific side
        self.is_left_door = lambda name: name in self.left_doors
        self.is_right_door = lambda name: name in self.right_doors


    def check_click(self, mouse_pos):
        for door_name, rect in self.door_click_areas.items():
            if rect.collidepoint(mouse_pos):
                return door_name
        return None

door_manager = DoorManager()

class Key:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = True

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.visible = True

    def update(self, current_time):
        pass

    def draw(self, surface):
        if self.visible:
            surface.blit(key_image, (self.x, self.y))

    def check_click(self, mouse_pos):
        if self.visible:
            rel_x = mouse_pos[0] - self.x
            rel_y = mouse_pos[1] - self.y
            if 0 <= rel_x < key_width and 0 <= rel_y < key_height:
                if key_mask.get_at((rel_x, rel_y)):
                    self.visible = False
                    return True
        return False

class StudentGroup:
    def __init__(self, spawn_time, group_type="normal", stop_position=322):
        self.spawn_time = spawn_time
        self.group_type = group_type
        self.right_frames, self.left_frames = load_group_frames(group_sprites[group_type])

        self.state = "waiting"
        self.x = VIRTUAL_WIDTH
        self.y = min(755, VIRTUAL_HEIGHT - group_frame_height)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.direction = "left"
        self.speed = 10
        self.stop_time = None
        self.stop_position = stop_position
        self.key = Key(self.x + 30, self.y - 50)

    def update(self, current_time):
        if self.state == "waiting" and current_time >= self.spawn_time:
            self.state = "entering"
        elif self.state == "entering":
            self.x -= self.speed
            if self.x <= self.stop_position:
                self.x = self.stop_position
                self.state = "stopped"
                self.stop_time = current_time
                self.key.set_position(self.x + 53.65, self.y - 50)
        elif self.state == "stopped" and current_time - self.stop_time >= 20000:
            self.state = "exiting"
            self.direction = "right"
        elif self.state == "exiting":
            self.x += self.speed
            if self.x >= VIRTUAL_WIDTH:
                self.state = "done"

        if self.state in ["entering", "exiting"]:
            if current_time - self.last_update > group_animation_cooldown:
                self.frame = (self.frame + 1) % group_animation_steps
                self.last_update = current_time

        self.key.update(current_time)

    def draw(self, surface):
        if self.state in ["entering", "stopped", "exiting"]:
            frames = self.right_frames if self.direction == "right" else self.left_frames
            surface.blit(frames[self.frame], (self.x, self.y))
            if self.state == "stopped":
                self.key.draw(surface)

    def is_done(self):
        return self.state == "done"

clock = pygame.time.Clock()
FPS = 60
running = True

groups = []
first_group_time = pygame.time.get_ticks() + 4000
next_group_time = first_group_time
current_group = None
group_types = list(group_sprites.keys())

# --- Define common pathing coordinates ---
GROUND_Y = 760
SECOND_FLOOR_Y = 573 # This is the Y-level at the top of the stairs where character lands

# Adjust this Y-coordinate to match the lowest point of the blue curve on the second floor
SECOND_FLOOR_CURVE_Y = 600 # Estimate, adjust based on visual alignment from 1st.png

# Stairs coordinates (match the blue line in the image)
# Left stairs: from (stairs base) to (top of stairs)
STAIRS_LEFT_GROUND_X = 320  # base of left stairs (adjust as needed)
STAIRS_LEFT_SECOND_FLOOR_X = 570  # top of left stairs (adjust as needed)

# Right stairs: from (stairs base) to (top of stairs)
STAIRS_RIGHT_GROUND_X = 1280  # base of right stairs (adjust as needed)
STAIRS_RIGHT_SECOND_FLOOR_X = 1030  # top of right stairs (adjust as needed)

STAIRS_HORIZONTAL_MID_X = (STAIRS_LEFT_SECOND_FLOOR_X + STAIRS_RIGHT_SECOND_FLOOR_X) / 2 # A reference point to decide which stairs to use

# New waypoints for the second-floor curved path (based on 1st.png)
PATH_2F_LEFT_CURVE_X = 650 # Estimate
PATH_2F_MIDDLE_X = 800    # Estimate
PATH_2F_RIGHT_CURVE_X = 950 # Estimate

while running:
    dt = clock.tick(FPS)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Scale mouse position to virtual resolution
            mx, my = pygame.mouse.get_pos()
            scale_x = VIRTUAL_WIDTH / screen_width
            scale_y = VIRTUAL_HEIGHT / screen_height
            mouse_x = int(mx * scale_x)
            mouse_y = int(my * scale_y)

            # --- Movement Logic Start ---
            action_taken = False

            # 1. Check for Door Clicks (Highest Priority)
            clicked_door_name = door_manager.check_click((mouse_x, mouse_y))
            if clicked_door_name:
                char_path = [] # Clear any previous path on new click
                # Always start path from current actual location for smooth transition
                char_path.append((char_x, char_y))

                final_door_target_x, final_door_target_y = door_manager.door_target_positions[clicked_door_name]
                target_door_is_left = door_manager.is_left_door(clicked_door_name)
                
                # Determine character's current floor level
                tolerance = char_speed # Define tolerance for position checks.
                is_on_ground_floor = (char_y >= GROUND_Y - tolerance)
                is_on_second_floor_actual = (char_y <= SECOND_FLOOR_Y + tolerance) # Check for being at the top of stairs level or higher
                is_on_second_floor_path = (char_y <= SECOND_FLOOR_CURVE_Y + tolerance and char_y >= SECOND_FLOOR_Y - tolerance) # Check for being on the curved path level

                # Determine character's current side (left or right of stairs)
                current_side_is_left = char_x < STAIRS_HORIZONTAL_MID_X


                if is_on_ground_floor:
                    # Character is on the ground floor, needs to go up to a door on the second floor
                    if target_door_is_left:
                        char_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y)) # Move to base of left stairs
                        char_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y)) # Then diagonally up left stairs
                    else:  # target_door_is_right
                        char_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y)) # Move to base of right stairs
                        char_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y)) # Then diagonally up right stairs

                    # Now that we're on the second floor level (SECOND_FLOOR_Y), we need to get to the curve path
                    char_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y)) # Move to the target door's X on the curve Y
                    char_path.append((final_door_target_x, final_door_target_y)) # Then adjust to the door's actual Y

                elif is_on_second_floor_actual or is_on_second_floor_path:
                    # Character is already on the second floor (either at stair top or on the path)
                    # We need to guide them along the blue path to the destination door.

                    if target_door_is_left and current_side_is_left:
                        # Character is on the left side and target is on the left side.
                        # Move to the starting point of the left curve, then towards the door.
                        char_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y)) # Ensure at top of stairs
                        char_path.append((PATH_2F_LEFT_CURVE_X, SECOND_FLOOR_CURVE_Y)) # Move to bottom of left curve
                        char_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y)) # Move along curve towards door X
                        char_path.append((final_door_target_x, final_door_target_y)) # Final adjustment to door Y

                    elif not target_door_is_left and not current_side_is_left:
                        # Character is on the right side and target is on the right side.
                        # Move to the starting point of the right curve, then towards the door.
                        char_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y)) # Ensure at top of stairs
                        char_path.append((PATH_2F_RIGHT_CURVE_X, SECOND_FLOOR_CURVE_Y)) # Move to bottom of right curve
                        char_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y)) # Move along curve towards door X
                        char_path.append((final_door_target_x, final_door_target_y)) # Final adjustment to door Y

                    else:
                        # Character needs to cross from left to right or right to left on the second floor path.
                        if current_side_is_left:
                            # Move from left to right side via the curved path
                            char_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y)) # To top of left stairs
                            char_path.append((PATH_2F_LEFT_CURVE_X, SECOND_FLOOR_CURVE_Y)) # To bottom of left curve
                            char_path.append((PATH_2F_MIDDLE_X, SECOND_FLOOR_CURVE_Y)) # To middle of path
                            char_path.append((PATH_2F_RIGHT_CURVE_X, SECOND_FLOOR_CURVE_Y)) # To bottom of right curve
                            char_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y)) # To top of right stairs
                            char_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y)) # Move to target door's X on the curve Y
                            char_path.append((final_door_target_x, final_door_target_y)) # Then adjust to door Y
                        else: # current_side_is_right
                            # Move from right to left side via the curved path
                            char_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y)) # To top of right stairs
                            char_path.append((PATH_2F_RIGHT_CURVE_X, SECOND_FLOOR_CURVE_Y)) # To bottom of right curve
                            char_path.append((PATH_2F_MIDDLE_X, SECOND_FLOOR_CURVE_Y)) # To middle of path
                            char_path.append((PATH_2F_LEFT_CURVE_X, SECOND_FLOOR_CURVE_Y)) # To bottom of left curve
                            char_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y)) # To top of left stairs
                            char_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y)) # Move to target door's X on the curve Y
                            char_path.append((final_door_target_x, final_door_target_y)) # Then adjust to door Y

                # The rest of your path handling for door clicks remains the same
                char_state = CHAR_STATE_FOLLOWING_PATH
                if char_path and abs(char_x - char_path[0][0]) < tolerance and abs(char_y - char_path[0][1]) < tolerance:
                    char_path.pop(0)
                if char_path:
                    char_target_x, char_target_y = char_path.pop(0)
                else:
                    char_state = CHAR_STATE_IDLE
                action_taken = True

            # 2. Check for Key Clicks (Next Priority, only if no door was clicked)
            if not action_taken:
                for group in groups:
                    if group.state == "stopped" and group.key.check_click((mouse_x, mouse_y)):
                        action_taken = True
                        break

            # 3. Check for Ground Clicks (Lowest Priority, only if no door or key was clicked)
            if not action_taken:
                # Only allow clicks on the ground (Y-axis around GROUND_Y)
                if mouse_y >= GROUND_Y - char_frame_height * char_scale / 2:
                    char_path = [] # Clear any previous path on new click
                    char_path.append((char_x, char_y)) # Always start path from current actual location

                    # If currently on the second floor or mid-landing, add path to descend
                    # Check if character is anywhere on the second floor level
                    if char_y <= SECOND_FLOOR_CURVE_Y + tolerance: # Using SECOND_FLOOR_CURVE_Y as the highest point of the "floor"
                        if char_x < STAIRS_HORIZONTAL_MID_X:  # Closer to left stairs
                            # Guide to top of left stairs, then down
                            char_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            char_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                        else:  # Closer to right stairs
                            # Guide to top of right stairs, then down
                            char_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            char_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))

                    # Always add the final ground click point as the last destination
                    char_path.append((mouse_x, GROUND_Y))

                    char_state = CHAR_STATE_FOLLOWING_PATH
                    if char_path and abs(char_x - char_path[0][0]) < tolerance and abs(char_y - char_path[0][1]) < tolerance:
                        char_path.pop(0)
                    if char_path:
                        char_target_x, char_target_y = char_path.pop(0)
                    else:
                        char_state = CHAR_STATE_IDLE
                    action_taken = True
                # Else: click was in a blocked area (above Y=GROUND_Y and not a door/key), do nothing.

            # If no action was taken (no door, key, or valid ground click), Pio Pi stays idle.
            if not action_taken:
                char_state = CHAR_STATE_IDLE
                # char_moving = False # This will be set correctly by the main movement logic

    # --- Character Movement Logic ---
    char_moving = False

    tolerance = char_speed / 2.0 # Keep this tolerance for snapping to points

    if char_state == CHAR_STATE_FOLLOWING_PATH:
        # Check if Pio Pi has reached the current target point
        if abs(char_target_x - char_x) < tolerance and abs(char_target_y - char_y) < tolerance:
            char_x = char_target_x # Snap to target
            char_y = char_target_y

            if char_path: # If there are more points in the path
                char_target_x, char_target_y = char_path.pop(0) # Get the next point
            else: # Path is complete
                char_state = CHAR_STATE_IDLE
                char_moving = False
        else: # Pio Pi is still moving towards the current target point
            char_moving = True
            # Calculate movement towards target
            dist_x = char_target_x - char_x
            dist_y = char_target_y - char_y
            distance = pygame.math.Vector2(dist_x, dist_y).length()

            if distance > 0: # Avoid division by zero
                # Calculate movement step based on speed and direction
                move_x = char_speed * (dist_x / distance)
                move_y = char_speed * (dist_y / distance)

                # Determine facing direction based on current move direction
                if move_x > 0:
                    char_facing_right = True
                elif move_x < 0:
                    char_facing_right = False
                # If move_x is 0 (vertical movement), keep previous facing direction

                # Ensure we don't overshoot the target
                if abs(move_x) > abs(dist_x): move_x = dist_x
                if abs(move_y) > abs(dist_y): move_y = dist_y

                char_x += move_x
                char_y += move_y

    # The CHAR_STATE_MOVING_TO_POINT block is functionally redundant with FOLLOW_PATH for single points
    # It can be safely removed or refactored if we consolidate movement states.
    # For now, let's keep it consistent, but note its limited use.
    elif char_state == CHAR_STATE_MOVING_TO_POINT:
        if abs(char_target_x - char_x) < tolerance and abs(char_target_y - char_y) < tolerance:
            char_x = char_target_x
            char_y = char_target_y
            char_state = CHAR_STATE_IDLE
            char_moving = False
        else:
            char_moving = True
            dist_x = char_target_x - char_x
            dist_y = char_target_y - char_y
            distance = pygame.math.Vector2(dist_x, dist_y).length()

            if distance > 0:
                move_x = char_speed * (dist_x / distance)
                move_y = char_speed * (dist_y / distance)

                if move_x > 0:
                    char_facing_right = True
                elif move_x < 0:
                    char_facing_right = False

                if abs(move_x) > abs(dist_x): move_x = dist_x
                if abs(move_y) > abs(dist_y): move_y = dist_y
                char_x += move_x
                char_y += move_y

    char_x = max(0, min(char_x, VIRTUAL_WIDTH - char_frame_width * char_scale))
    char_y = max(0, min(char_y, VIRTUAL_HEIGHT - char_frame_height * char_scale))

    if char_moving and current_time - char_last_update > char_animation_cooldown:
        char_frame = (char_frame + 1) % char_animation_steps
        char_last_update = current_time
    elif not char_moving:
        char_frame = 0

    for group in groups:
        group.update(current_time)

    groups = [g for g in groups if not g.is_done()]

    if current_group is None or current_group.is_done():
        if current_time >= next_group_time:
            chosen_type = random.choice(group_types)
            current_group = StudentGroup(current_time, group_type=chosen_type, stop_position=322)
            groups.append(current_group)
            next_group_time = current_time + 10000

    # --- DRAW EVERYTHING ON VIRTUAL SURFACE ---
    virtual_surface.blit(background_image, (0, 0))
    virtual_surface.blit(overlay_image, overlay_position)
    virtual_surface.blit(room_image, room_position)

    sheet.update(current_time)
    sheet.draw(virtual_surface)
    virtual_surface.blit(bord_image, bord_position)

    for group in groups:
        group.draw(virtual_surface)

    # Draw character after groups to ensure it's on top
    if char_facing_right:
        virtual_surface.blit(char_right_frames[char_frame], (char_x, char_y))
    else:
        virtual_surface.blit(char_left_frames[char_frame], (char_x, char_y))

    # --- SCALE VIRTUAL SURFACE TO SCREEN ---
    scaled_surface = pygame.transform.smoothscale(virtual_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))
    pygame.display.update()

pygame.quit()
sys.exit()