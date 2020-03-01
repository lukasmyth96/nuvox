from threading import Timer, Thread, Event


class IntervalCallback():

    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.thread = Timer(self.interval, self.call_callback)

    def call_callback(self):
        self.callback()
        self.thread = Timer(self.interval, self.call_callback)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

    def restart(self):
        self.cancel()
        self.thread = Timer(self.interval, self.call_callback)
        self.start()
