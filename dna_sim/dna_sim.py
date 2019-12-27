#!/usr/bin/env python3

import argparse
import collections
import random


def sim_segment_length():
  """Return a random simulation of segment length between crossovers.

  This is modeled as a Poisson process with expected value 100 cM.
  """
  return random.expovariate(1/100.)


def sim_crossover(chrom_size):
  """Simulate crossover from two generic parent chromosomes."""
  cross = []
  # Flip a coin to decide which chromosome to start with.
  chrom_num = random.randrange(2)
  begin = 0.0
  while True:
    end = begin + sim_segment_length()
    if end > chrom_size:
      # Final chunk ends at the end of the chromosome.
      cross.append((begin, chrom_size, chrom_num))
      return cross
    else:
      # Add a new segment.
      cross.append((begin, end, chrom_num))
      begin = end
      # Swap to other chromosome.
      chrom_num = 1 - chrom_num


def apply_crossover(cross, par_chromos):
  child_chromo = []
  for begin_cross, end_cross, chrom_num in cross:
    for begin_seg, end_seg, ahn in par_chromos[chrom_num]:
      if end_seg <= begin_cross:
        # Keep scanning chromosome till we find a segment that overlaps.
        continue
      elif begin_seg >= end_cross:
        # Move on to next crossover chunk.
        break
      else:
        # Add the overlapping portion of [begin_cross, end_cross] & [begin_seg, end_seg]
        child_chromo.append((max(begin_seg, begin_cross),
                             min(end_seg, end_cross),
                             ahn))
  return child_chromo


def validate_chromosome(chrom_size, chrom):
  prev_end = 0.0
  prev_ahn = None
  for begin, end, ahn in chrom:
    assert begin == prev_end
    assert ahn != prev_ahn
    prev_end = end
    prev_ahn = ahn
  assert prev_end == chrom_size


def sim_chrom_pair(chrom_size, gens):
  """Simulate a pair of chromosomes of size |chrom_size| centi-Morgans passed down |gens| generations.

  Returns two lists of tuples of (start index of a segment [in cM], which ancestor they came from [Ahnentafel # stored as binary string with leading 1 removed]).

  Note: This assumes no pedagry collapse within the last |gens| generations. In other words, it assumes that you have 2^|gens| distinct ancestors |gens| generations back (2 parents, 4 grandparents, etc.).
  """

  if gens == 1:
    # Base case:
    # 1 gens back, one of your chromosomes comes competely from
    # your father and one competely from your mother.
    return [(0, chrom_size, "0")], [(0, chrom_size, "1")]

  # Inductive case:
  chromosomes = [None, None]
  # For each parent, we:
  for i in range(2):
    # 1) Simulate that parent's chromosomes,
    par_chromos = sim_chrom_pair(chrom_size, gens - 1)
    # 2) Simulate crossover to produce a single hybrid chromosome which
    #    will be passed down to the child.
    cross = sim_crossover(chrom_size)
    child_chromo = apply_crossover(cross, par_chromos)
    validate_chromosome(chrom_size, child_chromo)
    # 3) Update the Ahnentafel #s
    # TODO: This is the wrong Ahnentafel translation!?!
    chromosomes[i] = [(begin, end, str(i) + ahn)
                      for (begin, end, ahn) in child_chromo]
  return chromosomes


def print_sim(cM, num_gens):
  """Print details about a single chromosome pair simulation."""
  chroms = sim_chrom_pair(cM, num_gens)

  for chrom in chroms:
    print("Chromosome")
    for begin, end, ahn in chrom:
      print("- %6.2f  %d" % (end-begin, int("1" + ahn, 2)))


def sim_human_chroms(num_gens):
  """Simulate chromosomes 1-22 as independent events."""
  # Chromosome 1-22 sizes according to GEDmatch:
  #   See: https://isogg.org/wiki/CentiMorgan
  # Note: We are not including X chromosome.
  chrom_sizes = [281.5, 263.7, 224.2, 214.4, 209.3, 194.1, 187., 169.2, 167.2, 174.1, 161.1, 176., 131.9, 125.2, 132.4, 133.8, 137.3, 129.5, 111.1, 114.8, 70.1, 79.1]
  return [sim_chrom_pair(cM, num_gens) for cM in chrom_sizes]


def describe_stat(xs):
  """Print various summary stats about a list of observations."""
  print("  Mean:   %.2f" % (sum(xs) / len(xs)))
  xs.sort()
  print("  Median: %.2f" % xs[len(xs) // 2])
  for percentile in (1, 10, 90, 99):
    print("  %3d%%-ile:%7.2f" % (percentile, xs[len(xs) * percentile // 100]))


class TopN:
  def __init__(self, n):
    self.n = n
    self.vals = []

  def update(self, val):
    self.vals.append(val)
    self.vals.sort(reverse=True)
    del self.vals[self.n:]


MIN_CM = 7.0
def summarize(num_gens, num_sims):
  """Simulate many human genomes num_gens back and print some summary stats."""
  max_seg_sizes = []
  max2_seg_sizes = []
  num_segs_vals = []
  num_segs_min_vals = []
  max_ancestor_total_cM = []
  med_ancestor_total_cM = []
  num_genetic_ancestors = []
  for _ in range(num_sims):
    chrom_pairs = sim_human_chroms(num_gens)

    per_ahn = collections.defaultdict(float)
    max_seg_size = TopN(2)
    num_segs = 0
    num_segs_min = 0
    for chrom_pair in chrom_pairs:
      for chrom in chrom_pair:
        for begin, end, ahn in chrom:
          num_segs += 1
          size = end-begin
          if size >= MIN_CM:
            num_segs_min += 1
            per_ahn[ahn] += size
            max_seg_size.update(size)
    max_seg_sizes.append(max_seg_size.vals[0])
    max2_seg_sizes.append(max_seg_size.vals[1])
    num_segs_vals.append(num_segs)
    num_segs_min_vals.append(num_segs_min)
    per_ahn_vals = list(per_ahn.values())
    per_ahn_vals.sort(reverse=True)
    max_ancestor_total_cM.append(per_ahn_vals[0])
    try:
      med_ancestor_total_cM.append(per_ahn_vals[2**(num_gens-1)])
    except IndexError:
      med_ancestor_total_cM.append(0.0)
    num_genetic_ancestors.append(len(per_ahn))

  print("Max segment size (cM):")
  describe_stat(max_seg_sizes)
  print()
  print("2nd largest segment size (cM):")
  describe_stat(max2_seg_sizes)
  print()
  print("Number of segments:")
  describe_stat(num_segs_vals)
  print()
  print("Number of segments [>= 7cM]:")
  describe_stat(num_segs_min_vals)
  print()
  print("Max ancestor total contribution (cM) [inc. segs >= 7cM]:")
  describe_stat(max_ancestor_total_cM)
  print()
  print("Median ancestor total contribution (cM) [inc. segs >= 7cM]:")
  describe_stat(med_ancestor_total_cM)
  print()
  print("Num genetic ancestors", num_gens, "back [seg >= 7cM]:")
  describe_stat(num_genetic_ancestors)
  print()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("num_gens", type=int)
  parser.add_argument("--num-sims", type=int, default=10000)
  args = parser.parse_args()

  summarize(args.num_gens, args.num_sims)
  #print_sim(281.5, args.num_gens)
