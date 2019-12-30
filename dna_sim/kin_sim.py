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
  def __init__(self, id, *parents):
    assert len(parents) in (0, 2), (id, parents)
    self.id = id
    self.parents = parents
    self.genome = None
    self.people.append(self)


def create_desc(fertility_func, num_gens_down, parent1, parent2=None, remove_child=False):
  if num_gens_down <= 0:
    return

  if not parent2:
    # Non-kin spouses
    parent2 = Person(parent1.id + "S")
  num_children = fertility_func()
  if remove_child:
    num_children -= 1
  if num_children > 0:
    for child_num in range(num_children):
      child_id = parent1.id + "." + str(child_num)
      # TODO: Should we randomize which parent is listed first?
      child = Person(child_id, parent1, parent2)
      create_desc(fertility_func, num_gens_down - 1, child)


def create_tree(fertility_func, num_gens_up, num_gens_down, id_prefix="R"):
  """Create a collection of descendants of ancestors.

  Search num_gens_up generations above starting person and then num_gens_down
  from them using fertility_func() to get # of children.

  Assumes no inbreeding.
  """
  if num_gens_up == 0:
    return Person(id_prefix)

  parents = []
  for par in ("0", "1"):
    parents.append(create_tree(fertility_func, num_gens_up - 1, num_gens_down, id_prefix + par))

  p = Person(id_prefix, *parents)
  create_desc(fertility_func, num_gens_down, *parents, remove_child=True)
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


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--num-gens-up", type=int)
  parser.add_argument("--num-gens-down", type=int, default=0)
  args = parser.parse_args()

  fertility_func = lambda: 3
  root = create_tree(fertility_func, args.num_gens_up, args.num_gens_down)

  # Human autosome (Chromosomes 1-22).
  genome = Genome([281.5, 263.7, 224.2, 214.4, 209.3, 194.1, 187., 169.2, 167.2, 174.1, 161.1, 176., 131.9, 125.2, 132.4, 133.8, 137.3, 129.5, 111.1, 114.8, 70.1, 79.1])
  sim_tree(genome, Person.people)

  shared_amount = []
  print("Tree size:", len(Person.people))
  for person in Person.people:
    shared_segments = shared_dna(root.genome, person.genome)
    # When seeing a DNA match, we do not actually know where the segments come
    # from. So flatten the shared_segments out so that we just know where
    # matches not who it comes from.
    # Note: This does not distinguish fully identical vs half-identical regions.
    detected_segments = flatten_segments(shared_segments)
    sizes_detectable = [end-begin for _, begin, end in detected_segments if end-begin >= 7.0]
    shared_amount.append((sum(sizes_detectable), max(sizes_detectable, default=0.), person.id))
  print()
  shared_amount.sort()
  for total_cm, max_cm, person_id in shared_amount:
    if person_id[-1] != "S":
      genetic_dist = len(person_id) - person_id.count(".") - 1
      if "." in person_id:
        genetic_dist -= 1
      print("%3d %-10s %10.2f %10.2f" % (genetic_dist, person_id, total_cm, max_cm))
