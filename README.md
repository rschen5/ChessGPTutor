# ChessGPT
Integrating ChatGPT into Chess for move explanations with Stockfish as the engine.

## Feedback form

https://docs.google.com/forms/d/e/1FAIpQLSfCVMd_ZQ4gH_0IZCgYvv6H3ZkD-3RKyYfgP_5riiUQDOXdFA/viewform

## Instructions

### Prerequisites:
* Create an account with OpenAI
* Download Stockfish here: https://stockfishchess.org/download/
* Create your own `config.json` file. It should look like this:
```
{
	"OPENAI_API_KEY": <your OpenAI API key>,
	"STOCKFISH_PATH": <path to Stockfish executable>
}
```

To run, create a conda environment:
```
conda create -n ChessEnv python=3.9
```
Run the following command to get the proper requirements:
```
pip install -r requirements.txt
```

### Running ChessGPT

```
python chessGPT.py --side {white, black} --level {easy, medium, hard}
```


## Funny ChatGPT quotes

ChatGPT commentary: The move f3e5 for White is not possible as there is a piece obstructing the f3 square.

