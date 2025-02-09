import atexit
import pickle
from cachetools import TTLCache
import time
import threading
import os

class PersistentTTLCache(TTLCache):
    def __init__(
        self,
        maxsize: int,
        ttl: float,
        filename: str,
        timer=time.monotonic,
        getsizeof=None,
        save_interval=60  # seconds
    ):
        super().__init__(maxsize, ttl, timer=timer, getsizeof=getsizeof)
        self.filename = filename
        self._lock = threading.Lock()
        self._dirty = False
        self._load_cache()

        # Hope and pray for oom exec
        atexit.register(self.save_cache)
        
        if save_interval:
            self._setup_autosave(save_interval)

    def _setup_autosave(self, interval):
        def periodic_save():
            while True:
                time.sleep(interval)
                if self._dirty:
                    self.save_cache()

        save_thread = threading.Thread(target=periodic_save, daemon=True)
        save_thread.start()

    def _load_cache(self):
        if not os.path.exists(self.filename):
            return

        with self._lock:
            try:
                with open(self.filename, 'rb') as f:
                    data = pickle.load(f)
                    
                current_time = self.timer()
                for key, (value, expires) in data.items():
                    if expires > current_time:
                        super().__setitem__(key, value)
            except (pickle.PickleError, FileNotFoundError):
                pass

    def save_cache(self):
        with self._lock:
            cache_data = {}
            current_time = self.timer()
            
            for key, value in self.items():
                expires = self.timer() + self.ttl
                if expires > current_time:
                    cache_data[key] = (value, expires)

            # Atomic write using temporary file
            temp_filename = f"{self.filename}.tmp"
            with open(temp_filename, 'wb') as f:
                pickle.dump(cache_data, f)
            os.replace(temp_filename, self.filename)
            self._dirty = False

    def __setitem__(self, key, value):
        with self._lock:
            super().__setitem__(key, value)
            self._dirty = True

    def __delitem__(self, key):
        with self._lock:
            super().__delitem__(key)
            self._dirty = True
