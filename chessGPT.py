import json, argparse, openai
import chess.engine

parser = argparse.ArgumentParser()
parser.add_argument("--side", help="which side to play as; options: {white, black}", type=str)
parser.add_argument("--level", help="level of difficulty of AI opponent; options {easy, medium, hard}", type=str)
args = parser.parse_args()


f = open("./config.json")
data = json.load(f)
f.close()

if args.side not in ["white","black"]:
    exit('Invalid player. Please enter "white" or "black"')
elif args.level not in ["easy","medium","hard"]:
    exit('Invalid level. Please enter "easy", "medium", or "hard"')


import gameplay

if args.side == "white":
    human_black = False
    p1 = gameplay.HumanPlayer(color = True)

    if args.level == "easy":
        p2 = gameplay.AIPlayer(color = False, algo = "AB_fail_soft", depth=3)
    elif args.level == "medium":
        p2 = gameplay.StockfishPlayer(path = data['STOCKFISH_PATH'], color = False, depth = 4)
    else:
        p2 = gameplay.StockfishPlayer(path = data['STOCKFISH_PATH'], color = False)

else:
    human_black = True
    p2 = gameplay.HumanPlayer(color = False)

    if args.level == "easy":
        p1 = gameplay.AIPlayer(color = True, algo = "AB_fail_soft", depth=3)
    elif args.level == "medium":
        p1 = gameplay.StockfishPlayer(path = data['STOCKFISH_PATH'], color = True, depth = 4)
    else:
        p1 = gameplay.StockfishPlayer(path = data['STOCKFISH_PATH'], color = True)


openai.api_key = data['OPENAI_API_KEY']
model_engine = "gpt-3.5-turbo"

intro_message = f"You are a chess tutor for a beginner player playing as {args.side}."

response = openai.ChatCompletion.create(
    model=model_engine,
    messages=[
        {"role": "system", "content": intro_message},
        {"role": "user", "content": "Hello, ChatGPT!"},
    ],
    max_tokens=100
)

message = response.choices[0]['message']
print(f"Chess tutor for {args.side} player is ready. Have fun!")

gameplay.play_game(p1, p2, human_black)
