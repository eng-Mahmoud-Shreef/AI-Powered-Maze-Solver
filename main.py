import pygame
import sys
import time
import tkinter as tk
from threading import Thread
import os
import heapq

# Constants
TILE_SIZE = 40  # Size of each square
FPS = 60  # Frames per second
SIDEBAR_WIDTH = 200  # Width of the sidebar

# Functions
def check_assets():
    """Ensure all required assets exist in the assets folder."""
    required_assets = [
        "assets/wall.png",
        "assets/floor.png",
        "assets/start.png",
        "assets/goal.png",
        "assets/player.png",
        "assets/footprint.png",
        "assets/arrow_right.png",
        "assets/arrow_down.png",
        "assets/arrow_left.png",
        "assets/arrow_up.png",
        "assets/background_music.mp3",
        "assets/click.wav",
        "assets/victory.wav"
    ]

    for asset in required_assets:
        if not os.path.exists(asset):
            print(f"Error: Missing required asset: {asset}")
            sys.exit(1)

def read_maze(file_path):
    with open(file_path, 'r') as file:
        maze = [list(line.strip()) for line in file]
    return maze

def find_position(maze, target):
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == target:
                return row, col
    return None

def open_tkinter_window(selected_algorithm, steps_count, solve_time):
    def tkinter_thread():
        root = tk.Tk()
        root.title("Algorithm Details")

        label_algorithm = tk.Label(root, text=f"Algorithm Used: {selected_algorithm}", font=("Arial", 14))
        label_algorithm.pack(pady=10)

        steps_label = tk.Label(root, text=f"Number of Steps: {steps_count}", font=("Arial", 12))
        steps_label.pack(pady=5)

        time_label = tk.Label(root, text=f"Time Taken: {solve_time:.2f} seconds", font=("Arial", 12))
        time_label.pack(pady=5)

        def close_window():
            root.destroy()

        close_button = tk.Button(root, text="Close", command=close_window, font=("Arial", 12), bg="red", fg="white")
        close_button.pack(pady=20)

        root.mainloop()

    Thread(target=tkinter_thread).start()

def solve_with_dfs(screen, maze, start, goal, textures, player_texture, footprint_texture, screen_width, screen_height, sound_on):
    rows, cols = len(maze), len(maze[0])
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    stack = [(start, [])]
    visited = set()
    start_time = time.time()
    step_count = 0

    while stack:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        (x, y), path = stack.pop()

        if (x, y) in visited:
            continue

        visited.add((x, y))
        step_count += 1

        screen.fill((0, 0, 0))
        draw_maze(screen, maze, textures)
        draw_sidebar(screen, screen_width, screen_height, "DFS", sound_on)
        for step in path:
            screen.blit(footprint_texture, (step[1] * TILE_SIZE, step[0] * TILE_SIZE))
        screen.blit(player_texture, (y * TILE_SIZE, x * TILE_SIZE))
        pygame.display.flip()
        time.sleep(0.05)

        if (x, y) == goal:
            solve_time = time.time() - start_time
            return path + [(x, y)], step_count, solve_time

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] in ('E', 'G', 'S') and (nx, ny) not in visited:
                stack.append(((nx, ny), path + [(x, y)]))

    return None, 0, 0.0

def solve_with_a_star(screen, maze, start, goal, textures, player_texture, footprint_texture, screen_width, screen_height, sound_on):
    rows, cols = len(maze), len(maze[0])
    open_set = []
    heapq.heappush(open_set, (0, start, [], 0))  # (priority, current_position, path, cost)
    visited = set()
    step_count = 0
    start_time = time.time()

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        _, (x, y), path, cost = heapq.heappop(open_set)

        if (x, y) in visited:
            continue
        visited.add((x, y))
        step_count += 1

        screen.fill((0, 0, 0))
        draw_maze(screen, maze, textures)
        draw_sidebar(screen, screen_width, screen_height, "A*", sound_on)
        for step in path:
            screen.blit(footprint_texture, (step[1] * TILE_SIZE, step[0] * TILE_SIZE))
        screen.blit(player_texture, (y * TILE_SIZE, x * TILE_SIZE))
        pygame.display.flip()
        pygame.event.pump()
        time.sleep(0.05)

        if (x, y) == goal:
            solve_time = time.time() - start_time
            return path + [(x, y)], step_count, solve_time

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] in ('E', 'G', 'S') and (nx, ny) not in visited:
                new_cost = cost + 1 + abs(nx - goal[0]) + abs(ny - goal[1])
                priority = new_cost
                heapq.heappush(open_set, (priority, (nx, ny), path + [(x, y)], new_cost))

    return None, 0, 0.0

