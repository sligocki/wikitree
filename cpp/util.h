#ifndef WIKITREE_UTIL_H_
#define WIKITREE_UTIL_H_

#include <map>

// Return key and value for maximum value in map.
// If there are more than one max, arbitrarily returns the first.
template<typename Key>
std::pair<Key, int> ArgMax(const std::map<Key, int>& map) {
  int max_value = -1;
  Key best_key;
  for (const auto& [key, value] : map) {
    if (value > max_value) {
      max_value = value;
      best_key = key;
    }
  }

  return std::make_pair(best_key, max_value);
}

#endif  // WIKITREE_UTIL_H_
