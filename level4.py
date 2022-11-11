import glob
import numpy as np
from typing import IO
from time import sleep

def main():
    inputs = glob.glob('data/level4/*.in')
    for inputfile in inputs:
        
        if 'example' in inputfile:
            continue
        
        print(inputfile)

        solution = solve(inputfile)
        if solution:
            with open(inputfile.replace('in', 'out'), 'w') as f:
                f.write(solution)
        else:
            print('no solution found')
        print(len(solution))
    
    return

def solve(inputfile: str) -> str:
    with open(inputfile, 'r') as f:
        k, board, px, py, maxmoves = read_data(f)
    
    grid = Grid(board, k)
    pacman = PacMan(px, py)
    grid.grid[px, py] = '.'
    ghosts = []
    for x in range(k):
        for y in range(k):
            if grid.grid[x, y] == 'G':
                ghosts.append(Ghost(x, y))
                grid.grid[x, y] = '.'
    grid.add_ghosts(ghosts)
    
    budget = maxmoves + 1
    result = semi_random_search(grid, pacman, budget, visual=False)
    return result


class Player:
    def __init__(self, x: int, y: int, moves: str = ''):
        self.name = ' '
        self.x = x
        self.y = y
        self.moves = moves
        self.x_bkp, self.y_bkp = x, y
    
    def get_new_pos(self, move: str) -> tuple[int, int]:
        x, y = self.x, self.y
        if move == 'U':
            x -= 1
        elif move == 'D':
            x += 1
        elif move == 'L':
            y -= 1
        elif move == 'R':
            y += 1
        return x, y
    
    def set_pos(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    
    def reset(self) -> None:
        self.x, self.y = self.x_bkp, self.y_bkp

class PacMan(Player):
    def __init__(self, x: int, y: int, moves: str = ''):
        super().__init__(x, y, moves)
        self.name = 'P'
        self.coins_collected = 0
        self.alive = True
        self.history = ''

class Ghost(Player):
    def __init__(self, x: int, y: int, moves: str = ''):
        super().__init__(x, y, moves)
        self.name = 'G'

class Grid:
    def __init__(self, input_string: str, k: int):
        self.grid = np.array(list(input_string)).reshape(k, input_string.count('\n') + 1)
        self.grid = np.delete(self.grid, -1, axis=1)
        self.coins_left = np.count_nonzero(self.grid == 'C')
        self.backup_grid = self.grid.copy()
    
    def add_ghosts(self, ghosts: list[Ghost]) -> None:
        self.ghosts = ghosts
    
    def reset(self) -> None:
        self.grid = self.backup_grid.copy()
    
    def get_legal_moves(self, player: Player) -> list[tuple[int, int]]:
        legal_moves = {'U', 'D', 'L', 'R'}
        for move in ['U', 'D', 'L', 'R']:
            x, y = player.get_new_pos(move)
            for ghost in self.ghosts:
                if ghost.x == x and ghost.y == y:
                    legal_moves.remove(move)
            if self.grid[x, y] == 'W':
                legal_moves.remove(move)
        return legal_moves

    def update_position(self, player: Player, move: str):
        prev_x, prev_y = player.x, player.y
        x, y = player.get_new_pos(move)
        if isinstance(player, PacMan):
            # check wall
            if self.grid[x, y] == 'W':
                player.alive = False
            # check against ghost positions
            for ghost in self.ghosts:
                if ghost.x == x and ghost.y == y:
                    player.alive = False
                    break
            else:
                if self.grid[x, y] == 'C':
                    self.grid[x, y] = '.'
                    player.coins_collected += 1
                    self.coins_left -= 1
                player.set_pos(x, y)
        elif isinstance(player, Ghost):
            if self.grid[x, y] == 'W':
                player.set_pos(prev_x, prev_y)
                return
            player.set_pos(x, y)
        player.history += move
    
    def print_state(self, px: int, py: int) -> None:
        sleep(0.05)
        grid = self.grid.copy()
        # make p red
        grid[px, py] = 'P'
        for ghost in self.ghosts:
            grid[ghost.x, ghost.y] = 'G'
        d = {
            'W': '\033[40m  \033[0m',
            '.': '\033[47m  \033[0m',
            'P': '\033[41m  \033[0m',
            'G': '\033[46m  \033[0m',
            'o': '\033[42m  \033[0m',
            'C': '\033[43m  \033[0m'
        }
        for k, v in d.items():
            grid = np.where(grid == k, v, grid)
        grid_str = ''
        for row in grid:
            grid_str += ''.join(row)
            grid_str += '\n'
        print(grid_str)
        print('\033[0m---')

def read_data(f: IO) -> tuple[int, str, int, int, int]:
    k = int(f.readline())
    board = ""
    for i in range(k):
        board += f.readline()
    ppos = f.readline().split(' ')
    px, py = int(ppos[0]) - 1, int(ppos[1]) - 1
    maxmoves = int(f.readline())
    return k, board, px, py, maxmoves
    
def random_search(grid: Grid, pacman: PacMan, budget, visual: bool = False) -> str:
    if visual:
        grid.print_state(pacman.x, pacman.y)
    while grid.coins_left and budget:
        # get random move
        legal_moves = grid.get_legal_moves(pacman)
        move = np.random.choice(list(legal_moves))
        # move pacman
        grid.update_position(pacman, move)
        if visual:
            grid.print_state(pacman.x, pacman.y)
        if not pacman.alive:
            grid.reset()
            pacman.reset()
            print('died', '\n'*10)
        budget -= 1
    
    if budget:
        return pacman.history
    else:
        return ''

def opposite(move: str) -> str:
    return {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}[move]

def semi_random_search(grid: Grid, pacman: PacMan, budget, visual: bool = False) -> str:
    if visual:
        grid.print_state(pacman.x, pacman.y)
    prev_move = 'U'
    while grid.coins_left and budget:
        # get random move
        legal_moves = grid.get_legal_moves(pacman)
        if opposite(prev_move) in legal_moves and len(legal_moves) > 1:
            legal_moves.remove(opposite(prev_move))
        move = np.random.choice(list(legal_moves))
        # move pacman
        grid.update_position(pacman, move)
        prev_move = move
        if visual:
            grid.print_state(pacman.x, pacman.y)
        if not pacman.alive:
            grid.reset()
            pacman.reset()
            print('died', '\n'*10)
        budget -= 1
    
    if budget:
        return pacman.history
    else:
        return ''


if __name__ == '__main__':
    main()
