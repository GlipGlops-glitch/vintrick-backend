import requests
import time
import json
from collections import deque
from threading import Lock
import logging

def setup_metrics_logger(log_path="metrics.log"):
    metrics_logger = logging.getLogger("metrics_logger")
    metrics_logger.setLevel(logging.INFO)
    if not metrics_logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        metrics_logger.addHandler(handler)
        metrics_logger.propagate = False
    return metrics_logger

def setup_error_logger(log_path="error.log"):
    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)
    if not error_logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        error_logger.addHandler(handler)
        error_logger.propagate = False
    return error_logger

class EndpointCaller:
    def __init__(self, logger=None, metrics_logger=None, error_logger=None):
        self.metrics_lock = Lock()
        self.request_times = deque(maxlen=1000)
        self.logger = logger
        self.metrics_logger = metrics_logger or setup_metrics_logger()
        self.error_logger = error_logger or setup_error_logger()

    def call(self, url, headers=None, params=None):
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, params=params)
            latency = time.time() - start_time
            response.raise_for_status()
            result = response.json()
            response_size_kb = len(json.dumps(result)) / 1024.0

            now = time.time()
            with self.metrics_lock:
                self.request_times.append(now)
                while self.request_times and self.request_times[0] < now - 60:
                    self.request_times.popleft()
                rpm = len(self.request_times)
                throughput = rpm / 60.0

            metrics_msg = (
                f"📊 Metrics | Latency: {latency:.4f}s | Response Size: {response_size_kb:.2f}kB | RPM: {rpm} | Throughput: {throughput:.2f} req/sec"
            )
            if self.logger:
                self.logger.info(metrics_msg)
            if self.metrics_logger:
                self.metrics_logger.info(metrics_msg)

            return result
        except Exception as exc:
            # Log errors to error_logger!
            if self.error_logger:
                self.error_logger.error(f"Error during endpoint call to {url}: {exc}", exc_info=True)
            if self.logger:
                self.logger.error(f"Error during endpoint call to {url}: {exc}", exc_info=True)
            raise