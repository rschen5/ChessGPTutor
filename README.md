# ChessGPTutor

Integrating ChatGPT into chess for move explanations with Stockfish as the engine - Command Line Interface version.

## Feedback form

https://docs.google.com/forms/d/e/1FAIpQLSfCVMd_ZQ4gH_0IZCgYvv6H3ZkD-3RKyYfgP_5riiUQDOXdFA/viewform

## Instructions

### Requirements:

This application requires Python 3.7 or higher.
* Create an account with OpenAI
* Download Stockfish here: https://stockfishchess.org/download/
* Create your own `config.json` file. It should look like this:
```
{
	"OPENAI_API_KEY": <your OpenAI API key>,
	"STOCKFISH_PATH": <path to Stockfish executable>
}
```

Create a conda environment:
```
conda create -n ChessEnv python=<python version>
```
Run the following command to get the Python libraries needed:
```
pip install -r requirements.txt
```

### Running ChessGPTutor (Command Line Interface version)

```
python chessGPTutor.py --side {white, black} --level {easy, medium, hard}
```

## Funny ChatGPT quotes

ChatGPT commentary: The move f3e5 for White is not possible as there is a piece obstructing the f3 square.

