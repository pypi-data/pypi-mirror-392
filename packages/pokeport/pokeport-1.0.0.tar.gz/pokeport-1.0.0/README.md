# Pokeport

Pokeport is a Python script that queries [SpriteCollab](https://sprites.pmdcollab.org) and returns prints a portrait of a Pokémon to the terminal. It leverages [CLImage](https://github.com/pnappa/CLImage) to allow for unicode and truecolor output in terminals that support such.

## Requirements

This program requires `python3` and `pip`. Additional python dependancies should be installed automatically.

Truecolor and unicode output requires a supported terminal. See [this](https://github.com/termstandard/colors) for more details, and a list of supported terminals.

## Installation

If you're on MacOS, you may need to install libjpeg as a requirement for Pillow.

```bash
brew install libavif libjpeg libraqm libtiff little-cms2 openjpeg webp
```

Install the project via pip;

```bash
pip install pokeport
```

The program should then be installed. You can check this by running;

```bash
pokeport
```

Which should print out the help page for the program.

## Uninstall

To uninstall the program, uninstall it via pip.

```bash
pip uninstall pokeport
```

## Updating

If bugs come up and you need to update the program, update it via pip.

```bash
pip install pokeport -U
```

## Usage

You can run the program from the command line to display the portrait of a Pokémon of your choice.

```text
usage: pokeport [POKÉMON NAME] [OPTION]

CLI utility that queries SpriteCollab, and prints a portrait from there in your shell

positional arguments:
  name                  Required. Name of desired Pokémon.

options:
  -h, --help            Show this help message and exit
  -e EMOTION, --emotion EMOTION
                        Name of desired emotion. Defaults to "Normal".
  -f FORM, --form FORM  Show the specified alternate form of a Pokémon.
  --female              Show the female form of the Pokémon instead, if it exists.
  --shiny               Show the shiny colors of the Pokémon instead, if it exists.
  --truecolor           Returns result in true colors instead of 256 colors, if supported by your terminal.
  --unicode             Returns result in unicode.
```

Example of printing out a specific Pokémon;

```bash
pokeport dragonair
```

Example of printing out a Pokémon with a specific emotion;

```bash
pokeport sneasler -e happy
```

Example of printing out a Shiny Pokémon;

```bash
pokeport absol --shiny
```

Example of printing out a Pokémon with gender differences;

```bash
pokeport luxray --female
```

Example of printing out a Pokémon with an alternate form;

```bash
pokeport zoroark -f hisui
```

Example of printing out a Pokémon in truecolor;

```bash
pokeport greninja --truecolor
```

Example of printing out a Pokémon in unicode;

```bash
pokeport serperior --unicode
```

## Credits

All Pokémon designs, names, branding etc. are trademarks of The Pokémon Company.

Pokémon portraits are taken from [SpriteCollab](https://sprites.pmdcollab.org). Credits for specific portraits are printed when the program is run.

## Similar Projects

`pokeport` is by no means the first program to print out Pokémon to your terminal. You should check out these other projects;

- [pokeget](https://github.com/talwat/pokeget)
- [pokeshell](https://github.com/acxz/pokeshell)
- [krabby](https://github.com/yannjor/krabby)
- [pokemon-colorscripts](https://gitlab.com/phoneybadger/pokemon-colorscripts)

## Building

Just use `build`.
