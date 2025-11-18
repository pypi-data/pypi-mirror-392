import time

class Clock:
    def __init__(self):
        self.last = time.time()
        self.delta = 0
        self.fps = 60

    def tick(self, fps=None):
        now = time.time()
        self.delta = now - self.last
        self.last = now

        if fps:  
            self.fps = fps
            sleep_for = (1 / fps) - self.delta
            if sleep_for > 0:
                time.sleep(sleep_for)

        return self.delta

    def get_fps(self):
        return round(1 / self.delta, 2) if self.delta else 0
