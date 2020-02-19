#include "timer.h"

Timer::Timer()
  : start_time_(std::chrono::high_resolution_clock::now()) {}

double Timer::ElapsedSeconds() const {
  const auto end_time = std::chrono::high_resolution_clock::now();
  const std::chrono::duration<double> time_diff = end_time - start_time_;
  return time_diff.count();
}
