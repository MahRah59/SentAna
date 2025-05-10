import psutil
import threading
import time
from datetime import datetime

log_thread = None
stop_flag = False

def _log_resource_usage(logfile="resourcelog.txt", interval=1):
    def log_loop():
        global stop_flag
        with open(logfile, "a") as f:
            while not stop_flag:
                cpu = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory().percent
                f.write(f"{datetime.now().isoformat()} - CPU: {cpu}%, Memory: {memory}%\n")
                f.flush()
                time.sleep(interval)

    return threading.Thread(target=log_loop)

def start_logging(logfile="resourcelog.txt", interval=1):
    global log_thread, stop_flag
    stop_flag = False
    log_thread = _log_resource_usage(logfile, interval)
    log_thread.start()

def stop_logging():
    global stop_flag, log_thread
    stop_flag = True
    if log_thread is not None:
        log_thread.join()

