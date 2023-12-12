import cv2
import dotenv
import os
import pyautogui
from functools import cache
from pyuac import main_requires_admin
from time import sleep

dotenv.load_dotenv()

class Config:
    """ all of these are represented in number of pixels on your screen, see README for details """
    X_BEGIN_LETTER_GRID_PX = int(os.environ.get("X_BEGIN_LETTER_GRID_PX"))
    Y_BEGIN_LETTER_GRID_PX = int(os.environ.get("Y_BEGIN_LETTER_GRID_PX"))
    GRID_SIZE_PX = int(os.environ.get("GRID_SIZE_PX"))
    SWAP_OPTION_SIZE_PX = int(os.environ.get("SWAP_OPTION_SIZE_PX"))
    X_BASE_SWAP_OPTION_PX = int(os.environ.get("X_BASE_SWAP_OPTION_PX"))
    Y_BASE_SWAP_OPTION_PX = int(os.environ.get("Y_BASE_SWAP_OPTION_PX"))

GRIDSIZE = 5
CHARSCORE = {
    'A': 1, 'B': 4, 'C': 5, 'D': 3,
    'E': 1, 'F': 5, 'G': 3, 'H': 4,
    'I': 1, 'J': 7, 'K': 6, 'L': 3,
    'M': 4, 'N': 2, 'O': 1, 'P': 4,
    'Q': 8, 'R': 2, 'S': 2, 'T': 2,
    'U': 4, 'V': 5, 'W': 5, 'X': 7,
    'Y': 4, 'Z': 8,
}
SWAP_OPTION_POS = {
    'A': (0, 0), 'B': (0, 1), 'C': (0, 2), 'D': (0, 3), 'E': (0, 4), 'F': (0, 5),
    'G': (1, 0), 'H': (1, 1), 'I': (1, 2), 'J': (1, 3), 'K': (1, 4), 'L': (1, 5),
    'M': (2, 0), 'N': (2, 1), 'O': (2, 2), 'P': (2, 3), 'Q': (2, 4), 'R': (2, 5),
    'S': (3, 0), 'T': (3, 1), 'U': (3, 2), 'V': (3, 3), 'W': (3, 4), 'X': (3, 5),
    'Y': (4, 0), 'Z': (4, 1),
}

def path(p):
    """ file path helper function """
    return os.path.join(os.path.dirname(__file__), p)

def define_globals():
    """ mutates trie and set of words to match the local dictionary of English words """
    global trie, wordset
    trie, wordset = gen_word_dict(path("dictionary"))

def set_cursor_pos(x, y, duration = None):
    """ wrapper for moveTo for more control of any debugging purposes """
    print(f"moving cursor to: ({x}, {y})")
    if duration == None:
        pyautogui.moveTo(x, y)
    else:
        pyautogui.moveTo(x, y, duration=duration)

def define_grid_io():
    """ mutates global variables to match all required information from the grid USING MANUAL FILE INPUT, so that processing can be done in the program where it uses this information """
    global grid, lttr_r, lttr_c, lttr_mode, dbl_r, dbl_c, dbl_mode

    file_in = open(path("input"), "r")
    text_in = file_in.read().split('\n')

    grid = tuple(list(r[:GRIDSIZE]) for r in text_in[:GRIDSIZE])
    print("input:\n  grid:")
    for r in grid:
        print('    ' + ' '.join(r))

    lttr_r, lttr_c, lttr_mode = (lambda r, c, mode: (int(r) - 1, int(c) - 1, mode.upper()))(*text_in[GRIDSIZE].strip().split())
    print(f"  lttr: {lttr_mode} found at ({lttr_r + 1}, {lttr_c + 1}) i.e. {grid[lttr_r][lttr_c]}")

    dbl_r, dbl_c, dbl_mode = (lambda r, c, mode: (int(r) - 1, int(c) - 1, True if mode.upper() == 'Y' else False))(*text_in[GRIDSIZE + 1].strip().split())
    print(f"  dble: dbl {('is not', 'is')[dbl_mode]} found{('', ' at ({}, {}) i.e. {}'.format(dbl_r + 1, dbl_c + 1, grid[dbl_r][dbl_c]))[dbl_mode]}")