def highlight_path_with_arrows(maze, path, textures):
    arrow_textures = {
        (0, 1): pygame.image.load("assets/arrow_right.png"),
        (1, 0): pygame.image.load("assets/arrow_down.png"),
        (0, -1): pygame.image.load("assets/arrow_left.png"),
        (-1, 0): pygame.image.load("assets/arrow_up.png")
    }

    for key in arrow_textures:
        arrow_textures[key] = pygame.transform.scale(arrow_textures[key], (TILE_SIZE, TILE_SIZE))

    for i in range(len(path) - 1):
        x, y = path[i]
        nx, ny = path[i + 1]
        direction = (nx - x, ny - y)
        if direction in arrow_textures:
            maze[x][y] = arrow_textures[direction]

def load_textures():
    textures = {
        'X': pygame.image.load("assets/wall.png"),
        'E': pygame.image.load("assets/floor.png"),
        'S': pygame.image.load("assets/start.png"),
        'G': pygame.image.load("assets/goal.png")
    }
    for key in textures:
        textures[key] = pygame.transform.scale(textures[key], (TILE_SIZE, TILE_SIZE))
    return textures

def draw_maze(screen, maze, textures):
    rows, cols = len(maze), len(maze[0])
    for row in range(rows):
        for col in range(cols):
            tile = maze[row][col]
            if isinstance(tile, pygame.Surface):
                screen.blit(tile, (col * TILE_SIZE, row * TILE_SIZE))
            elif tile in textures:
                screen.blit(textures[tile], (col * TILE_SIZE, row * TILE_SIZE))

