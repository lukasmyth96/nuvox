from threading import Timer, Lock


class MyTimer():
    def __init__(self, timeout_secs, interval_secs, completion_callback, periodic_callback):

        self.timeout_secs = timeout_secs
        self.interval_secs = interval_secs
        self.seconds_passed = 0

        self.main_thread = Timer(timeout_secs, self.end)
        self.main_timer_running = False
        self.completion_callback = completion_callback

        self.periodic_timer_running = False
        self.interval_callback = periodic_callback

        self.lock = Lock()

    def start(self):
        self.main_timer_running = True
        self.main_thread.start()
        self.run_periodic_timer()

    def cancel(self):

        self.lock.acquire()
        if self.main_timer_running:
            self.main_timer_running = False
            self.main_thread.cancel()
        self.lock.release()

    def end(self):
        self.cancel()
        self.completion_callback()

    def run_periodic_timer(self):

        self.lock.acquire()
        if self.main_timer_running:
            if self.periodic_timer_running:
                self.seconds_passed += self.interval_secs
                self.interval_callback(self.seconds_passed)
            else:
                self.periodic_timer_running = True

            periodic_timer = Timer(self.interval_secs, self.run_periodic_timer)
            periodic_timer.start()

        self.lock.release()

