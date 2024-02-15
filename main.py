from colorama import Fore
import os
import time
import random
import copy
import keyboard
import sys

gridWidth = 16
midWidth = gridWidth // 2
gridHeight = 32

# This is the grid, it is an empy 2D array at the start for now
grid = [[" " for i in range(gridWidth)] for j in range(gridHeight)]


# Removes any full rows from the grid and shifts above blocks down
def removeLines():

    for r in range(len(grid)):
        row = grid[r]
        if row.count(" ") == 0:  # Checks if a row is full
            for block in otherBlocks:
                newNodes = []
                # Removes and shifts the blocks based on their row
                for node in block.nodes:
                    if node.row < r:
                        node.row += 1
                        newNodes.append(node)
                    elif node.row != r:
                        newNodes.append(node)
                block.nodes = newNodes


# Resets the grid to an empty 2D array
def clearGrid():
    global grid
    grid = [[" " for i in range(gridWidth)] for j in range(gridHeight)]


# Draws the grid - the bars are added and the colors are reset
def drawGrid():
    for row in grid:
        print(Fore.RESET + "|" + (Fore.RESET + "|").join(row) + Fore.RESET + "|")


# A node is 1 part of a block
class Node:
    # It contains a row and column
    def __init__(self, row, column):
        self.row = row
        self.column = column

    # Draws a node
    def draw(self, color):
        grid[self.row][self.column] = color + "X"

    # Checks if the block is colliding with other blocks or the floor
    def collidingDown(self):
        # floor
        if self.row == gridHeight:
            return True
        # other blocks
        for block in otherBlocks:
            for node in block.nodes:
                if self.row == node.row and self.column == node.column:
                    return True
        return False

    # Checks if the block is colliding with the walls or other blocks
    def collidingSides(self):
        if self.column < 0 or self.column == gridWidth:
            return True
        # other blocks
        for block in otherBlocks:
            for node in block.nodes:
                if self.row == node.row and self.column == node.column:
                    return True
        return False


# A block is a shape in tetris that moves down
class Block:
    # It has some nodes and a color
    def __init__(self, nodes, color):
        self.nodes = nodes
        self.color = color

    # Checks if it can move down by trying and checking collisions
    def cantMoveDown(self):
        copySelf = copy.deepcopy(self)
        copySelf.moveDown()
        return any(map(lambda x: x.collidingDown(), copySelf.nodes))

    # Checks if it can move left by trying and checking collisions
    def cantMoveLeft(self):
        copySelf = copy.deepcopy(self)
        copySelf.moveLeft()
        return any(map(lambda x: x.collidingSides(), copySelf.nodes))

    # Checks if it can move right by trying and checking collisions
    def cantMoveRight(self):
        copySelf = copy.deepcopy(self)
        copySelf.moveRight()
        return any(map(lambda x: x.collidingSides(), copySelf.nodes))

    # Checks if it can move rotate by trying and checking collisions
    def cantRotate(self):
        copySelf = copy.deepcopy(self)
        copySelf.rotate()
        return any(
            map(lambda x: x.collidingSides() or x.collidingDown(), copySelf.nodes)
        )

    # Moves the block left
    def moveLeft(self):
        for node in self.nodes:
            node.column -= 1

    # Moves the block right
    def moveRight(self):
        for node in self.nodes:
            node.column += 1

    # Moves the block down
    def moveDown(self):
        for node in self.nodes:
            node.row += 1

    # Rotates the block
    def rotate(self):
        # Calculate center of rotation
        center_x = sum(node.row for node in self.nodes) // len(self.nodes)
        center_y = sum(node.column for node in self.nodes) // len(self.nodes)

        # Rotate each node around the center (using the principles of matricies)
        new_nodes = []
        for node in self.nodes:
            dx = node.row - center_x
            dy = node.column - center_y
            new_row = center_x + dy
            new_column = center_y - dx
            new_nodes.append(Node(new_row, new_column))

        self.nodes = new_nodes

    # Draws the block (self explanatory)
    def draw(self):
        for node in self.nodes:
            node.draw(self.color)

    # Moves the block down until it can't anymore
    def forceDown(self):
        while True:
            if self.cantMoveDown():
                break
            self.moveDown()


# Here are all the blocks
i_block = Block(
    [
        Node(0, midWidth - 1),
        Node(0, midWidth),
        Node(0, midWidth + 1),
        Node(0, midWidth + 2),
    ],
    Fore.BLUE,
)

j_block = Block(
    [
        Node(0, midWidth),
        Node(0, midWidth + 1),
        Node(0, midWidth + 2),
        Node(1, midWidth + 2),
    ],
    Fore.CYAN,
)

l_block = Block(
    [
        Node(0, midWidth),
        Node(0, midWidth + 1),
        Node(0, midWidth + 2),
        Node(1, midWidth),
    ],
    Fore.MAGENTA,
)

o_block = Block(
    [
        Node(0, midWidth),
        Node(1, midWidth),
        Node(0, midWidth + 1),
        Node(1, midWidth + 1),
    ],
    Fore.YELLOW,
)
s_block = Block(
    [
        Node(1, midWidth),
        Node(0, midWidth + 1),
        Node(1, midWidth + 1),
        Node(0, midWidth + 2),
    ],
    Fore.GREEN,
)

z_block = Block(
    [
        Node(0, midWidth),
        Node(0, midWidth + 1),
        Node(1, midWidth + 1),
        Node(2, midWidth + 1),
    ],
    Fore.RED,
)

t_block = Block(
    [
        Node(0, midWidth),
        Node(0, midWidth + 1),
        Node(0, midWidth + 2),
        Node(1, midWidth + 1),
    ],
    Fore.LIGHTBLACK_EX,
)

# All the possible shapes
tetrisBlocks = [i_block, j_block, s_block, z_block, l_block, o_block, t_block]

# This is the block the user is moving - it is randomly set
currentBlock = copy.deepcopy(random.choice(tetrisBlocks))
# These are the blocks that have already been placed
otherBlocks = []

while True:
    # Keyboard controls
    if keyboard.is_pressed("left") and not currentBlock.cantMoveLeft():
        currentBlock.moveLeft()
    if keyboard.is_pressed("right") and not currentBlock.cantMoveRight():
        currentBlock.moveRight()
    if keyboard.is_pressed("space"):
        currentBlock.forceDown()
    if keyboard.is_pressed("up") and not currentBlock.cantRotate():
        currentBlock.rotate()

    # Clears the grid and draws the blocks
    clearGrid()
    currentBlock.draw()
    for shape in otherBlocks:
        shape.draw()
    drawGrid()

    # Ticks the clock
    time.sleep(0.075)

    # Resets the screen
    os.system("cls")

    # Checks if the block is placed
    if currentBlock.cantMoveDown():
        # Checks for game over
        for node in currentBlock.nodes:
            if node.row == 0:
                print("Game Over")
                sys.exit()
        # Changes the block to a new block and removes any full rows if needed
        otherBlocks.append(currentBlock)
        currentBlock = copy.deepcopy(random.choice(tetrisBlocks))
        removeLines()
    else:
        currentBlock.moveDown()
