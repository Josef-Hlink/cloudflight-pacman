import glob
import numpy as np

inputs = glob.glob('data/level2/*.in')

for inputfile in inputs:
    if 'example' in inputfile:
        continue

    with open(inputfile, 'r') as f:
        k = int(f.readline())
        board = ""
        for i in range(k):
            board += f.readline()
        pos = f.readline().split(' ')
        x, y = int(pos[0]) - 1, int(pos[1]) - 1
        nmoves = int(f.readline())
        moves = f.readline()
    
    # turn board into a 2d array
    board = np.array(list(board)).reshape(k, board.count('\n') + 1)
    # drop last element in each row to get rid of newline characters
    board = np.delete(board, -1, axis=1)

    coins_collected = 0

    for move in moves:
        if move == 'U':
            x -= 1
        elif move == 'D':
            x += 1
        elif move == 'L':
            y -= 1
        elif move == 'R':
            y += 1

        # check if pacman is on a coin
        if board[x, y] == 'C':
            board[x, y] = 'E'
            coins_collected += 1
    
    with open(inputfile.replace('in', 'out'), 'w') as f:
        f.write(str(coins_collected))
