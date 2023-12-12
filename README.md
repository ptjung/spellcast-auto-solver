# Spellcast Autosolver

Spellcast is a round-based Discord Activity game which revolves around spelling
out valid words from a grid to gain points. The number of points you can earn
is dictated by bonuses placed on the grid, fixed points given for each character,
and the length of the word.

This repository offers a script which finds the optimal word to spell out. It
uses a greedy approach which *only* cares about maximizing points in the current
round (and does not bother to account for gem counts.) A depth-first search recursive
implementation is used to find the word which would grant the most points, and
when allowed to, will use up to `1` swap to maximize the points gained.

Within the code, you can change whether to automate the process or not, and
whether to use input from the screen or file input. By default, the process is
fully automated, and the script will use your mouse to perform actions in
Discord. The script runs on an infinite loop.

## Running

#### 1 - Installation
Install the required Python packages from the project's root directory:
```
$ pip install -r requirements.txt
```

#### 2 - Environment Setup
Create an `.env` file in the same root directory, containing the keys:
```
X_BEGIN_LETTER_GRID_PX - Number of pixels from left of entire screen
Y_BEGIN_LETTER_GRID_PX - Number of pixels from top of entire screen
GRID_SIZE_PX - Number of pixels
SWAP_OPTION_SIZE_PX - Number of pixels
X_BASE_SWAP_OPTION_PX - Number of pixels from left of entire screen
Y_BASE_SWAP_OPTION_PX - Number of pixels from top of entire screen
```
The values to use should follow this guideline:

<img src="https://i.imgur.com/z9dXkS8.png" width="300"> <img src="https://i.imgur.com/cUfbhlk.png" width="300">

My current environment is curated for `1920 x 1080` screens with a typical
full-screened Discord desktop application. This is what I use for that:
```
X_BEGIN_LETTER_GRID_PX=935
Y_BEGIN_LETTER_GRID_PX=275
GRID_SIZE_PX=360
SWAP_OPTION_SIZE_PX=53
X_BASE_SWAP_OPTION_PX=980
Y_BASE_SWAP_OPTION_PX=385
```

#### 3 - Running
Run the script in the project's root directory:
```
$ python main.py
```

## FAQ

**Will this script work 100% of the time?**

No, sadly the mouse coordinates seem buggy at times. Also, for automation, OCR
had been very difficult not to give false positives when identifying the in-game
characters, especially when the images are prone to noise.

My approach to this was to use hard-coded "signal images" (see `signals` folder),
which is tested on the user's screen until found. Through some trial and error,
I landed on some signals which gave me good results most of the time, but the
caveat with this is how the game window scales with your Discord window size, and
what I have hard-coded might not work for everyone. 

You can tweak the signal images as you wish to fit your needs, but what is
currently in there is curated for `1920 x 1080` screens with a typical full-screened
Discord desktop application. The same goes for the very specific confidence ratio
in-code that is used when identifying the images.

**Why do some of the signal images look uneven or are cropped strangely?**

These were attempts to play around the current confidence ratio used in the program.

One reason was to distinguish them from other characters as much as possible.
Sometimes you'll get a `Q` matching an `O` instead, so by cropping the `Q`'s image
to narrow down on the `Q`'s leg even more, the program will mistake it less as an `O`
and more of a `Q`.

Another reason was that sometimes characters are not found by the program, which
means that more confidence in the image is required. To counter this, I would add
a bit of white padding around the character as a trivial way to increase confidence.

**Why does it require administrator permissions for gameplay automation?**

The Discord desktop app does not seem to respond to mouse commands when
administrator permissions are not used, so I made the script require permissions
for automation. You can comment on the decorator within the script to test this
functionality.

## Acknowledgements
- Uses the dictionary file from a similar project: ![AaronLieb's SpellCastSolver](https://github.com/AaronLieb/SpellCastSolver)

## License
Usage is provided under the [MIT License](http://opensource.org/licenses/mit-license.php). See LICENSE for the full details.
