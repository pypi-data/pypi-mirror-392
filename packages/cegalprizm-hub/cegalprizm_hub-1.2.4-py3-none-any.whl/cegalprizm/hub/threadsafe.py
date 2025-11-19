import threading
import logging


class ConcurrentDictionary():
    def __init__(self):
        self._dict = {}
        self._lock = threading.Lock()

    def get(self, key, default=None):
        with self._lock:
            return self._dict.get(key, default)

    def set_if_not_present(self, key, value):
        with self._lock:
            if key not in self._dict:
                self._dict[key] = value
                return value
            else:
                return self._dict[key]

    def remove(self, key):
        with self._lock:
            if key in self._dict:
                del self._dict[key]

    def __len__(self):
        with self._lock:
            return len(self._dict)


class CooperativeCancellationToken():
    def __init__(self):
        self.cancel_event = threading.Event()

    def cancel(self):
        logging.debug("Cancelling CooperativeCancellationToken")
        self.cancel_event.set()

    def is_cancelled(self):
        return self.cancel_event.is_set()
