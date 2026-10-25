from disk import Disk
from scheduling_algorithms import fcfs, sstf, look, scan
from request_generator import generate_patterned_requests
from integrated_scheduler import compare_modes
from intelligent_scheduler import run_simulation
from predictor import Predictor
from cache import AdaptiveCache
import metrics


REQUESTS = generate_patterned_requests(100, seed=42)
NUM_TRACKS = 200
HEAD_START = 53
CACHE_SIZE = 8


def run_and_report(name, order, movement):
    print(f"\n{name} result")
    print(f"  Order: {order}")
    print(f"  Total head movement: {movement}")


def show_predictor_statistics():
    predictor = Predictor()
    cache = AdaptiveCache(cache_size=CACHE_SIZE)
    for block in REQUESTS:
        predictor.record(block)
        cache.access(block)

    print("\nPredictor statistics")
    print(f"  Blocks learned (transition sources): {len(predictor.transitions)}")
    print(f"  Recent history (last {predictor.history_size}): {predictor.history}")

    sample_block = REQUESTS[-1]
    print(f"  Prediction after block {sample_block}: {predictor.predict(sample_block)}")

    stats = run_simulation(REQUESTS, cache_size=CACHE_SIZE, use_predictor=True,
                            head_start=HEAD_START, num_tracks=NUM_TRACKS)
    print(f"  With prediction enabled -> hit rate: {stats['hit_rate']:.2%}, "
          f"useful prefetches: {stats['useful_prefetches']}, "
          f"wasted prefetches: {stats['wasted_prefetches']}")


def main():
    while True:
        print("\n=== Intelligent Disk Scheduling ===")
        print("1. Run FCFS")
        print("2. Run SSTF")
        print("3. Run LOOK")
        print("4. Run SCAN")
        print("5. Compare integrated cache + scheduling modes")
        print("6. Show predictor statistics")
        print("7. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            order, movement = fcfs(REQUESTS, HEAD_START)
            run_and_report("FCFS", order, movement)
        elif choice == "2":
            order, movement = sstf(REQUESTS, HEAD_START)
            run_and_report("SSTF", order, movement)
        elif choice == "3":
            order, movement = look(REQUESTS, HEAD_START, direction="up")
            run_and_report("LOOK", order, movement)
        elif choice == "4":
            order, movement = scan(REQUESTS, HEAD_START, NUM_TRACKS, direction="up")
            run_and_report("SCAN", order, movement)
        elif choice == "5":
            compare_modes(REQUESTS, head_start=HEAD_START, cache_size=CACHE_SIZE, num_tracks=NUM_TRACKS)
        elif choice == "6":
            show_predictor_statistics()
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
