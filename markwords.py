#!/usr/bin/python3
"""A tool to generate random words using Markov chains."""

from random import random

import os
import argparse

parser = argparse.ArgumentParser(description='Generate a random word using Markov chains.')

parser.add_argument('--dictionary', '-d', metavar='WORDLIST', default='/usr/share/dict/words', type=str, help='The word list to use.')
parser.add_argument('--word_count', '-c', metavar='NUM', default=1, type=int, help='The number of words to generate.')
parser.add_argument('--input_width', '-w', metavar='NUM', default=3, type=int, help='The number of letters to use as input for the markov chain.')
parser.add_argument('--initial_prefix', '-p', metavar='PREFIX', default='', type=lambda s: s.lower(), help='The prefix to use for the generated names.')

args = parser.parse_args()


def PathCanonicalize(filename):
  # Given a path, if it's absolute, return it, if it's relative, assume it's
  # relative to the directory containing the executable.
  if os.path.isabs(filename):
    return filename
  else:
    return os.path.join(os.path.dirname(__file__), filename)


def LoadWordList(filename):
  # Load the lines of a file into a list and return it with comments removed.
  file_path = PathCanonicalize(filename)
  with open(file_path, 'r') as file:
    words = [word.strip().lower() for word in filter(lambda x:x.strip().isalpha(), [y.split('#')[0] for y in file.readlines()])]
    return words


def WordsAndCountToMarkovChain(words, count):
  # Given a word list and a letter count, return a probability dict mapping a
  # 'count' letter string to a list of tuples containing possible subsequent
  # letters and their probabilities.
  letter_count = {}
  total_count = {}
  for word in words:
    full_word = word + '#' # We use # to mean 'nothing'
    for i, letter in enumerate(full_word):
      first_char_index = i - count
      subword = ''
      if first_char_index < 0:
        subword += '#' * (-first_char_index)
        first_char_index = 0
      subword += full_word[first_char_index:i+1]
      source = subword[0:count]
      dest = subword[-1]
      total_count[source] = total_count.setdefault(source, 0) + 1
      letter_count[source][dest] = letter_count.setdefault(source, {}).setdefault(dest, 0) + 1
  markov_chain = {}
  for source_letters in letter_count.keys():
    markov_chain[source_letters] = []
    cumulative_probability = 0.0
    for dest_letter in sorted(letter_count[source_letters].keys()):
      cumulative_probability += letter_count[source_letters][dest_letter] / total_count[source_letters]
      markov_chain[source_letters].append((dest_letter, cumulative_probability))
  return markov_chain


def GetOneFromN(n_to_one_probabilities, letters):
  # Given a probability distribution for sequential letters and a string of
  # letters, return a random letter that might follow the ones provided.
  number = random()
  for dest, cumulative_probability in n_to_one_probabilities[letters]:
    if cumulative_probability > number:
      return dest
  return letter_probabilities[-1][0]


def main():
  words = LoadWordList(args.dictionary)
  markov_chain = WordsAndCountToMarkovChain(words, args.input_width)
  initial_string = args.initial_prefix[-args.input_width:]
  initial_string = '#' * (args.input_width - len(initial_string)) + initial_string
  for word_num in range(0, args.word_count):
    current_string = initial_string
    word = args.initial_prefix
    while True:
      letter = GetOneFromN(markov_chain, current_string)
      if letter == '#':
        break
      word += letter
      current_string = current_string[1:] + letter
    print(''.join(word))


if __name__ == '__main__':
  main()
