"""
CountdownTimer - Thread-safe countdown timer
"""
import threading
import time


class CountdownTimer:
    def __init__(self, initial_time=30, on_tick=None, on_timeout=None):
        """
        Args:
            initial_time: Thời gian ban đầu (giây)
            on_tick: Callback mỗi giây (remaining_time)
            on_timeout: Callback khi hết giờ
        """
        self.initial_time = initial_time
        self.remaining_time = initial_time
        self.on_tick = on_tick
        self.on_timeout = on_timeout

        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def start(self):
        """Bắt đầu đếm ngược"""
        with self._lock:
            if self._running:
                return

            self._running = True
            self.remaining_time = self.initial_time

            self._thread = threading.Thread(target=self._countdown_loop, daemon=True)
            self._thread.start()

    def stop(self):
        """Dừng đếm ngược"""
        with self._lock:
            self._running = False

    def reset(self, new_time=None):
        """Reset và khởi động lại"""
        self.stop()
        if new_time is not None:
            self.initial_time = new_time
        self.start()

    def _countdown_loop(self):
        """Vòng lặp đếm ngược"""
        while self._running:
            time.sleep(1)

            with self._lock:
                if not self._running:
                    break

                self.remaining_time -= 1

                # Callback tick
                if self.on_tick:
                    self.on_tick(self.remaining_time)

                # Kiểm tra timeout
                if self.remaining_time <= 0:
                    self._running = False
                    if self.on_timeout:
                        self.on_timeout()
                    break

    def is_running(self):
        """Kiểm tra timer có đang chạy không"""
        with self._lock:
            return self._running

    def get_remaining_time(self):
        """Lấy thời gian còn lại"""
        with self._lock:
            return self.remaining_time

