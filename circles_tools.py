"""
Tools for working with circles around a person.
"""

import bfs_tools
from data_reader import UserNum


def load_circles(db, focus : UserNum, num_circles : int
                 ) -> list[list[UserNum]]:
  focus_num = db.get_person_num(focus)

  circles : list[list[UserNum]] = [[] for dist in range(num_circles + 1)]
  for node in bfs_tools.ConnectionBfs(db, focus_num):
    if node.dist > num_circles:
      break
    circles[node.dist].append(node.person)

  return circles
