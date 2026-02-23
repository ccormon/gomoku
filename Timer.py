import time

class Timer:
    def __init__(self):
        self.startTime = None
        self.elapsedTime = 0

    def start(self):
        self.startTime = time.perf_counter()

    def stop(self):
        if self.startTime is not None:
            self.elapsedTime += time.perf_counter() - self.startTime
            self.startTime = None

    def reset(self):
        self.startTime = None
        self.elapsedTime = 0

    def getElapsedTime(self):
        if self.startTime is not None:
            return self.elapsedTime + (time.perf_counter() - self.startTime)
        return self.elapsedTime