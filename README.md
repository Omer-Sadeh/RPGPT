# RPGPT (An AI text based adventure game)

## Description

RPGPT is a game that generates a text-based adventure for a user-created character, aimed to act as a human game master in a tabletop RPG game.
The game is based on the [GPT-4](https://openai.com/) language model, and uses a [HuggingFace](https://huggingface.co/) space for the text-to-image feature.
The backend is hosted on a FastAPI server, and a react frontend hosted on an electron app.
This project was created for fun and as a learning experience, and is open for contributions and improvements.
Used technologies in the project:
- FastAPI
- OpenAI API
- HuggingFace API
- Firebase Database
- React
- Electron

## Installation

### Credentials Setup
First set-up the following environment variables in the `./envfile` file:
- `OPENAI_API_KEY`: Your OpenAI API key (You can get an openai api key [here](https://platform.openai.com/)).
- `HUGGINGFACE_BEARER`: Your HuggingFace API key (You can get a huggingface api key [here](https://huggingface.co/)).
- `AUTH_SECRET`: The secret you want to use for the JWT authentication.
- `REACT_APP_BACKEND_URL`: Your backend URL (default is `http://localhost:8000`).
- `FIREBASE_API_KEY` and all other Firebase environment variables.

To set up a Firebase project go [here](https://firebase.google.com/), and create a new project.
Then, go to the project settings and get the Firebase SDK snippet for the envfile variables.
Now, download the firebase service account key and save it in a `./backend/Database/conn/firebaseAuth.json` file.

Then:

```bash
cp envfile ./backend/.env
cp envfile ./frontend/.env
```

### Installation
```bash
pip install -r requirements.txt
cd frontend
npm install
```

## Running the Game

Just the `main.py` file in the `root` directory and follow the instructions.

## AI Models

### LLM
Currently, the game uses OpenAI's gpt-4.
This model can be changed in the `backend/GenAI/LLM/LLM.py` file, by generating a new ModelClass object with the desired model.
The model is then used with the `generate` function, so if the model is changed, the `generate` function must keep its functionality.
**Warning**: The game has only been tested with gpt-4.

### T2I
Currently,
the game uses [stabilityai's stable-diffusion-xl-base-1.0](https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0) from an open HuggingFace space.
This model can be changed in the `backend/GenAI/T2I.py` file.
The model is then used with the `generate` function, so if the model is changed, the `generate` function must keep its functionality.

## Game Themes

Currently, the available themes are:
- Fantasy
- Sci-Fi
- Wild-West
- Superhero

It is possible to add more themes by adding them in the `backend/Types/Themes` file.
The theme must be a Theme class object (defined in `backend/Types/Theme.py`).
A theme must receive a name, and all other parameters are optional.
The optional parameters are:
- `fields`: A list of fields that the theme will use in character creation and for story context.
- `extra_inventory_categories`: A list of extra inventory categories that the character has.
- `extra_fields`: A list of extra fields that the character has.
- `skills`: A list of skills that the character has to replace the defaults (see `backend/Types/Theme.py` for the default skills).
You can see examples for all of these in the `backend/Types/Themes.py` file, in the existing themes.

## Plans / Open for Contributions

1. **Make an actually good UI.**
I'm not an expert in React or frontend development, so the React code is quite messy and external libraries dependent.
It would be great if someone who knows what they're doing could clean up the code and make a better UI.
2. Upgrade the SNS system, so it would be better at protecting the LLM's from attacks. Currently, it's at a placeholder level.
3. Overhaul the logging system.
Currently, the logging system is very basic and local.
It would be nice to have a more robust logging system
that can be used for debugging and monitoring in an actual backend server.
4. Work out a testing framework, both for the backend and the frontend. Currently, there are no tests for the project.
5. Test out other AI models (such as Gemini, Claude...), and see if they can be used in the game.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
