# ChessGPT
Integrating ChatGPT into Chess for move explanations with Stockfish as the engine.

To run, create a conda environment:

conda create -n ChessEnv python=3.9

run the following command:

pip install -r requirements.txt

This will get you the proper requirements.

You do need to create your own config.json file once you create an account with OpenAI. The config.json file should look like this:

```
	{
		"OPENAI_API_KEY": <your openAI API key>,
		"STOCKFISH_PATH": <path to Stockfish executable>
	}
```

You will also need to download Stockfish here: https://stockfishchess.org/download/


To run command-line interface:

```python main.py --side {white, black} --level {easy, hard}```


Citation for GUI:

https://github.com/fsmosca/Python-Easy-Chess-GUI/blob/master/python_easy_chess_gui.py

Funny ChatGPT quotes:

ChatGPT commentary: The move f3e5 for White is not possible as there is a piece obstructing the f3 square.

