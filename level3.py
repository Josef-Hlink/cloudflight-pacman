import glob
import numpy as np
from typing import IO

def main():
    inputs = glob.glob('data/level3/*.in')
    for inputfile in inputs:
        print(inputfile)
        # if 'example' in inputfile:
        #     continue

        with open(inputfile, 'r') as f:
            k, board, px, py, nmoves, pmoves, ghosts = read_data(f)
    
        board = create_board(board, k)

        coins_collected = 0
        survived = 'YES'

        for mi in range(nmoves):
            pmove = pmoves[mi]

            px, py = do_move(px, py, pmove)

            if board[px, py] == 'W':
                survived = 'NO'
                break

            for ghost in ghosts:
                gmove = ghost['moves'][mi]
                ghost['x'], ghost['y'] = do_move(ghost['x'], ghost['y'], gmove)
                # check collision
                if ghost['x'] == px and ghost['y'] == py:
                    survived = 'NO'
                    break
            
            if survived == 'NO':
                break

            # check if pacman is on a coin
            if board[px, py] == 'C':
                board[px, py] = 'E'
                coins_collected += 1
        
        print(f'{coins_collected} {survived}')
        with open(inputfile.replace('in', 'out'), 'w') as f:
            f.write(f'{coins_collected} {survived}')
    
    return

def do_move(x: int, y: int, dir: str) -> tuple[int, int]:
    if dir == 'U':
        x -= 1
    elif dir == 'D':
        x += 1
    elif dir == 'L':
        y -= 1
    elif dir == 'R':
        y += 1
    return x, y

def read_data(f: IO) -> tuple[int, str, int, int, int, str, list[dict]]:
    k = int(f.readline())
    board = ""
    for i in range(k):
        board += f.readline()
    ppos = f.readline().split(' ')
    px, py = int(ppos[0]) - 1, int(ppos[1]) - 1
    nmoves = int(f.readline())
    pmoves = f.readline()
    
    # read in ghosts data
    ghosts = []
    # skip the number of ghosts line
    f.readline()
    while True:
        line = f.readline()
        if line == '':
            break
        ghost = {}
        pos = line.split(' ')
        x, y = int(pos[0]) - 1, int(pos[1]) - 1
        ghost['x'] = x
        ghost['y'] = y
        nmoves = int(f.readline())
        moves = f.readline()
        ghost['moves'] = moves
        ghosts.append(ghost)

    return k, board, px, py, nmoves, pmoves, ghosts

def create_board(board: str, k: int) -> np.ndarray:
    # turn board into a 2d array
    board = np.array(list(board)).reshape(k, board.count('\n') + 1)
    # drop last element in each row to get rid of newline characters
    board = np.delete(board, -1, axis=1)
    return board

if __name__ == '__main__':
    main()
