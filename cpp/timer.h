#ifndef WIKITREE_TIMER_H_
#define WIKITREE_TIMER_H_

#include <chrono>

class Timer {
 public:
  Timer();
  // Seconds since Timer was created.
  double ElapsedSeconds() const;

 private:
  const std::chrono::high_resolution_clock::time_point start_time_;
};

Timer::Timer()
  : start_time_(std::chrono::high_resolution_clock::now()) {}

double Timer::ElapsedSeconds() const {
  const auto end_time = std::chrono::high_resolution_clock::now();
  const std::chrono::duration<double> time_diff = end_time - start_time_;
  return time_diff.count();
}

#endif  // WIKITREE_TIMER_H_
