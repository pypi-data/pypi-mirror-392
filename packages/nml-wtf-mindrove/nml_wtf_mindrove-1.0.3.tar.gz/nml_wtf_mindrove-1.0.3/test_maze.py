from nml.maze_generator import MazeGenerator

if __name__ == "__main__":
    width, height = 21, 21  # Maze dimensions (odd numbers work best)
    maze_gen = MazeGenerator(width, height)
    maze_layout = maze_gen.generate_maze()
    maze_gen.display_maze()