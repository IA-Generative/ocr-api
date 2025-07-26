import threading
import time
import os
import psutil
import logging
import json
from functools import wraps

try:
    from pynvml import (
        nvmlInit,
        nvmlShutdown,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetMemoryInfo,
        nvmlDeviceGetUtilizationRates,
        nvmlSystemGetDriverVersion,
        nvmlDeviceGetTemperature,
        nvmlDeviceGetCount,
        nvmlDeviceGetName,
    )

    nvmlInit()
    GPU_AVAILABLE = True
    GPU_COUNT = nvmlDeviceGetCount()  # Nombre de GPUs disponibles
    # On prend le premier GPU, si plusieurs
    GPU_HANDLE = nvmlDeviceGetHandleByIndex(0)
    gpu_name = nvmlDeviceGetName(GPU_HANDLE).decode("utf-8")
    driver_version = nvmlSystemGetDriverVersion().decode("utf-8")
    total_gpu_memory = nvmlDeviceGetMemoryInfo(GPU_HANDLE).total / 1024**2  # Total VRAM en MB
    # On part du principe que tous les GPUs ont des CUDA cores, sinon il faudrait interroger chaque GPU
    cuda_cores = nvmlDeviceGetCount()
except Exception as e:
    GPU_AVAILABLE = False
    GPU_HANDLE = None
    gpu_name = None
    driver_version = None
    total_gpu_memory = None
    cuda_cores = None
    print(e)


logger = logging.getLogger("resource_monitor")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


class ResourceMonitor:
    def __init__(self, interval_sec=1, label="default"):
        self.interval = interval_sec
        self.running = False
        self.thread = None
        self.label = label
        self.process = psutil.Process(os.getpid())
        self.cpu_name = ""
        self.total_cpu_cores = psutil.cpu_count(logical=False)  # Nombre de cores physiques
        self.total_cpu_threads = psutil.cpu_count(logical=True)  # Nombre total de threads
        self.total_ram = psutil.virtual_memory().total / 1024**2  # RAM en MB

        # Réseau
        self.net_io = psutil.net_io_counters()

        # I/O Disque
        self.disk_io = psutil.disk_io_counters()

        # Swap
        self.swap = psutil.swap_memory()

    def _log_usage(self):
        while self.running:
            cpu = self.process.cpu_percent(interval=None)
            ram = self.process.memory_info().rss / 1024**2  # Utilisation de la RAM en MB

            # Réseau
            net_io = psutil.net_io_counters()
            net_sent = net_io.bytes_sent / 1024**2  # Octets envoyés (MB)
            net_recv = net_io.bytes_recv / 1024**2  # Octets reçus (MB)

            # I/O Disque
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes / 1024**2  # Octets lus (MB)
            disk_write = disk_io.write_bytes / 1024**2  # Octets écrits (MB)

            # Swap
            swap_used = self.swap.used / 1024**2  # Swap utilisé en MB
            swap_total = self.swap.total / 1024**2  # Swap total en MB

            # Température CPU et GPU
            cpu_temp = psutil.sensors_temperatures().get(
                "coretemp",
            )  # Température CPU
            cpu_temp = cpu_temp[0].current if cpu_temp is not None else None
            gpu_temp = None
            if GPU_AVAILABLE:
                gpu_temp = nvmlDeviceGetTemperature(GPU_HANDLE, 0)  # Température GPU

            gpu_util = None
            gpu_mem = None
            if GPU_AVAILABLE:
                util = nvmlDeviceGetUtilizationRates(GPU_HANDLE)
                mem = nvmlDeviceGetMemoryInfo(GPU_HANDLE)
                gpu_util = util.gpu
                gpu_mem = mem.used / 1024**2  # VRAM utilisée en MB

            log_entry = {
                "timestamp": time.time(),
                "label": self.label,
                "cpu_percent": round(cpu, 2),
                "ram_mb": round(ram, 2),
                "gpu_util": gpu_util,
                "gpu_mem_mb": gpu_mem,
                "cpu_name": self.cpu_name,
                "gpu_name": gpu_name,
                "driver_version": driver_version,
                "cpu_cores": self.total_cpu_cores,
                "cpu_threads": self.total_cpu_threads,
                "total_ram_mb": round(self.total_ram, 2),
                "total_gpu_memory_mb": total_gpu_memory if GPU_AVAILABLE else None,
                "cuda_cores": cuda_cores if GPU_AVAILABLE else None,
                "pid": os.getpid(),
                "net_sent_mb": round(net_sent, 2),  # Réseau : Octets envoyés
                "net_recv_mb": round(net_recv, 2),  # Réseau : Octets reçus
                "disk_read_mb": round(disk_read, 2),  # I/O Disque : Octets lus
                # I/O Disque : Octets écrits
                "disk_write_mb": round(disk_write, 2),
                "swap_used_mb": round(swap_used, 2),  # Swap utilisé en MB
                "swap_total_mb": round(swap_total, 2),  # Swap total en MB
                "cpu_temp_celsius": cpu_temp,  # Température du CPU en °C
                "gpu_temp_celsius": gpu_temp,  # Température du GPU en °C
            }

            logger.info(json.dumps(log_entry))
            time.sleep(self.interval)

    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self._log_usage)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        self.thread.join()
        if GPU_AVAILABLE:
            nvmlShutdown()


def resource_monitor(interval_sec=1, label="default"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with ResourceMonitor(interval_sec=interval_sec, label=label):
                return func(*args, **kwargs)

        return wrapper

    return decorator
