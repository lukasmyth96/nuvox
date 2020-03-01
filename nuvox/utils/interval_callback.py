from threading import Timer, Thread, Event


class IntervalCallback():

    def __init__(self, interval, num_intervals, interval_callback, completion_callback):
        """

        Parameters
        ----------
        interval: float
            time (s) between calls of interval_callback
        num_intervals: int
            total number of intervals until completion_callback is called
        interval_callback: function
            function to be called after each interval
        completion_callback: function
            function to be called after n=num_intervals
        """
        self.interval = interval
        self.num_intervals = num_intervals
        self.interval_callback = interval_callback
        self.completion_callback = completion_callback
        self.thread = Timer(self.interval, self.call_callback)

        self.count = 0

    def call_callback(self):
        self.count += 1
        if self.count == self.num_intervals:
            self.completion_callback()
        else:
            self.interval_callback()
            self.thread = Timer(self.interval, self.call_callback)
            self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

    def restart(self):
        self.cancel()
        self.count = 0
        self.thread = Timer(self.interval, self.call_callback)
        self.start()
