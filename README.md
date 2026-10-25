# Intelligent Disk Scheduling

A simulation of disk head scheduling (FCFS, SSTF, LOOK, SCAN, C-SCAN)
combined with an LRU/adaptive cache and a Markov chain predictor for
prefetching, so you can see how caching and prediction reduce real
disk head movement on top of classic scheduling algorithms.

## How to run

```bash
python ui.py      # tkinter GUI with charts and stats
python main.py     # menu-driven CLI
```

## Files

- `disk.py` — virtual disk model, tracks head position and movement
- `request_generator.py` — random, patterned, and mixed request traces
- `scheduling_algorithms.py` — FCFS, SSTF, LOOK, SCAN policies
- `cache.py` — LRUCache and AdaptiveCache (LRU/MRU hybrid)
- `predictor.py` — Markov chain next-block predictor
- `metrics.py` — head movement, seek time, algorithm comparison
- `intelligent_scheduler.py` — single-pass cache + predictor simulation
- `integrated_scheduler.py` — 4-mode cache/prediction comparison
- `main.py` — menu-driven CLI demo
- `ui.py` — tkinter GUI with bar charts and stat panels
- `visualize.py` — matplotlib chart helpers
- `test_*.py` — unit tests

## Requirements

- Python 3.7+
- `tkinter` (for `ui.py`; ships with most Python installs)
- `matplotlib` (for `visualize.py` only)
