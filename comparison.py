import evaluation
import search
import gameplay
import json, argparse

# for us to run trials on different algorithms playing each other

parser = argparse.ArgumentParser()
parser.add_argument("--white", help="algorithm to play as white; options: {ab_hard, ab_soft, minimax, stockfish}", type=str)
parser.add_argument("--black", help="algorithm to play as black; options: {ab_hard, ab_soft, minimax, stockfish}", type=str)
args = parser.parse_args()
print(args.side)
print(args.opponent)

