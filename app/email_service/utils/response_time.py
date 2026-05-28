import time

class ResponseTime:
    @staticmethod
    def start():
        return time.perf_counter()

    @staticmethod
    def end(start_time):
        return int((time.perf_counter() - start_time) * 1000)
