#!/usr/bin/env python

import pygame
from pygame.locals import *
import sys

BLACK = pygame.Color(0,   0,   0,   255)
WHITE = pygame.Color(255, 255, 255, 255)
GREY  = pygame.Color(150, 150, 150, 255)

BLUE  = pygame.Color(0,   0,   255, 255)
GREEN = pygame.Color(0,   255, 0,   255)
RED   = pygame.Color(255, 0,   0,   255)

FPS = 60
N = 11

SIDE = 40

GOAL = [(0,       0),
        (0,       N-1),
        (N-1,     0),
        (N-1,     N-1)]
RESTRICTED = GOAL + [((N-1)/2, (N-1)/2)]

COLORS = [RED, BLUE, GREEN]

def main():
  screen = pygame.display.set_mode((N*SIDE, N*SIDE))
  clock = pygame.time.Clock()

  selected = None
  pieces = setup()
  turn = False
  winner = None

  while not winner:
    # handle user input
    for event in pygame.event.get():
      if event.type == QUIT:
        sys.exit(0)
      elif event.type == MOUSEBUTTONUP and event.button == 1:
        x, y = event.pos
        target = (x/SIDE, y/SIDE)
        assert target[0] < N
        assert target[1] < N
        if selected:
          result = try_move(pieces, selected, target)
          if result:
            if target in GOAL and pieces[target] == 2:
              winner = 1
            if try_capture(pieces, target):
              winner = 2
            turn = not turn
          selected = None
        else:
          if target not in pieces: continue
          if (not turn and pieces[target] == 0) or (turn and pieces[target] > 0):
            selected = target

    # draw
    screen.fill(WHITE)
    for i in range(N):
      for j in range(N):
        square = pygame.Rect(i*SIDE, j*SIDE, SIDE, SIDE)
        if (i,j) in RESTRICTED:
          pygame.draw.rect(screen, GREY, square)
        pygame.draw.rect(screen, BLACK, square, 1)
        if (i,j) in pieces:
          width = SIDE/4 if selected == (i,j) else 0
          pygame.draw.ellipse(screen, COLORS[pieces[(i,j)]], square, width)
    clock.tick(FPS)
    pygame.display.flip()

  while True:
    for event in pygame.event.get():
      if event.type == QUIT:
        sys.exit(0)
    screen.fill(RED if winner == 2 else GREEN)
    clock.tick(FPS)
    pygame.display.flip()

# return True if king captured, else False
def try_capture(pieces, loc):
  i, j = loc
  win = False

  for x,y,f in [(i+1,j,ROW), (i-1,j,ROW), (i,j+1,COL), (i,j-1,COL)]:
    if (x,y) in pieces:
      flag = BOTH if pieces[(x,y)] == 2 else f
      if is_captured(pieces, (x,y), flag):
        # TODO: debug
        if pieces[(x,y)] == 2: win = True
        del pieces[(x,y)]

  return win

ROW  = 1
COL  = 2
BOTH = 3

# return True if piece at loc is captured, else False
def is_captured(pieces, loc, flag):
  assert flag in [ROW, COL, BOTH]
  i, j = loc

  # choose spaces to examine
  if flag == ROW:
    locs = [(i+1,j), (i-1,j)]
  elif flag == COL:
    locs = [(i,j+1), (i,j-1)]
  else: # BOTH
    locs = [(i+1,j), (i-1,j), (i,j+1), (i,j-1)]

  # choose the test to use
  if flag == ROW or flag == COL:
    test = lambda p: (p in RESTRICTED and p not in pieces) or \
                     (p in pieces and bool(pieces[p]) != bool(pieces[loc]))
  else: # BOTH
    test = lambda p: (p in RESTRICTED and p not in pieces) or \
                     (p[0] < 0 or p[0] >= N or p[1] < 0 or p[1] >= N) or \
                     (p in pieces and bool(pieces[p]) != bool(pieces[loc]))

  # see if all spaces satisfy the conditions
  return all(test(s) for s in locs)

# return True if move succeeds, else False
def try_move(pieces, src, dst):
  if src not in pieces:
    raise 'should never happen'

  if src == dst:
    return False # no-op

  if dst in RESTRICTED and pieces[src] != 2:
    return False # attempt to move onto RESTRICTED square

  diff = (dst[0] - src[0], dst[1] - src[1])

  if diff[0] and diff[1]:
    return False # attempt to move diagonally

  # handle all four possible movement directions
  if diff[0] and diff[0] > 0:
    path = (range(src[0]+1, dst[0]+1), [src[1]])
  elif diff[0] and diff[0] < 0:
    path = (range(dst[0], src[0]), [src[1]])
  elif diff[1] and diff[1] > 0:
    path = ([src[0]], range(src[1]+1, dst[1]+1))
  elif diff[1] and diff[1] < 0:
    path = ([src[0]], range(dst[1], src[1]))
  else:
    raise 'should never happen'

  # check for a clear path
  if is_clear(pieces, *path):
    pieces[dst] = pieces[src]
    del pieces[src]
    return True
  else:
    return False

def is_clear(pieces, ii, jj):
  return not any((i,j) in pieces for i in ii for j in jj)

def setup():
  p = {}
  for i in range(N):
    for j in range(N):
      # setup outside
      if ((i == 0 or i == N-1) and (j > N/4 and j < N*3/4)):
        p[(i,j)] = 0
      if ((j == 0 or j == N-1) and (i > N/4 and i < N*3/4)):
        p[(i,j)] = 0
      if i == (N-1)/2 and (j == 1 or j == N-2):
        p[(i,j)] = 0
      if j == (N-1)/2 and (i == 1 or i == N-2):
        p[(i,j)] = 0
      # setup inside
      if abs(i - (N-1)/2) + abs(j - (N-1)/2) < N/3:
        p[(i,j)] = 1
  p[((N-1)/2, (N-1)/2)] = 2
  return p

if __name__ == '__main__':
  main()
