def fcfs(requests, head_start):
    """
    First Come First Served: service requests in the exact order given.
    No optimization at all -- this is the baseline everything else
    should beat.
    """
    order = list(requests)
    movement = 0
    current = head_start
    for track in order:
        movement += abs(track - current)
        current = track
    return order, movement


def sstf(requests, head_start):
    """
    Shortest Seek Time First: always service whichever pending request
    is closest to the head's current position. Greedy -- makes the
    locally best choice every step, without looking ahead.
    """
    remaining = list(requests)
    order = []
    current = head_start
    movement = 0

    while remaining:
        nearest = min(remaining, key=lambda track: abs(track - current))
        movement += abs(nearest - current)
        current = nearest
        order.append(nearest)
        remaining.remove(nearest)

    return order, movement


def look(requests, head, direction="up"):
    """
    Sweep in `direction`, servicing every pending request in the way,
    then reverse as soon as there's nothing left ahead -- no wasted
    travel to the disk's physical edge. This is what real disk
    schedulers use in practice.
    """
    left = sorted(t for t in requests if t < head)   # tracks below head
    right = sorted(t for t in requests if t >= head)  # tracks at/above head

    if direction == "up":
        order = right + list(reversed(left))
    else:
        order = list(reversed(left)) + right

    movement = 0
    current = head
    for track in order:
        movement += abs(track - current)
        current = track

    return order, movement


def scan(requests, head, num_tracks=200, direction="up"):
    """
    Like LOOK, but always travels all the way to the physical edge of
    the disk (track 0, or the last track) before reversing -- even if
    no request is waiting there. This is the classic textbook version;
    it can never be cheaper than LOOK on the same data, only equal or
    worse, because it's doing everything LOOK does plus an extra trip.
    """
    left = sorted(t for t in requests if t < head)
    right = sorted(t for t in requests if t >= head)

    order = []
    movement = 0
    current = head

    def visit(track):
        nonlocal current, movement
        movement += abs(track - current)
        current = track

    if direction == "up":
        for track in right:
            visit(track)
            order.append(track)
        visit(num_tracks - 1)  # always sweep to the far edge
        for track in reversed(left):
            visit(track)
            order.append(track)
    else:
        for track in reversed(left):
            visit(track)
            order.append(track)
        visit(0)  # always sweep to the near edge
        for track in right:
            visit(track)
            order.append(track)

    return order, movement


if __name__ == "__main__":
    requests = [98, 183, 37, 122, 14, 124, 65, 67]
    head = 53
    num_tracks = 200

    results = {
        "FCFS": fcfs(requests, head),
        "SSTF": sstf(requests, head),
        "LOOK": look(requests, head, direction="up"),
        "SCAN": scan(requests, head, num_tracks, direction="up"),
    }

    print(f"Head starts at {head}, requests: {requests}\n")
    for name, (order, movement) in results.items():
        print(f"{name:5s} | total movement: {movement:4d} | order: {order}")