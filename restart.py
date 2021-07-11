import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("id", nargs='?')
args = parser.parse_args()

os.system("python bot.py " + args.id)
