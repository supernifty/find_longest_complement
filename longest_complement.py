#!/usr/bin/env python

import collections
import datetime
import sys

def log(msg):
    sys.stderr.write('{0} {1}\n'.format(datetime.datetime.now().strftime('%H:%M:%S'), msg))

rev = { 'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N' }
def complement(s):
  return ''.join([rev[x] for x in s])

def of_interest(s):
  if 'N' in s or s == len(s) * s[0]:
      return False
  else:
      return True

def hashval(s):
  return hash(s)

def main(seed, dist, mm, fastas, verbose, show):
  log('seeding with size {0} mismatch {1} dist {2}...'.format(seed, mm, dist))
  position = 0
  seeds = {}
  current = ''
  current_start = 0
  candidates = set()
  chromosomes = []
  for fasta in fastas:
    log('processing {0}...'.format(fasta))
    for linenum, line in enumerate(open(fasta, 'r')):
      if line.startswith('>'):
        chromosomes.append((line.strip()[1:], position))
        continue
      if linenum % 100000 == 0:
        log('read {0} lines. {1} seeds...'.format(linenum, len(candidates)))
      
      current += line.strip().upper()
      while position + seed <= current_start + len(current):
        block = current[position - current_start:position - current_start + seed]
        if of_interest(block):
          complemented = complement(block)
          if hashval(block) in seeds:
            if verbose:
              sys.stdout.write('{0} {1}:{2} {3}\n'.format(block, position, ','.join([ str(x) for x in seeds[hashval(block)]]), complemented))
            [ candidates.add((alt, position)) for alt in seeds[hashval(block)] ]
          if hashval(complemented) in seeds:
            seeds[hashval(complemented)].add(position)
          else:
            seeds[hashval(complemented)] = set([position])
        position += 1
      # remove old
      current = current[position - current_start:]
      current_start = position
    log('processing {0}: done'.format(fasta))

  seeds = None # hint to free memory

  log('extending with {0} seeds...'.format(len(candidates)))
  # pull everything into memory (!)
  # TODO can match across fastas
  current = ''
  for fasta in fastas:
    log('processing {0}...'.format(fasta))
    for linenum, line in enumerate(open(fasta, 'r')):
      if line.startswith('>'):
        continue
      if linenum % 100000 == 0:
        log('read {0} lines...'.format(linenum))
      current += line.strip().upper()

  log('checking seeds...')
  final = set()
  for idx, cand in enumerate(candidates):
      start1, start2 = cand
      length = seed
      # try extending to right
      while start2 + length < len(current):
        if current[start1 + length] == rev[current[start2 + length]]:
          length += 1
          #log('right extend...')
        else:
          break
      # try extending to left
      while start1 >= 0:
        if current[start1 - 1] == rev[current[start2 - 1]]:
          start1 -= 1
          start2 -= 1
          length += 1
          #log('left extend...')
        else:
          break
      #log('adding to final: {0} {1} {2}'.format(length, start1, start2))
      final.add((length, start1, start2, current[start1:start1+length], current[start2:start2+length]))
      if idx % 100000 == 0:
        log('processed {0} seeds...'.format(idx))

  sys.stdout.write('\n'.join(['{0} {1}:{2} {3}'.format(x[0], x[1], x[2], x[3]) for x in sorted(final)[-show:]]))
  sys.stdout.write('\nSequences\n')
  sys.stdout.write('\n'.join(['{0}\t{1}'.format(x[1], x[0]) for x in chromosomes]))
  sys.stdout.write('\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Longest complement')
    parser.add_argument('--seed', default=12, help='seed length')
    parser.add_argument('--show', default=100, help='results to show')
    parser.add_argument('--verbose', action='store_true', default=False, help='more logging')
    parser.add_argument('fasta', nargs='+', help='fasta file')
    args = parser.parse_args()
    dist = 100
    mm = 0
    main(int(args.seed), dist, mm, args.fasta, args.verbose, args.show)

