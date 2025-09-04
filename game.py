import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 32
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
CAVE_COLOR = (40, 30, 20)
PLAYER_COLOR = (200, 150, 100)
AMBER_COLOR = (255, 191, 0)
HOOK_COLOR = (150, 100, 50)
ROCK_COLOR = (80, 60, 40)
GROUND_COLOR = (60, 45, 30)
POISON_COLOR = (100, 255, 100)
EXIT_COLOR = (255, 255, 0)
CRAB_COLOR = (200, 100, 100)

class Bat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 1  # 1 = moving down, -1 = moving up
        self.ceiling_y = GRID_SIZE
        self.floor_y = (SCREEN_HEIGHT // GRID_SIZE - 2) * GRID_SIZE
    
    def update(self):
        # Move one grid space per tick
        if self.direction == 1:  # Moving down
            self.y += GRID_SIZE
            if self.y >= self.floor_y:
                self.direction = -1  # Switch to moving up
        else:  # Moving up
            self.y -= GRID_SIZE
            if self.y <= self.ceiling_y:
                self.direction = 1  # Switch to moving down

class AmberCrab:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.direction = 1  # 1 = moving right, -1 = moving left
        self.start_x = x
        self.move_range = GRID_SIZE * 4  # Move 4 grid spaces back and forth
    
    def update(self):
        if self.alive:
            # Move one grid space per tick
            if self.direction == 1:  # Moving right
                self.x += GRID_SIZE
                if self.x >= self.start_x + self.move_range:
                    self.direction = -1  # Switch to moving left
            else:  # Moving left
                self.x -= GRID_SIZE
                if self.x <= self.start_x:
                    self.direction = 1  # Switch to moving right

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.grappling = False
        self.hook_target_x = 0
        self.hook_target_y = 0
        self.grapple_ticks_remaining = 0
        self.falling = False
        self.fall_ticks_remaining = 0
        self.fall_delay = 0
        self.just_moved = False
        
    def update(self, world):
        if self.grappling:
            # Grid-based grappling - move one grid space every 3 ticks (slower)
            if self.grapple_ticks_remaining > 0:
                # Only move every 3 ticks
                if self.grapple_ticks_remaining % 3 == 0:
                    dx = self.hook_target_x - self.x
                    dy = self.hook_target_y - self.y
                    
                    # Move one grid space towards target
                    if abs(dx) > abs(dy):
                        # Move horizontally
                        if dx > 0:
                            self.x += GRID_SIZE
                        else:
                            self.x -= GRID_SIZE
                    else:
                        # Move vertically
                        if dy > 0:
                            self.y += GRID_SIZE
                        else:
                            self.y -= GRID_SIZE
                
                self.grapple_ticks_remaining -= 1
            else:
                # Grappling complete
                self.stop_grappling()
        elif self.falling:
            # Grid-based falling with delay - move one grid space down per tick
            if self.fall_ticks_remaining > 0:
                if self.fall_delay <= 0:
                    # Time to move down one space
                    self.y += GRID_SIZE
                    self.fall_ticks_remaining -= 1
                    self.fall_delay = 3  # Wait 3 frames before next fall
                else:
                    # Still waiting
                    self.fall_delay -= 1
            else:
                # Falling complete
                self.falling = False
    
    def moved_this_tick(self):
        # Check if player moved a full grid space this update
        return (self.grappling and self.grapple_ticks_remaining > 0 and self.grapple_ticks_remaining % 3 == 0) or (self.falling and self.fall_ticks_remaining > 0 and self.fall_delay <= 0) or self.just_moved
    
    def move_left(self, world, game):
        # Check if can move left
        new_x = self.x - GRID_SIZE
        if self.can_move_to(new_x, self.y, world):
            self.x = new_x
            self.just_moved = True  # Mark that player moved
            # Check if player should fall after moving
            self.start_falling(world)
            return True
        return False
    
    def move_right(self, world, game):
        # Check if can move right
        new_x = self.x + GRID_SIZE
        if self.can_move_to(new_x, self.y, world):
            self.x = new_x
            self.just_moved = True  # Mark that player moved
            # Check if player should fall after moving
            self.start_falling(world)
            return True
        return False
    
    def jump(self, world, game):
        # Check if can jump up
        new_y = self.y - GRID_SIZE
        if self.can_move_to(self.x, new_y, world):
            self.y = new_y
            self.just_moved = True  # Mark that player moved
            # Check if player should fall after jumping
            self.start_falling(world)
            return True
        return False
    
    def can_move_to(self, x, y, world):
        # Check if position is valid (not inside walls)
        grid_x = int(x // GRID_SIZE)
        grid_y = int(y // GRID_SIZE)
        
        # Check bounds
        if grid_x < 0 or grid_x >= len(world[0]) or grid_y < 0 or grid_y >= len(world):
            return False
        
        # Check if position is solid
        return world[grid_y][grid_x] == 0  # 0 = air, 1 = solid
    
    def start_falling(self, world):
        # Calculate how many spaces the player can fall
        fall_distance = 0
        current_y = self.y + GRID_SIZE  # Start checking one space below
        
        while self.can_move_to(self.x, current_y, world):
            fall_distance += 1
            current_y += GRID_SIZE
        
        if fall_distance > 0:
            self.falling = True
            self.fall_ticks_remaining = fall_distance
            return True
        return False
    
    
    
    def start_grappling(self, target_x, target_y):
        self.grappling = True
        self.hook_target_x = target_x
        self.hook_target_y = target_y
        dx = target_x - self.x
        dy = target_y - self.y
        self.hook_length = math.sqrt(dx*dx + dy*dy)
        
        # Calculate distance in grid spaces
        grid_distance = max(abs(dx // GRID_SIZE), abs(dy // GRID_SIZE))
        self.grapple_ticks_remaining = grid_distance * 3  # Make grappling 3x slower
    
    def stop_grappling(self):
        self.grappling = False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Grapplecore - Cave Adventure")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Create cave level
        self.world = self.create_cave_level()
        
        # Create player (spawn in air so they can fall)
        self.player = Player(GRID_SIZE * 2, GRID_SIZE * 5)
        
        # Create bat
        self.bat = Bat(GRID_SIZE * 15, GRID_SIZE)
        
        # Game state
        self.amber_count = 0
        self.turn_based = True
        self.waiting_for_input = True
        self.game_over = False
        self.fade_alpha = 0
        self.fade_speed = 5
        self.fading_out = False
        self.fading_in = False
        
        # Create amber collectibles (empty - only get amber from crabs)
        self.amber_positions = []
        
        # Create poison clouds
        self.poison_clouds = [
            (GRID_SIZE * 28, GRID_SIZE * 18),  # Under the exit
            (GRID_SIZE * 12, GRID_SIZE * 18),  # On ground
            (GRID_SIZE * 6, GRID_SIZE * 16)    # On first platform
        ]
        
        # Create exit
        self.exit_x = (SCREEN_WIDTH // GRID_SIZE - 2) * GRID_SIZE  # Top right
        self.exit_y = GRID_SIZE * 2
        
        # Create amber crabs (on ground level)
        ground_y = (SCREEN_HEIGHT // GRID_SIZE - 3) * GRID_SIZE  # Ground level
        self.amber_crabs = [
            AmberCrab(GRID_SIZE * 5, ground_y),   # On ground, left side
            AmberCrab(GRID_SIZE * 15, ground_y),  # On ground, middle
            AmberCrab(GRID_SIZE * 25, ground_y)   # On ground, right side
        ]
        
        
        # Input handling
        self.keys_pressed = set()
    
    def create_cave_level(self):
        # Create a simple cave level
        world = []
        height = SCREEN_HEIGHT // GRID_SIZE
        width = SCREEN_WIDTH // GRID_SIZE
        
        # Initialize empty world
        for y in range(height):
            row = []
            for x in range(width):
                row.append(0)  # 0 = air, 1 = solid
            world.append(row)
        
        # Create ground - just a simple floor
        for x in range(width):
            world[height - 2][x] = 1  # Ground level
        
        # Create simple walls - just left and right boundaries
        for y in range(height - 2):
            world[y][0] = 1  # Left wall
            world[y][width - 1] = 1  # Right wall
        
        # Create ceiling - just top boundary
        for x in range(width):
            world[0][x] = 1  # Ceiling
        
        # Add just a few simple platforms for testing
        # Platform 1 - easy to reach
        for x in range(8, 12):
            world[height - 6][x] = 1
        
        # Platform 2 - slightly higher
        for x in range(20, 24):
            world[height - 8][x] = 1
        
        # Platform 3 - requires grappling
        for x in range(15, 18):
            world[height - 12][x] = 1
        
        return world
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.turn_based and self.waiting_for_input and not self.game_over:
                    # Movement controls (A/W/D keys) - grid-based
                    if event.key == pygame.K_a:
                        if self.player.move_left(self.world, self):
                            self.waiting_for_input = False
                    elif event.key == pygame.K_d:
                        if self.player.move_right(self.world, self):
                            self.waiting_for_input = False
                    elif event.key == pygame.K_w:
                        if self.player.jump(self.world, self):
                            self.waiting_for_input = False
                    # Grappling hook controls (Arrow keys) - only cardinal directions
                    elif event.key == pygame.K_LEFT:
                        # Grappling hook left - find nearest solid block or crab
                        target_x, target_y = self.find_grapple_target(self.player.x, self.player.y, -1, 0)
                        if target_x is not None:
                            self.player.start_grappling(target_x, target_y)
                            self.waiting_for_input = False
                        # If target_x is None, we hit a crab and turn ends immediately
                    elif event.key == pygame.K_RIGHT:
                        # Grappling hook right - find nearest solid block or crab
                        target_x, target_y = self.find_grapple_target(self.player.x, self.player.y, 1, 0)
                        if target_x is not None:
                            self.player.start_grappling(target_x, target_y)
                            self.waiting_for_input = False
                        # If target_x is None, we hit a crab and turn ends immediately
                    elif event.key == pygame.K_UP:
                        # Grappling hook up - find nearest solid block or crab
                        target_x, target_y = self.find_grapple_target(self.player.x, self.player.y, 0, -1)
                        if target_x is not None:
                            self.player.start_grappling(target_x, target_y)
                            self.waiting_for_input = False
                        # If target_x is None, we hit a crab and turn ends immediately
        
        return True
    
    def find_grapple_target(self, start_x, start_y, dx, dy):
        # Find the nearest solid block in the given direction
        current_x = start_x
        current_y = start_y
        
        while True:
            # Move one grid space in the direction
            current_x += dx * GRID_SIZE
            current_y += dy * GRID_SIZE
            
            # Check for crab collision first
            for crab in self.amber_crabs:
                if crab.alive:
                    crab_rect = pygame.Rect(crab.x, crab.y, GRID_SIZE, GRID_SIZE)
                    hook_rect = pygame.Rect(current_x, current_y, GRID_SIZE, GRID_SIZE)
                    if hook_rect.colliderect(crab_rect):
                        # Hit a crab - kill it and return None to indicate no movement
                        crab.alive = False
                        self.amber_count += 1
                        return None, None
            
            # Check bounds
            grid_x = int(current_x // GRID_SIZE)
            grid_y = int(current_y // GRID_SIZE)
            
            if grid_x < 0 or grid_x >= len(self.world[0]) or grid_y < 0 or grid_y >= len(self.world):
                # Hit boundary, return the last valid position
                return current_x - dx * GRID_SIZE, current_y - dy * GRID_SIZE
            
            # Check if this position is solid
            if self.world[grid_y][grid_x] == 1:  # Solid block found
                # Return the position one space before the solid block (so player lands next to it)
                return current_x - dx * GRID_SIZE, current_y - dy * GRID_SIZE
    
    
    def update(self):
        if not self.waiting_for_input and not self.game_over:
            self.player.update(self.world)
            
            # Check if player moved a full grid space (for bat and crab synchronization)
            if self.player.moved_this_tick():
                self.bat.update()  # Move bat when player moves one grid space
                # Move all alive crabs
                for crab in self.amber_crabs:
                    crab.update()
                self.player.just_moved = False  # Reset the flag
                
                # Check poison cloud collision (only when player actually moves)
                player_rect = pygame.Rect(self.player.x, self.player.y, GRID_SIZE, GRID_SIZE)
                for poison_x, poison_y in self.poison_clouds:
                    poison_rect = pygame.Rect(poison_x, poison_y, GRID_SIZE, GRID_SIZE)
                    if player_rect.colliderect(poison_rect):
                        if self.amber_count > 0:
                            self.amber_count -= 1
                            # Don't die if we have amber - just lose one amber per movement
                        else:
                            # Player dies if they have no amber
                            self.game_over = True
                            self.fading_out = True
                        break
            
            # Check amber collection (no scattered ambers - only from crabs)
            
            # Create player rectangle for collision detection
            player_rect = pygame.Rect(self.player.x, self.player.y, GRID_SIZE, GRID_SIZE)
            
            
            
            # Check exit collision (victory)
            exit_rect = pygame.Rect(self.exit_x, self.exit_y, GRID_SIZE, GRID_SIZE)
            if player_rect.colliderect(exit_rect):
                # Player wins - restart game
                self.restart_game()
                self.fading_in = True
            
            # Check crab collision (game over)
            for crab in self.amber_crabs:
                if crab.alive:
                    crab_rect = pygame.Rect(crab.x, crab.y, GRID_SIZE, GRID_SIZE)
                    if player_rect.colliderect(crab_rect):
                        self.game_over = True
                        self.fading_out = True
                        break
            
            # Check bat collision (game over)
            bat_rect = pygame.Rect(self.bat.x, self.bat.y, GRID_SIZE, GRID_SIZE)
            if player_rect.colliderect(bat_rect):
                self.game_over = True
                self.fading_out = True
            
            # Check if turn is complete
            if self.player.grappling or self.player.falling:
                # Still grappling or falling, continue
                pass
            else:
                # Player has completed their move
                self.waiting_for_input = True
        
        # Handle fade transitions
        if self.fading_out:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fading_out = False
                self.restart_game()
                self.fading_in = True
        elif self.fading_in:
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading_in = False
    
    def restart_game(self):
        # Reset game state
        self.game_over = False
        self.waiting_for_input = True
        self.amber_count = 0
        
        # Reset player position
        self.player = Player(GRID_SIZE * 2, GRID_SIZE * 5)
        
        # Reset bat position
        self.bat = Bat(GRID_SIZE * 15, GRID_SIZE)
        
        # Reset amber positions
        self.amber_positions = [
            (GRID_SIZE * 5, GRID_SIZE * 18),  # On ground, easy to reach
            (GRID_SIZE * 10, GRID_SIZE * 16), # On first platform
            (GRID_SIZE * 22, GRID_SIZE * 14), # On second platform
            (GRID_SIZE * 16, GRID_SIZE * 10), # On high platform (needs grappling)
            (GRID_SIZE * 25, GRID_SIZE * 18)  # On ground, far right
        ]
        
        # Reset poison clouds
        self.poison_clouds = [
            (GRID_SIZE * 28, GRID_SIZE * 18),  # Under the exit
            (GRID_SIZE * 12, GRID_SIZE * 18),  # On ground
            (GRID_SIZE * 6, GRID_SIZE * 16)    # On first platform
        ]
        
        # Reset exit
        self.exit_x = (SCREEN_WIDTH // GRID_SIZE - 2) * GRID_SIZE  # Top right
        self.exit_y = GRID_SIZE * 2
        
        # Reset amber crabs (on ground level)
        ground_y = (SCREEN_HEIGHT // GRID_SIZE - 3) * GRID_SIZE  # Ground level
        self.amber_crabs = [
            AmberCrab(GRID_SIZE * 5, ground_y),   # On ground, left side
            AmberCrab(GRID_SIZE * 15, ground_y),  # On ground, middle
            AmberCrab(GRID_SIZE * 25, ground_y)   # On ground, right side
        ]
        
    
    def draw(self):
        self.screen.fill(CAVE_COLOR)
        
        # Draw world
        for y in range(len(self.world)):
            for x in range(len(self.world[0])):
                if self.world[y][x] == 1:
                    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(self.screen, ROCK_COLOR, rect)
                    pygame.draw.rect(self.screen, (100, 80, 60), rect, 2)
        
        # Draw player
        player_rect = pygame.Rect(self.player.x, self.player.y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, PLAYER_COLOR, player_rect)
        pygame.draw.rect(self.screen, (255, 200, 150), player_rect, 2)
        
        # Draw grappling hook
        if self.player.grappling:
            pygame.draw.line(self.screen, HOOK_COLOR, 
                           (self.player.x + GRID_SIZE//2, self.player.y + GRID_SIZE//2),
                           (self.player.hook_target_x, self.player.hook_target_y), 3)
        
        # Draw amber collectibles (none - only get amber from crabs)
        
        # Draw poison clouds
        for poison_x, poison_y in self.poison_clouds:
            poison_rect = pygame.Rect(poison_x + 2, poison_y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
            pygame.draw.ellipse(self.screen, POISON_COLOR, poison_rect)
            pygame.draw.ellipse(self.screen, (50, 200, 50), poison_rect, 2)
        
        # Draw exit
        exit_rect = pygame.Rect(self.exit_x, self.exit_y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, EXIT_COLOR, exit_rect)
        pygame.draw.rect(self.screen, (200, 200, 0), exit_rect, 3)
        
        # Draw amber crabs
        for crab in self.amber_crabs:
            if crab.alive:
                crab_rect = pygame.Rect(crab.x + 2, crab.y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
                pygame.draw.ellipse(self.screen, CRAB_COLOR, crab_rect)
                pygame.draw.ellipse(self.screen, (150, 50, 50), crab_rect, 2)
        
        
        # Draw bat
        bat_rect = pygame.Rect(self.bat.x + 2, self.bat.y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
        pygame.draw.ellipse(self.screen, (60, 60, 60), bat_rect)  # Dark gray bat
        pygame.draw.ellipse(self.screen, (100, 100, 100), bat_rect, 2)  # Light gray outline
        
        # Draw collected amber icons
        for i in range(self.amber_count):
            amber_x = 10 + (i * (GRID_SIZE + 5))  # Space them out horizontally
            amber_y = 10
            amber_rect = pygame.Rect(amber_x, amber_y, GRID_SIZE - 4, GRID_SIZE - 4)
            pygame.draw.ellipse(self.screen, AMBER_COLOR, amber_rect)
            pygame.draw.ellipse(self.screen, (255, 215, 0), amber_rect, 2)
        
        
        # Draw fade overlay
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.set_alpha(self.fade_alpha)
            fade_surface.fill((0, 0, 0))  # Black fade
            self.screen.blit(fade_surface, (0, 0))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
