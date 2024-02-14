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
grid = [[" " for i in range(gridWidth)] for j in range(gridHeight)]


def removeLines():
    for r in range(len(grid)):
        row = grid[r]
        if row.count(" ") == 0:
            for block in otherShapes:
                newNodes = []
                for node in block.nodes:
                    if node.row < r:
                        node.row += 1
                        newNodes.append(node)
                    elif node.row != r:
                        newNodes.append(node)
                block.nodes = newNodes


def clearGrid():
    global grid
    grid = [[" " for i in range(gridWidth)] for j in range(gridHeight)]


def drawGrid():
    for row in grid:
        print(Fore.RESET + "|" + (Fore.RESET + "|").join(row) + Fore.RESET + "|")


class Node:
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def draw(self, color):
        grid[self.row][self.column] = color + "X"

    def collidingDown(self):
        if self.row == gridHeight:
            return True
        for block in otherShapes:
            for node in block.nodes:
                if self.row == node.row and self.column == node.column:
                    return True
        return False

    def collidingSides(self):
        if self.column < 0 or self.column == gridWidth:
            return True
        for block in otherShapes:
            for node in block.nodes:
                if self.row == node.row and self.column == node.column:
                    return True
        return False


class Block:
    def __init__(self, nodes, color):
        self.nodes = nodes
        self.color = color

    def cantMoveDown(self):
        copySelf = copy.deepcopy(self)
        copySelf.moveDown()
        return any(map(lambda x: x.collidingDown(), copySelf.nodes))

    def cantMoveLeft(self):
        copySelf = copy.deepcopy(self)
        copySelf.moveLeft()
        return any(map(lambda x: x.collidingSides(), copySelf.nodes))

    def cantMoveRight(self):
        copySelf = copy.deepcopy(self)
        copySelf.moveRight()
        return any(map(lambda x: x.collidingSides(), copySelf.nodes))

    def cantRotate(self):
        copySelf = copy.deepcopy(self)
        copySelf.rotate()
        return any(
            map(lambda x: x.collidingSides() or x.collidingDown(), copySelf.nodes)
        )

    def moveLeft(self):
        for node in self.nodes:
            node.column -= 1

    def moveRight(self):
        for node in self.nodes:
            node.column += 1

    def moveDown(self):
        for node in self.nodes:
            node.row += 1

    def rotate(self):
        # Calculate center of rotation
        center_x = sum(node.row for node in self.nodes) // len(self.nodes)
        center_y = sum(node.column for node in self.nodes) // len(self.nodes)

        # Rotate each node around the center
        new_nodes = []
        for node in self.nodes:
            dx = node.row - center_x
            dy = node.column - center_y
            new_row = center_x + dy
            new_column = center_y - dx
            new_nodes.append(Node(new_row, new_column))

        self.nodes = new_nodes

    def draw(self):
        for node in self.nodes:
            node.draw(self.color)

    def forceDown(self):
        while True:
            if self.cantMoveDown():
                break
            self.moveDown()


# Example usage
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
        Node(1, midWidth),
        Node(1, midWidth + 1),
        Node(0, midWidth + 2),
    ],
    Fore.RED,
)

tetrisShapes = [i_block, j_block, s_block, z_block, l_block, o_block]

currentShape = copy.deepcopy(random.choice(tetrisShapes))
otherShapes = []

while True:
    if keyboard.is_pressed("left") and not currentShape.cantMoveLeft():
        currentShape.moveLeft()
    if keyboard.is_pressed("right") and not currentShape.cantMoveRight():
        currentShape.moveRight()
    if keyboard.is_pressed("space"):
        currentShape.forceDown()
    if keyboard.is_pressed("up") and not currentShape.cantRotate():
        currentShape.rotate()
    clearGrid()
    currentShape.draw()
    for shape in otherShapes:
        shape.draw()
    drawGrid()
    time.sleep(0.075)
    os.system("cls")
    if currentShape.cantMoveDown():
        for node in currentShape.nodes:
            if node.row == 0:
                print("Game Over")
                sys.exit()
        otherShapes.append(currentShape)
        currentShape = copy.deepcopy(random.choice(tetrisShapes))
        removeLines()
    else:
        currentShape.moveDown()
