import evaluation
import search
import gameplay
import json, argparse, openai
import chess
import chess.engine


parser = argparse.ArgumentParser()
parser.add_argument("--side", help="which side to play as; options: {white, black}", type=str)
parser.add_argument("--level", help="level of difficulty of AI opponent; options {easy, hard}", type=str)
args = parser.parse_args()


f = open("./config.json")
data = json.load(f)
f.close()


if args.side == "white":
    p1 = gameplay.HumanPlayer(color = True)

    if args.level == "easy":
        p2 = gameplay.AIPlayer(color = False, algo = "AB_fail_soft", depth=3)
    elif args.level == "hard":
        p2 = gameplay.StockfishPlayer(path = data['STOCKFISH_PATH'], color = False)
    else:
        exit('Invalid level. Please enter "easy" or "hard"')

elif args.side == "black":
    p2 = gameplay.HumanPlayer(color = False)

    if args.level == "easy":
        p1 = gameplay.AIPlayer(color = True, algo = "AB_fail_soft", depth=3)
    elif args.level == "hard":
        p1 = gameplay.StockfishPlayer(path = data['STOCKFISH_PATH'], color = True)
    else:
        exit('Invalid level. Please enter "easy" or "hard"')

else:
    exit('Invalid player. Please enter "white" or "black"')


openai.api_key = data['OPENAI_API_KEY']
model_engine = "gpt-3.5-turbo"

intro_message = "You are a chess tutor for a beginner player playing as {}.".format(args.side)

response = openai.ChatCompletion.create(
    model=model_engine,
    messages=[
        {"role": "system", "content": intro_message},
        {"role": "user", "content": "Hello, ChatGPT!"},
    ],
    max_tokens=100
)

message = response.choices[0]['message']
print("Chess tutor for {} player is ready. Have fun!".format(args.side))

gameplay.play_game(p1, p2)