def define_grid_screen():
    """ mutates global variables to match all required information from the grid ON YOUR SCREEN, so that processing can be done in the program where it uses this information """
    global grid, lttr_r, lttr_c, lttr_mode, dbl_r, dbl_c, dbl_mode

    while True:
        grid = [[None for _c in range(GRIDSIZE)] for _r in range(GRIDSIZE)]
        px_per_cell = Config.GRID_SIZE_PX / GRIDSIZE
        grid_reg = (Config.X_BEGIN_LETTER_GRID_PX, Config.Y_BEGIN_LETTER_GRID_PX, Config.GRID_SIZE_PX, Config.GRID_SIZE_PX)
        im = pyautogui.screenshot('_grid.png', region=grid_reg)
        for char in "RQWMKXEHGYUNPJOSTZBAVCDFIL":
            for loc_box in pyautogui.locateAll(path(f"signals\\{char}.png"), path('_grid.png'), confidence=0.865):
                grid_r, grid_c = int(loc_box.top // px_per_cell), int(loc_box.left // px_per_cell)
                if not grid[grid_r][grid_c]:
                    grid[grid_r][grid_c] = char

        grid_loaded = True
        for r in grid:
            for elem in r:
                if elem == None:
                    grid_loaded = False
                    print(f"something wrong with this grid? maybe restart script: {grid}")
                    break
            if elem == None:
                break
        if grid_loaded:
            break

    print("input:\n  grid:")
    for r in grid:
        print('    ' + ' '.join(r))

    for pot_lttr_mode in ('DL', 'TL'):
        loc_lttr = pyautogui.locate(path(f"signals\\{pot_lttr_mode}.png"), path('_grid.png'), confidence=0.65)
        if loc_lttr:
            lttr_r, lttr_c, lttr_mode = int(loc_lttr.top // px_per_cell), int(loc_lttr.left // px_per_cell), pot_lttr_mode
            print(f"  lttr: {lttr_mode} found at ({lttr_r + 1}, {lttr_c + 1}) i.e. {grid[lttr_r][lttr_c]}")
            break

    loc_dbl = pyautogui.locate(path("signals\\2X.png"), path('_grid.png'), confidence=0.65)
    dbl_r, dbl_c, dbl_mode = -1, -1, False
    if loc_dbl:
        dbl_r, dbl_c, dbl_mode = int(loc_dbl.top // px_per_cell), int(loc_dbl.left // px_per_cell), True
    print(f"  dble: dbl {('is not', 'is')[dbl_mode]} found{('', ' at ({}, {}) i.e. {}'.format(dbl_r + 1, dbl_c + 1, grid[dbl_r][dbl_c]))[dbl_mode]}")

@cache
def get_score(coords_list):
    """
    gets score of a list of grid coordinates (representing characters of an assumed-to-be-valid word), according to spellcast scoring logic

    - doubled score if it goes across a '2X'
    - doubled/tripled score for a character if they are selected while 'DL' or 'TL'
    - long words get +10 fixed score
    - each character is scored to what is listed in CHARSCORE
    """
    result = 0
    use_dbl = False
    for r, c in coords_list:
        if dbl_mode and r == dbl_r and c == dbl_c:
            use_dbl = True
        char_score = CHARSCORE[grid[r][c]]
        if r == lttr_r and c == lttr_c:
            if lttr_mode == 'DL':
                result += 2 * char_score
            else:
                result += 3 * char_score
        else:
            result += char_score
    if use_dbl:
        result *= 2
    if len(coords_list) > 5:
        result += 10
    return result

def get_score_leading_to(coords_list):
    """ returns a string representing the expected score accumulating throughout each coordinate you go through, in this coords_list """
    acc = []
    for i in range(1, len(coords_list) + 1):
        acc += get_score(coords_list[:i]),
    return ' / '.join(map(str, acc))

def gen_word_dict(file_name):
    """ generates a trie and set of words from I/O (given a file name containing the entire English dictionary, one word on each line) """
    file_in = open(file_name, "r")
    text_in = file_in.read().split('\n')
    trie, wordset = dict(), set()
    for word in text_in:
        uword = word.upper()
        curr = trie
        for char in uword:
            if char not in curr:
                curr[char] = {}
            curr = curr[char]
        wordset.add(uword)
    return trie, wordset

def rec(grid, r, c, trie, acc_word, acc_coords, expl):
    """ recursive function to find lists of grid coordinates (representing characters of a completed word), and returns the list giving the best score; depth-first search implementation """
    potential_coords = []
    if acc_word in wordset:
        potential_coords += acc_coords,
    for dr, dc in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
        new_coords = (r + dr, c + dc)
        nr, nc = new_coords[0], new_coords[1]
        if not (0 <= nr < GRIDSIZE and 0 <= nc < GRIDSIZE):
            continue
        if new_coords in expl:
            continue
        rc_next = grid[nr][nc]
        if rc_next in trie:
            potential_coords += rec(grid, nr, nc, trie[rc_next], acc_word + rc_next, acc_coords + (new_coords,), expl | {new_coords}),
    return max(potential_coords, default=tuple(), key=get_score)

def solve_best(out = True):
    """ finds the 'grid best coordinates' (e.g. solution) given the current grid """
    if out:
        print("solving best...")
    best_coords = tuple()
    for r in range(GRIDSIZE):
        for c in range(GRIDSIZE):
            char = grid[r][c]
            if char in trie:
                best_at_coords = rec(grid, r, c, trie[char], char, ((r, c),), {(r, c)})
                best_coords = max(best_coords, best_at_coords, key=get_score)
    if out:
        print(f"\nbest:\n  \"{''.join(map(lambda rc: grid[rc[0]][rc[1]], best_coords))}\" (+{get_score(best_coords)}, {get_score_leading_to(best_coords)})")
        print(f"  {' -> '.join(map(lambda rc: str((rc[0] + 1, rc[1] + 1)), best_coords))}\n")
    return best_coords

def solve_best_with_swap(out = True):
    """ basically solve_best but it brute-forces the entire grid to swap in a single character which would lead to an optimal scoring """
    if out:
        print("solving best with swap...")
    best_coords = solve_best(False)
    best_swap = None
    best_score = get_score(best_coords)
    for sr in range(GRIDSIZE):
        for sc in range(GRIDSIZE):
            prev = grid[sr][sc]
            for new_char in CHARSCORE:
                if new_char == prev:
                    continue
                grid[sr][sc] = new_char
                best_at_coords = solve_best(False)
                new_score = get_score(best_at_coords)
                if new_score > best_score:
                    best_swap = (sr, sc, new_char)
                    best_coords = best_at_coords
                    best_score = new_score
            grid[sr][sc] = prev
    if out:
        print(f"\nbest with swap:\n")
        print(f"  swap at ({best_swap[0] + 1}, {best_swap[1] + 1}) to '{best_swap[2]}' (pos = {SWAP_OPTION_POS[best_swap[2]]})")
        print(f"  \"{''.join(map(lambda rc: best_swap[2] if best_swap[0] == rc[0] and best_swap[1] == rc[1] else grid[rc[0]][rc[1]], best_coords))}\" (+{best_score})")
        print(f"  {' -> '.join(map(lambda rc: str((rc[0] + 1, rc[1] + 1)), best_coords))}\n")

    return best_coords, best_swap

def control_mouse_to_solve(coords):
    """ controls mouse from normal game screen to hold down click, drag mouse to each given grid coordinate tuple, then release afterward to 'enter the solution in' """
    px_per_cell = Config.GRID_SIZE_PX / GRIDSIZE
    x_base = Config.X_BEGIN_LETTER_GRID_PX + px_per_cell // 2
    y_base = Config.Y_BEGIN_LETTER_GRID_PX + px_per_cell // 2

    set_cursor_pos(x_base + px_per_cell * coords[0][1], y_base + px_per_cell * coords[0][0])
    sleep(0.1)
    pyautogui.mouseDown()
    sleep(0.1)
    for r, c in coords[1:]:
        set_cursor_pos(x_base + px_per_cell * c, y_base + px_per_cell * r, duration=0.1)
    pyautogui.mouseUp()

def control_mouse_to_swap(swap):
    """ controls mouse from normal game screen to clicking letter to swap in, going back to normal game screen afterward """
    px_per_cell = Config.GRID_SIZE_PX / GRIDSIZE
    x_base = Config.X_BEGIN_LETTER_GRID_PX + px_per_cell // 2
    y_base = Config.Y_BEGIN_LETTER_GRID_PX + px_per_cell // 2

    r, c, letter = swap
    while True:
        loc_swap = pyautogui.locateOnScreen(path("signals\\SWAP.png"), confidence=0.75)
        if loc_swap:
            center_swap_bttn_pnt = pyautogui.center((loc_swap.left, loc_swap.top, loc_swap.width, loc_swap.height))
            break
        sleep(0.1)

    # press 'SWAP' button option
    set_cursor_pos(center_swap_bttn_pnt.x, center_swap_bttn_pnt.y)
    sleep(1)
    pyautogui.click()
    sleep(1)

    # press letter node to swap out
    set_cursor_pos(x_base + px_per_cell * c, y_base + px_per_cell * r)
    sleep(1)
    pyautogui.click()
    sleep(1)

    # click the letter to swap in
    sr, sc = SWAP_OPTION_POS[letter]
    set_cursor_pos(Config.X_BASE_SWAP_OPTION_PX + Config.SWAP_OPTION_SIZE_PX * sc, Config.Y_BASE_SWAP_OPTION_PX + Config.SWAP_OPTION_SIZE_PX * sr)
    sleep(1)
    pyautogui.click()
    sleep(1)

def test_swap_options():
    """ seeing where it clicks for each swap character for debugging purposes """
    for k in SWAP_OPTION_POS:
        sr, sc = SWAP_OPTION_POS[k]
        set_cursor_pos(Config.X_BASE_SWAP_OPTION_PX + Config.SWAP_OPTION_SIZE_PX * sc, Config.Y_BASE_SWAP_OPTION_PX + Config.SWAP_OPTION_SIZE_PX * sr)
        sleep(0.25)
    exit()

def main_no_automation():
    """ can replace main() if you don't want the automation (all info will be displayed during the program's runtime) """
    define_globals()
    while True:
        loc_turn = pyautogui.locateOnScreen(path("signals\\TURN.png"), confidence=0.75)
        if loc_turn:
            define_grid_screen()
            coords = solve_best()
            coords, swap = solve_best_with_swap()
        sleep(5)

@main_requires_admin
def main_yes_automation():
    """ solves and automatically clicks around to enter the solution in (why is admin required?: controlling mouse in Discord app requires it, for some reason) """
    #test_swap_options()
    print("defining globals")
    define_globals()
    print("please clear all non-Discord windows and cursor from the grid to make it as accurate as possible")
    for sec_count in range(3, 0, -1):
        print(f"you have {sec_count} seconds")
        sleep(1)
    print("starting loop")
    while True:
        loc_turn = pyautogui.locateOnScreen(path("signals\\TURN.png"), confidence=0.75)
        if loc_turn:
            set_cursor_pos(Config.X_BEGIN_LETTER_GRID_PX - 50, Config.Y_BEGIN_LETTER_GRID_PX - 10)
            define_grid_screen()
            loc_can_swap = pyautogui.locateOnScreen(path("signals\\CAN_SWAP.png"), confidence=0.9)
            if loc_can_swap:
                print('will swap')
                coords, swap = solve_best_with_swap()
                control_mouse_to_swap(swap)
            else:
                print('cannot swap')
                coords = solve_best()
            control_mouse_to_solve(coords)
            sleep(1)

if __name__ == "__main__":
    """ simply comment out the one you don't want to use, while uncommenting the other one that you do want to use """
    #main_no_automation()
    main_yes_automation()