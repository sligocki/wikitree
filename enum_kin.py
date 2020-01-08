def enum_ancestors(db, start_num):
  gen = [(1, start_num)]
  while gen:
    new_gen = []
    for ahn, person in gen:
      yield ahn, person
      father = db.father_of(person)
      if father:
        new_gen.append((2 * ahn, father))
      mother = db.mother_of(person)
      if mother:
        new_gen.append((2 * ahn + 1, mother))
    gen = new_gen


def enum_descendant_generations(db, id, start_num, skip=None):
  gen = [(id, start_num)]
  while gen:
    yield gen
    new_gen = []
    for id, person in gen:
      for child_index, child in enumerate(db.children_of(person)):
        if not skip or child not in skip:
          new_gen.append(("%s.%d" % (id, child_index), child))
    gen = new_gen


def enum_kin(db, start_num):
  visited = set()
  for ahn, ancestor in enum_ancestors(db, start_num):
    for gen in enum_descendant_generations(db, str(ahn), ancestor, skip=visited):
      for id, person in gen:
        if person not in visited:
          visited.add(person)
          yield id, person
