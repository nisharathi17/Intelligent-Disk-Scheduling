class Disk:
    """
    A simplified model of a disk. We don't touch real hardware —
    we just track a 'head position' (an integer track number) and
    measure how far it has to move to service each request.
    """

    def __init__(self, num_tracks=200, head_start=50):
        self.num_tracks = num_tracks      # tracks are numbered 0 .. num_tracks-1
        self.head_position = head_start   # where the head currently sits
        self.total_movement = 0           # running total of distance traveled
        self.history = [head_start]       # log of every position the head has visited

    def seek(self, track):
        """
        Move the head to `track`. This is the ONE operation every
        scheduling algorithm will call, in whatever order it decides.
        """
        if not (0 <= track < self.num_tracks):
            raise ValueError(f"track {track} is out of range 0..{self.num_tracks - 1}")

        distance = abs(track - self.head_position)
        self.total_movement += distance
        self.head_position = track
        self.history.append(track)
        return distance


if __name__ == "__main__":
    # Quick manual test: service 3 requests in the order given, no
    # smart ordering yet, just to see the class works.
    disk = Disk(num_tracks=200, head_start=50)

    for request in [98, 183, 37]:
        moved = disk.seek(request)
        print(f"Moved head to track {request} (cost: {moved})")

    print(f"\nTotal head movement: {disk.total_movement}")
    print(f"Head position history: {disk.history}")