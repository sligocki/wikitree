"""
Tools for working with circles around a person.
"""

import bfs_tools


def load_circles(db, focus, num_circles):
  focus_num = db.get_person_num(focus)

  circles = [[] for dist in range(num_circles + 1)]
  for node in bfs_tools.ConnectionBfs(db, focus_num):
    if node.dist > num_circles:
      break
    circles[node.dist].append(node.person)

  return circles
