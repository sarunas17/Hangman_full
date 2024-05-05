# Hangman game

Welcome to the Hangman game! This is a classic word-guessing game where you try to figure out a hidden word by guessing one letter or a entire word at a time.

# Installation
## Virtual Environment
1. Make sure you have Python installed on your system.
2. Clone this repository to your local machine.
3. Navigate to the project directory.
4. Create a virtual environment:
```bash
python -m venv .venv
```
5. Activate the virtual environment:
```bash
source .venv/Scripts/activate
```
6. Install the required dependencies:
```bash
pip install -r requirements.txt
```
## Docker
1. Make sure you have Docker installed on your system.
2. Run the Docker container:
```bash
docker run -d -p 27017:27017 --name hangman-mongo mongo:latest
```
# Usage
1. Run the Hangman game:
```bash
python run.py
```
2. Follow the prompts to guess letters and try to uncover the hidden word.
3. You have a limited number of attempts to guess the word before the hangman is complete!

GOOD LUCK!