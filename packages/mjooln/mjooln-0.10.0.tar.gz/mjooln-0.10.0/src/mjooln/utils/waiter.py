import time
from threading import Event
import signal


class Waiter:
    """
    Convenience class for waiting or sleeping
    """

    @classmethod
    def sleep(cls, seconds):
        """
        Simple sleep

        :param seconds: Seconds to sleep
        """
        time.sleep(seconds)

    def __init__(self, keyboard_interrupt=True):
        self._come = Event()
        if keyboard_interrupt:
            for sig in ("SIGTERM", "SIGHUP", "SIGINT"):
                signal.signal(getattr(signal, sig), self._keyboard_interrupt)

    def wait(self, seconds):
        """
        Sleeps for the given time, can be aborted with :meth:`come` and
        exits gracefully with keyboard interrupt

        :param seconds: Seconds to wait
        :type seconds: float
        :return: True if interrupted, False if not
        :rtype: bool
        """
        self._come.clear()
        self._come.wait(seconds)
        return self._come.is_set()

    def _keyboard_interrupt(self, signo, _frame):
        self._come.set()

    def come(self):
        """
        Abort :meth:`wait`
        """
        self._come.set()
