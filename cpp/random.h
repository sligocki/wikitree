#ifndef WIKITREE_RANDOM_H
#define WIKITREE_RANDOM_H

#include <inttypes.h>
#include <random>

class Random {
 public:
  Random() : seed_(std::random_device()()), random_engine_(seed_) {}

  int RandRange(int num) {
    if (num == 1) {
      return 0;
    }
    std::uniform_int_distribution<int> dist(0, num - 1);
    return dist(random_engine_);
  }

  double UniformReal(double low, double high) {
    std::uniform_real_distribution<double> dist(low, high);
    return dist(random_engine_);
  }

  template<typename T>
  const T& Choose(const std::vector<T>& collection) {
    int index = RandRange(collection.size());
    return collection[index];
  }

 private:
  uint32_t seed_;
  std::mt19937 random_engine_;

  // Disallow Copy and Assign
  Random(Random&) = delete;
  void operator=(Random) = delete;
};

#endif  // WIKITREE_RANDOM_H
