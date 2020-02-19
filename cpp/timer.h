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

#endif  // WIKITREE_TIMER_H_
