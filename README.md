# RPGPT (An AI text based adventure game)

## Description

RPGPT is a game that generates a text-based adventure for a user-created character, aimed to act as a human game master in a tabletop RPG game.
The game is based on the [GPT-4](https://openai.com/) language model, and uses a [HuggingFace](https://huggingface.co/) space for the text-to-image feature.
This project was created for fun and as a learning experience, and is open for contributions and improvements.

## Installation

First, set your openai and huggingface api keys in the `./envfile` file. (You can get an openai api key [here](https://platform.openai.com/), and a huggingface api key [here](https://huggingface.co/), huggingface key is optional, and required only for the experimental T2I feature.)
Then:

```bash
cp envfile .env
pip install -r requirements.txt
```

## Usage

```bash
python CLI.py
```

## AI Models

### LLM
Currently the game uses OpenAI's gpt-4. This model can be changed in the `backend/models/LLM.py` file.
The model is then used with the `generate` function, so if the model is changed, the `generate` function must keep its functionality.
Warning: The game has only been tested with gpt-4.

### T2I (EXPERIEMENTAL)
Currently the game uses [prompthero's openjourney-v4](https://huggingface.co/prompthero/openjourney-v4) from an open HuggingFace space. This model can be changed in the `backend/models/T2I.py` file.
The model is then used with the `generate` function, so if the model is changed, the `generate` function must keep its functionality.

## Game Themes

Currently, the available themes are:
- Fantasy
- Sci-Fi
- Wild-West
- Superhero

It is possible to add more themes by adding them in the `backend/Themes` file.
The theme must be a Theme class object (defined in `backend/Classes.py`). A theme must recieve a name, and all other parameters are optional.
The optional parameters are:
- `fields`: A list of fields that the theme will use in character creation and for story context.
- `extra_inventory_categories`: A list of extra inventory categories that the character has.
- `extra_fields`: A list of extra fields that the character has.
- `skills`: A list of skills that the character has to replace the defaults (see `backend/Classes.py` for the default skills).
You can see examples for all of these in the `backend/Themes.py` file, in the existing themes.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
