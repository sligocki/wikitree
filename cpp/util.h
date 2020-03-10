#ifndef WIKITREE_UTIL_H_
#define WIKITREE_UTIL_H_

#include <algorithm>
#include <map>
#include <set>

// Return key and value for maximum value in map.
// If there are more than one max, arbitrarily returns the first.
template<typename Key, typename Value>
std::pair<Key, Value> ArgMax(const std::map<Key, Value>& map) {
  bool is_first = true;
  Value max_value;
  Key best_key;
  for (const auto& [key, value] : map) {
    if (is_first || value > max_value) {
      max_value = value;
      best_key = key;
    }
    is_first = false;
  }

  if (is_first) {
    throw std::invalid_argument("ArgMax: map was empty.");
  }
  return std::make_pair(best_key, max_value);
}

template<typename T>
std::set<T> SetIntersection(std::set<T> set1, std::set<T> set2) {
  std::set<T> result;
  std::set_intersection(set1.begin(), set1.end(),
                        set2.begin(), set2.end(),
                        std::inserter(result, result.begin()));
  return result;
}

#endif  // WIKITREE_UTIL_H_
