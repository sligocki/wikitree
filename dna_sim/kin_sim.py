#!/usr/bin/env python3
"""
Simulate DNA inheritance for all blood relatives (kin) up to a certain distance.
"""

import argparse
import collections
import random

import dna_sim


class Person:
  people = []
  def __init__(self, id, gen_dist, gen_delta, *parents):
    assert len(parents) in (0, 2), (id, parents)
    self.id = id
    self.gen_dist = gen_dist
    self.gen_delta = gen_delta
    self.parents = parents
    self.genome = None
    self.people.append(self)


def create_desc(fertility_func, max_gen_dist, gen_dist, gen_delta, parent1, parent2=None, remove_child=False):
  if max_gen_dist == 0:
    return
  if gen_delta < -2:
    return

  if not parent2:
    # Non-kin spouses
    parent2 = Person(parent1.id + "S", None, gen_delta)
  num_children = fertility_func()
  if remove_child:
    num_children -= 1
  if num_children > 0:
    for child_num in range(num_children):
      child_id = parent1.id + "." + str(child_num)
      # TODO: Should we randomize which parent is listed first?
      child = Person(child_id, gen_dist, gen_delta, parent1, parent2)
      create_desc(fertility_func, max_gen_dist - 1, gen_dist + 1, gen_delta - 1, child)


def create_tree(fertility_func, max_gen_dist, gen_dist=0, gen_delta=0, id_prefix="R"):
  """Create a collection of descendants of ancestors.

  Assumes no inbreeding.
  """
  if max_gen_dist == 0:
    return Person(id_prefix, gen_dist, gen_delta)

  parents = []
  for par in ("0", "1"):
    parents.append(create_tree(fertility_func, max_gen_dist - 1, gen_dist + 1, gen_delta + 1, id_prefix + par))

  p = Person(id_prefix, gen_dist, gen_delta, *parents)
  create_desc(fertility_func, max_gen_dist, gen_dist + 1, gen_delta, *parents, remove_child=True)
  return p


class Genome:
  def __init__(self, chrom_sizes):
    self.chrom_sizes = chrom_sizes

  def sim_inheritance(self, person):
    chrom_pairs = []
    for chrom_index, chrom_size in enumerate(self.chrom_sizes):
      if not person.parents:
        chrom_pairs.append(
          ([(0, chrom_size, person.id + "#0")],
           [(0, chrom_size, person.id + "#1")]))
      else:
        child_chrom_pair = []
        for par_index in range(2):
          par_chrom_pair = person.parents[par_index].genome[chrom_index]
          cross = dna_sim.sim_crossover(chrom_size)
          child_chrom = dna_sim.apply_crossover(cross, par_chrom_pair)
          dna_sim.validate_chromosome(chrom_size, child_chrom)
          child_chrom_pair.append(child_chrom)
        chrom_pairs.append(child_chrom_pair)
    return chrom_pairs


def sim_person(genome, person):
  if not person.genome:
    for parent in person.parents:
      sim_person(genome, parent)
    person.genome = genome.sim_inheritance(person)


def sim_tree(genome, people):
  for person in people:
    sim_person(genome, person)


def shared_dna(genome1, genome2):
  shared_segments = []
  for chrom_index, (chrom_pair1, chrom_pair2) in enumerate(zip(genome1, genome2)):
    for chrom1 in chrom_pair1:
      for begin_seg1, end_seg1, id1 in chrom1:
        for chrom2 in chrom_pair2:
          for begin_seg2, end_seg2, id2 in chrom2:
            if id1 == id2 and begin_seg1 < end_seg2 and begin_seg2 < end_seg1:
              shared_segments.append((chrom_index,
                                      max(begin_seg1, begin_seg2),
                                      min(end_seg1, end_seg2),
                                      id1))
  return shared_segments


def flatten_segments(segments):
  flat = []
  segments.sort()
  seg_chrom_num = None
  seg_begin = None
  seg_end = None
  for chrom_num, begin, end, _ in segments:
    if chrom_num == seg_chrom_num and begin <= seg_end:
      seg_end = end
    else:
      if seg_chrom_num != None:
        flat.append((seg_chrom_num, seg_begin, seg_end))
      seg_chrom_num = chrom_num
      seg_begin = begin
      seg_end = end
  return flat


def summarize_segments(shared_segments):
  sizes = [end-begin for _, begin, end, _ in shared_segments]
  sizes_detectable = [end-begin for _, begin, end, _ in shared_segments if end-begin >= 7.0]
  print("  Shared cM:", sum(sizes))
  print("  Shared cM [segs >= 7cM]:", sum(sizes_detectable))
  print("  Num segments:", len(sizes))
  print("  Num segments [>= 7cM]:", len(sizes_detectable))
  print("  Max segment [cM]:", max(sizes, default=0.))


def bin_search_index(xs, val):
  low = 0
  high = len(xs) - 1
  while high > low:
    mid = (low + high) // 2
    if xs[mid] < val:
      high = mid - 1
    else:
      low = mid + 1
  return low


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--max-gen-dist", type=int)
  args = parser.parse_args()

  fertility_func = lambda: 3
  root = create_tree(fertility_func, args.max_gen_dist)

  # Human autosome (Chromosomes 1-22).
  genome = Genome([281.5, 263.7, 224.2, 214.4, 209.3, 194.1, 187., 169.2, 167.2, 174.1, 161.1, 176., 131.9, 125.2, 132.4, 133.8, 137.3, 129.5, 111.1, 114.8, 70.1, 79.1])
  sim_tree(genome, Person.people)

  shared_amount = collections.defaultdict(list)
  print("Tree size:", len(Person.people))
  for person in Person.people:
    shared_segments = shared_dna(root.genome, person.genome)
    # When seeing a DNA match, we do not actually know where the segments come
    # from. So flatten the shared_segments out so that we just know where
    # matches not who it comes from.
    # Note: This does not distinguish fully identical vs half-identical regions.
    detected_segments = flatten_segments(shared_segments)
    sizes_detectable = [end-begin for _, begin, end in detected_segments if end-begin >= 7.0]
    shared_amount[person.gen_dist].append((sum(sizes_detectable), max(sizes_detectable, default=0.), person))
  print("%3s %8s %8s %8s %8s %8s %8s %8s" % ("Gen", "Max", "90%-ile", "Median", "Min", "Mean", "#>40cM", "#"))
  for gen_dist in range(args.max_gen_dist + 1):
    total_cMs = [total_cM for total_cM, _, person in shared_amount[gen_dist] if person.gen_delta <= 2]
    total_cMs.sort(reverse=True)
    print("%3d %8.2f %8.2f %8.2f %8.2f %8.2f %8d %8d" % (gen_dist, total_cMs[0], total_cMs[10 * len(total_cMs) // 100], total_cMs[len(total_cMs) // 2], total_cMs[-1], sum(total_cMs) / len(total_cMs), bin_search_index(total_cMs, 40.) + 1, len(total_cMs)))
  # for total_cm, max_cm, person in shared_amount:
  #   if person.gen_dist != None:
  #     print("%3d   %-10s %10.2f %10.2f" % (person.gen_dist, person.id, total_cm, max_cm))
