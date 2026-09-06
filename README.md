# Intelligent Disk Scheduler

This project is a compact simulation of an intelligent disk scheduling system with:

- virtual disk modeling
- request generation
- scheduling algorithms (FCFS, SSTF, SCAN, LOOK, C-SCAN)
- LRU cache support
- future block prediction
- simple metrics and optional visualization

## Folder structure

- `disk.py` — virtual disk model
- `request_generator.py` — request trace generation
- `scheduling_algorithms.py` — disk scheduling policies
- `cache.py` — LRU caching logic
- `predictor.py` — future block predictor
- `intelligent_scheduler.py` — combined scheduling orchestrator
- `metrics.py` — performance metrics
- `visualize.py` — simple graph output
- `main.py` — demo runner
- `test_cases.py` — sanity checks

## Run the demo

```bash
python main.py
```

## Run tests

```bash
python test_cases.py
```

## Notes

The scheduler is intentionally simple and educational, designed for experimentation and extension rather than production use.