def draw_sidebar(screen, width, height, selected_algorithm, sound_on):
    pygame.draw.rect(screen, (50, 50, 50), (width - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, height))

    font = pygame.font.Font(None, 36)
    title = font.render("Maze Solver", True, (255, 255, 255))
    screen.blit(title, (width - SIDEBAR_WIDTH + 20, 20))

    restart_rect = pygame.Rect(width - SIDEBAR_WIDTH + 20, 120, 160, 50)
    pygame.draw.rect(screen, (100, 200, 100), restart_rect)
    restart_text = font.render("Restart", True, (0, 0, 0))
    screen.blit(restart_text, (restart_rect.x + (restart_rect.width - restart_text.get_width()) // 2,
                               restart_rect.y + (restart_rect.height - restart_text.get_height()) // 2))

    solve_rect = pygame.Rect(width - SIDEBAR_WIDTH + 20, 200, 160, 50)
    pygame.draw.rect(screen, (200, 100, 100), solve_rect)
    solve_text = font.render("Solve", True, (0, 0, 0))
    screen.blit(solve_text, (solve_rect.x + (solve_rect.width - solve_text.get_width()) // 2,
                             solve_rect.y + (solve_rect.height - solve_text.get_height()) // 2))

    dfs_rect = pygame.Rect(width - SIDEBAR_WIDTH + 20, 300, 160, 50)
    a_star_rect = pygame.Rect(width - SIDEBAR_WIDTH + 20, 370, 160, 50)

    if selected_algorithm == "DFS":
        pygame.draw.rect(screen, (0, 150, 255), dfs_rect)
        pygame.draw.rect(screen, (200, 200, 200), a_star_rect)
    else:
        pygame.draw.rect(screen, (200, 200, 200), dfs_rect)
        pygame.draw.rect(screen, (0, 150, 255), a_star_rect)

    dfs_text = font.render("DFS", True, (0, 0, 0))
    a_star_text = font.render("A*", True, (0, 0, 0))
    screen.blit(dfs_text, (dfs_rect.x + (dfs_rect.width - dfs_text.get_width()) // 2,
                           dfs_rect.y + (dfs_rect.height - dfs_text.get_height()) // 2))
    screen.blit(a_star_text, (a_star_rect.x + (a_star_rect.width - a_star_text.get_width()) // 2,
                              a_star_rect.y + (a_star_rect.height - a_star_text.get_height()) // 2))

    sound_toggle_rect = pygame.Rect(width - SIDEBAR_WIDTH + 20, height - 80, 160, 50)
    pygame.draw.rect(screen, (200, 200, 0) if sound_on else (100, 100, 100), sound_toggle_rect)
    sound_text = font.render("Sound: ON" if sound_on else "Sound: OFF", True, (0, 0, 0))
    screen.blit(sound_text, (sound_toggle_rect.x + (sound_toggle_rect.width - sound_text.get_width()) // 2,
                             sound_toggle_rect.y + (sound_toggle_rect.height - sound_text.get_height()) // 2))

    developed_by_text = font.render("Developed by:", True, (200, 200, 200))
    developer_name = font.render("Eng Mahmoud Shreef", True, (200, 200, 200))
    screen.blit(developed_by_text, (width - SIDEBAR_WIDTH + 20, height - 160))
    screen.blit(developer_name, (width - SIDEBAR_WIDTH + 20, height - 130))

    return restart_rect, solve_rect, dfs_rect, a_star_rect, sound_toggle_rect

def victory_message(screen, screen_width, screen_height):
    font = pygame.font.Font(None, 72)
    message = font.render("Congratulations!", True, (0, 255, 0))
    sub_message = font.render("You solved the maze!", True, (0, 255, 0))
    screen.fill((0, 0, 0))
    screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 3))
    screen.blit(sub_message, (screen_width // 2 - sub_message.get_width() // 2, screen_height // 2))
    pygame.display.flip()
    pygame.time.delay(9500)

def restart_game():
    maze = read_maze("map.txt")
    start_pos = find_position(maze, 'S')
    goal_pos = find_position(maze, 'G')
    return maze, start_pos, goal_pos

def main():
    check_assets()  # Ensure all assets exist before starting the game
    pygame.init()

    maze = read_maze("map.txt")
    rows, cols = len(maze), len(maze[0])

    screen_width = cols * TILE_SIZE + SIDEBAR_WIDTH
    screen_height = rows * TILE_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Maze Solver")

    textures = load_textures()
    player_texture = pygame.image.load("assets/player.png")
    player_texture = pygame.transform.scale(player_texture, (TILE_SIZE, TILE_SIZE))
    footprint_texture = pygame.image.load("assets/footprint.png")
    footprint_texture = pygame.transform.scale(footprint_texture, (TILE_SIZE, TILE_SIZE))

    pygame.mixer.init()
    pygame.mixer.music.load("assets/background_music.mp3")
    pygame.mixer.music.play(-1)

    click_sound = pygame.mixer.Sound("assets/click.wav")
    victory_sound = pygame.mixer.Sound("assets/victory.wav")

    maze, start_pos, goal_pos = restart_game()
    player_pos = list(start_pos)
    running = True
    solving = False
    selected_algorithm = "DFS"
    won = False
    sound_on = True

    while running:
        restart_rect, solve_rect, dfs_rect, a_star_rect, sound_toggle_rect = draw_sidebar(screen, screen_width, screen_height, selected_algorithm, sound_on)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if sound_toggle_rect.collidepoint(event.pos):
                    sound_on = not sound_on
                    if sound_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                    if sound_on:
                        click_sound.play()
                elif restart_rect.collidepoint(event.pos):
                    if sound_on:
                        click_sound.play()
                    maze, start_pos, goal_pos = restart_game()
                    player_pos = list(start_pos)
                    solving = False
                    won = False
                elif solve_rect.collidepoint(event.pos):
                    if sound_on:
                        click_sound.play()
                    solving = True
                elif dfs_rect.collidepoint(event.pos):
                    if sound_on:
                        click_sound.play()
                    selected_algorithm = "DFS"
                elif a_star_rect.collidepoint(event.pos):
                    if sound_on:
                        click_sound.play()
                    selected_algorithm = "A*"
            elif event.type == pygame.KEYDOWN and not solving:
                if event.key == pygame.K_UP and maze[player_pos[0] - 1][player_pos[1]] in ('E', 'G', 'S'):
                    player_pos[0] -= 1
                elif event.key == pygame.K_DOWN and maze[player_pos[0] + 1][player_pos[1]] in ('E', 'G', 'S'):
                    player_pos[0] += 1
                elif event.key == pygame.K_LEFT and maze[player_pos[0]][player_pos[1] - 1] in ('E', 'G', 'S'):
                    player_pos[1] -= 1
                elif event.key == pygame.K_RIGHT and maze[player_pos[0]][player_pos[1] + 1] in ('E', 'G', 'S'):
                    player_pos[1] += 1

        # Check if the player manually reaches the goal
        if tuple(player_pos) == goal_pos and not won:
            if sound_on:
                victory_sound.play()
            victory_message(screen, screen_width, screen_height)
            won = True

        if solving and not won:
            if selected_algorithm == "DFS":
                path, steps_count, solve_time = solve_with_dfs(screen, maze, tuple(player_pos), goal_pos, textures, player_texture, footprint_texture, screen_width, screen_height, sound_on)
            elif selected_algorithm == "A*":
                path, steps_count, solve_time = solve_with_a_star(screen, maze, tuple(player_pos), goal_pos, textures, player_texture, footprint_texture, screen_width, screen_height, sound_on)

            if path:
                highlight_path_with_arrows(maze, path + [goal_pos], textures)
                if sound_on:
                    victory_sound.play()
                victory_message(screen, screen_width, screen_height)
                open_tkinter_window(selected_algorithm, steps_count, solve_time)
                won = True

        screen.fill((0, 0, 0))
        draw_maze(screen, maze, textures)
        draw_sidebar(screen, screen_width, screen_height, selected_algorithm, sound_on)
        screen.blit(player_texture, (player_pos[1] * TILE_SIZE, player_pos[0] * TILE_SIZE))
        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
