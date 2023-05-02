import json, argparse, openai


# Parse arguments for human player's side and opponent's level
parser = argparse.ArgumentParser()
parser.add_argument("--side", help = "which side to play as; options: {white, black}", type = str)
parser.add_argument("--level", help = "level of difficulty of AI opponent; options {easy, medium, hard}", type = str)
args = parser.parse_args()

# Exit if arguments are invalid
if args.side not in ["white", "black"]:
    exit('Invalid player. Please enter "white" or "black"')
elif args.level not in ["easy", "medium", "hard"]:
    exit('Invalid level. Please enter "easy", "medium", or "hard"')


# Start up game window
import src.gameplay as gp

# Parse config.json for OpenAI API key and Stockfish path
f = open("./config.json")
data = json.load(f)
f.close()

# Initialize players
if args.side == "white":
    # Human is the white player
    human_black = False
    p1 = gp.HumanPlayer(path = data['STOCKFISH_PATH'], color = True)

    if args.level == "easy":
        # Easy opponent - alpha-beta
        p2 = gp.ABPlayer(color = False, fail_hard = False)
    elif args.level == "medium":
        # Medium opponent - Stockfish
        p2 = gp.StockfishPlayer(path = data['STOCKFISH_PATH'], color = False, depth = 4)
    else:
        # Hard opponent - Stockfish
        p2 = gp.StockfishPlayer(path = data['STOCKFISH_PATH'], color = False)
else:
    # Human is the black player
    human_black = True
    p2 = gp.HumanPlayer(path = data['STOCKFISH_PATH'], color = False)

    if args.level == "easy":
        # Easy opponent - alpha-beta
        p1 = gp.ABPlayer(color = True, fail_hard = False)
    elif args.level == "medium":
        # Medium opponent - Stockfish
        p1 = gp.StockfishPlayer(path = data['STOCKFISH_PATH'], color = True, depth = 4)
    else:
        # Hard opponent - Stockfish
        p1 = gp.StockfishPlayer(path = data['STOCKFISH_PATH'], color = True)

# Initialize ChatGPT instance and prime with introduction
openai.api_key = data['OPENAI_API_KEY']
model_engine = "gpt-3.5-turbo"
intro_message = f"You are a chess tutor for a beginner player playing as {args.side}."

response = openai.ChatCompletion.create(
    model = model_engine,
    messages = [
        {"role": "system", "content": intro_message},
        {"role": "user", "content": "Hello, ChatGPT!"},
    ],
    max_tokens = 100
)

message = response.choices[0]['message']
print(f"Chess tutor for {args.side} player is ready. Have fun!")

# Play game
gp.play_game(p1, p2, human_black)
