from request_generator import generate_random_requests, generate_patterned_requests


def test_random_trace_has_correct_length():
    trace = generate_random_requests(50, num_tracks=200)
    assert len(trace) == 50


def test_random_trace_stays_in_range():
    trace = generate_random_requests(200, num_tracks=200)
    assert all(0 <= t < 200 for t in trace)


def test_patterned_trace_has_correct_length():
    trace = generate_patterned_requests(50, num_tracks=200)
    assert len(trace) == 50


def test_patterned_trace_stays_in_range():
    trace = generate_patterned_requests(200, num_tracks=200)
    assert all(0 <= t < 200 for t in trace)


def test_same_seed_gives_same_trace():
    # reproducibility matters: you want to be able to re-run the same
    # experiment and get identical results for your report
    trace_a = generate_patterned_requests(30, seed=7)
    trace_b = generate_patterned_requests(30, seed=7)
    assert trace_a == trace_b


def test_patterned_trace_has_more_locality_than_random():
    # a rough sanity check: average jump size between consecutive
    # requests should be much smaller for the patterned trace
    random_trace = generate_random_requests(300, seed=1)
    patterned_trace = generate_patterned_requests(300, seed=1)

    def avg_jump(trace):
        jumps = [abs(trace[i] - trace[i - 1]) for i in range(1, len(trace))]
        return sum(jumps) / len(jumps)

    assert avg_jump(patterned_trace) < avg_jump(random_trace)


if __name__ == "__main__":
    test_random_trace_has_correct_length()
    test_random_trace_stays_in_range()
    test_patterned_trace_has_correct_length()
    test_patterned_trace_stays_in_range()
    test_same_seed_gives_same_trace()
    test_patterned_trace_has_more_locality_than_random()
    print("All tests passed!")