#!/usr/bin/python3
"""A tool to generate random works using markov chains."""

from random import random

import os
import argparse

parser = argparse.ArgumentParser(description='Generate an album listing.')

parser.add_argument('--dictionary', '-d', metavar='WORDLIST', default='/usr/share/dict/words', type=str, help='The word list to use.')
parser.add_argument('--word_count', '-w', metavar='NUM', default=1, type=int, help='The number of words to generate.')
parser.add_argument('--input_width', '-i', metavar='NUM', default=3, type=int, help='The number of letters to use as input for the markov chain.')

args = parser.parse_args()


def PathCanonicalize(filename):
  # Given a path, if it's absolute, return it, if it's relative, assume it's
  # relative to the directory containing the executable.
  if os.path.isabs(filename):
    return filename
  else:
    return os.path.join(os.path.dirname(__file__), filename)


def LoadWordList(filename):
  # Load the lines of a file into a list and return it.
  file_path = PathCanonicalize(filename)
  with open(file_path, 'r') as file:
    words = [word.strip().lower() for word in filter(lambda x:x.strip().isalpha(), file.readlines())]
    return words


def MakeFirstLetterProbabilities(words):
  letter_count = {}
  total_count = float(len(words))
  for word in words:
    if word[0] in letter_count:
      letter_count[word[0]] += 1
    else:
      letter_count[word[0]] = 1
  letter_probabilities = []
  cumulative_probability = 0.0
  for letter in sorted(letter_count.keys()):
    cumulative_probability += letter_count[letter] / total_count
    letter_probabilities.append((letter, cumulative_probability))
  return letter_probabilities


def MakeNToOneProbabilities(words, count):
  letter_count = {}
  total_count = {}
  for word in words:
    for i in range(0, len(word)-count):
      source = word[i:i+count]
      dest = word[i+count:i+count+1]
      subword = word[i:i+count+1]
      if source not in total_count:
        total_count[source] = 0
      total_count[source] += 1
      if source not in letter_count:
        letter_count[source] = {}
      if dest not in letter_count[source]:
        letter_count[source][dest] = 1
      letter_count[source][dest] += 1
    terminal = word[len(word)-count:]
    if terminal not in total_count:
      total_count[terminal] = 0
    total_count[terminal] += 1
    if terminal not in letter_count:
      letter_count[terminal] = {}
    if '' not in letter_count[terminal]:
      letter_count[terminal][''] = 1
    letter_count[terminal][''] += 1
  letter_probabilities = {}
  for source_letters in letter_count.keys():
    letter_probabilities[source_letters] = []
    cumulative_probability = 0.0
    for dest_letter in sorted(letter_count[source_letters].keys()):
      cumulative_probability += letter_count[source_letters][dest_letter] / total_count[source_letters]
      letter_probabilities[source_letters].append((dest_letter, cumulative_probability))
  return letter_probabilities


def GetRandomFirstLetter(letter_probabilities):
  number = random()
  for letter, cumulative_probability in letter_probabilities:
    if cumulative_probability > number:
      return letter
  return letter_probabilities[-1][1]


def GetOneFromN(n_to_one_probabilities, letters):
  number = random()
  for dest, cumulative_probability in n_to_one_probabilities[letters]:
    if cumulative_probability > number:
      return dest
  return letter_probabilities[-1][1]


def main():
  words = LoadWordList(args.dictionary)
  first_letter_probabilities = MakeFirstLetterProbabilities(words)
  markov_chains = []
  for chain_length in range(0, args.input_width):
    markov_chains.append(MakeNToOneProbabilities(words, chain_length + 1))
  for word_num in range(0, args.word_count):
    word = []
    word.append(GetRandomFirstLetter(first_letter_probabilities))
    while True:
      if len(word[-args.input_width:]) < args.input_width:
        word_snippet = ''.join(word[-args.input_width:])
        letter = None
        while not letter:
          letter = GetOneFromN(markov_chains[len(word_snippet)-1], word_snippet)
      else:
        letter = GetOneFromN(markov_chains[args.input_width-1], ''.join(word[-args.input_width:]))
      if not letter:
        break
      word.append(letter)
    print(''.join(word))


if __name__ == '__main__':
  main()
